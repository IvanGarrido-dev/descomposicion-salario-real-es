#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
decomposition.py — Núcleo PURO de la descomposición (sin I/O, sin print).

Identidad (nivel total, por HORA, exacta):
    Δln(W/Pc) = Δln(s_L) + Δln(VA_Q/H) + [Δln(P_VA) − Δln(Pc)]
con W=LAB/H, s_L=LAB/VA, VA_Q/H productividad real por hora, P_VA=VA/VA_Q, Pc=deflactor.

La productividad por hora Δln(VA_Q/H) se abre en:
  - WITHIN: 5 factores intrasectoriales (familia LP coherente con la identidad por
    hora, INV-1), media ponderada Törnqvist de las contribuciones por rama,
    RENORMALIZADA por factor y año sobre las ramas con desglose completo (INV-3).
  - RESIDUO de productividad = Δln(VA_Q/H) − Σwithin. En §2 se deja SIN abrir y se
    etiqueta como residuo honesto; en §3 (reallocation.py) se separará en
    reasignación constructiva + residuo de reconciliación. **Nunca** se llama aquí
    "reasignación sectorial" a este cajón.

INV-2: la identidad cierra por construcción; se asierta cierre < 1e-9 como guardarraíl.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from reallocation import split_residual

# claves y etiquetas de los componentes (orden de presentación)
WITHIN_FACTORS = ("comp_lab", "cap_tic", "cap_notic", "cap_intang", "ptf")
COMPONENT_LABELS = {
    "c_labshare":     "Participación del trabajo",
    "comp_lab":       "Composición laboral",
    "cap_tic":        "Capital TIC",
    "cap_notic":      "Capital no-TIC",
    "cap_intang":     "Capital intangible",
    "ptf":            "PTF (intrasectorial)",
    # apertura del antiguo 'between' en DOS canales con significado + residuo honesto:
    "reallocation":   "Reasignación (horas)",                       # a DÓNDE van las horas (OP, niveles nominales)
    "domar":          "Composición del crecimiento sectorial (Domar)",  # QUÉ ramas crecen en output (crec. ponderado por VA)
    "reconciliation": "Reconciliación (no explicado)",             # lo que ningún término nombra (debe ser ~0)
    "c_wedge":        "Cuña de precios",
}
COMPONENT_KEYS = list(COMPONENT_LABELS)
RECON_BOUND = 0.2   # p.p. acum.: |reconciliación| debe quedar por debajo (INV-4)


@dataclass(frozen=True)
class DecompositionResult:
    country: str
    deflator: str
    lp_family: str
    renorm: bool                # True = certificado (renorm INV-3); False = modo bug
    period: tuple
    annual: pd.DataFrame        # p.p., filas=años (dyears), cols=COMPONENT_KEYS + "g_real"
    accumulated: pd.Series      # p.p., suma sobre `period`, por componente (+ g_real)
    contrib_coverage: pd.Series # cobertura de contribuciones por año (INV-3)
    closure_resid: float        # residuo de cierre de identidad (INV-2), p.p.
    reconciliation_acc: float   # |reconciliación| acumulada sobre `period` (INV-4), p.p.


def _dln(s: pd.Series, y: int) -> float:
    return float(np.log(s[y] / s[y - 1]))


def _within(data, dyears, renorm: bool = True) -> pd.DataFrame:
    """within por factor (DataFrame, índice=dyears).

    renorm=True (DEFAULT, certificado): pesos renormalizados POR FACTOR Y AÑO sobre
        las ramas con desglose completo (INV-3); las horas sin desglose se
        redistribuyen al within. Es un SUPUESTO (imputa las ramas sin dato a la
        media), no una corrección neutra; su sesgo va hacia lo negativo en la PTF
        (las ramas sin desglose —química, farma, electrónica— son de PTF alta).
    renorm=False (modo BUG, solo pedagogía): pesos sin renormalizar; las
        contribuciones NaN se tratan como 0 y su peso en horas cae al residuo.
        Reproduce el sesgo del proyecto viejo (ptf −10,09, residuo inflado +0,46).
        NO es una cifra alternativa legítima; existe para poder mostrar la
        diferencia en el writeup."""
    out = {k: [] for k in WITHIN_FACTORS}
    for y in dyears:
        s0 = data.hours_ind[y - 1] / data.hours[y - 1]
        s1 = data.hours_ind[y] / data.hours[y]
        wbar = (s0 + s1) / 2.0                      # pesos Törnqvist (cuotas de horas)
        for k in WITHIN_FACTORS:
            contr = (data.contrib[k][y] / 100.0).fillna(0.0)
            if renorm:
                valid = data.coverage_mask[k][y]    # bool por rama (INV-3, por factor/año)
                wuse = wbar.where(valid, 0.0)
                wuse = wuse / wuse.sum()             # renorm SOLO sobre ramas con dato
            else:
                wuse = wbar                          # modo bug: NaN -> residuo
            out[k].append(float((wuse * contr).sum()))
    return pd.DataFrame(out, index=list(dyears))


def decompose(data, *, deflator: str = "cne_p31",
              productivity: str = "per_hour",
              renorm: bool = True,
              period: tuple = (1996, 2019)) -> DecompositionResult:
    """Descompone el salario real por hora. Función pura: no lee ficheros ni imprime.

    renorm=True por defecto = modo certificado (renorm INV-3). renorm=False es el
    modo bug, solo para mostrar la diferencia en el writeup (ver _within)."""
    if productivity != "per_hour":
        raise NotImplementedError("v1 sólo certifica productivity='per_hour' (DESIGN §3.1).")
    if deflator not in data.deflators:
        raise KeyError(f"deflactor '{deflator}' no disponible; hay {list(data.deflators)}.")

    dyears = data.dyears
    lab, va, vaq, h = data.lab, data.va, data.vaq, data.hours
    dlnPc = data.deflators[deflator]

    # componentes macro (no dependen de la familia)
    c_labshare = pd.Series({y: _dln(lab / va, y) for y in dyears})
    c_prod     = pd.Series({y: _dln(vaq / h, y) for y in dyears})
    c_pva      = pd.Series({y: _dln(va / vaq, y) for y in dyears})
    c_wedge    = c_pva - dlnPc
    g_real     = pd.Series({y: _dln(lab / h, y) for y in dyears}) - dlnPc

    # within (LP coherente, renorm INV-3) + apertura del residuo de productividad
    # en DOS canales con significado (reasignación de horas + Domar) + reconciliación.
    within = _within(data, dyears, renorm=renorm)
    prod_resid = c_prod - within.sum(axis=1)
    split = split_residual(data, prod_resid, dyears)   # reallocation, domar, reconciliation

    cols = {"c_labshare": c_labshare}
    cols.update({k: within[k] for k in WITHIN_FACTORS})
    cols["reallocation"] = split["reallocation"]
    cols["domar"] = split["domar"]
    cols["reconciliation"] = split["reconciliation"]
    cols["c_wedge"] = c_wedge
    annual = pd.DataFrame(cols) * 100.0            # a puntos porcentuales
    annual["g_real"] = g_real * 100.0
    annual.index.name = "anio"

    # INV-2: cierre de identidad (guardarraíl, 1e-9)
    closure = float((annual[COMPONENT_KEYS].sum(axis=1) - annual["g_real"]).abs().max())
    if closure >= 1e-9:
        raise AssertionError(f"INV-2 violado: residuo de cierre {closure:.2e} p.p. >= 1e-9.")

    y0, y1 = period
    accumulated = annual.loc[y0:y1, COMPONENT_KEYS + ["g_real"]].sum()

    # INV-4: en el modo CERTIFICADO (renorm) la reconciliación acumulada debe quedar
    # acotada. Si se dispara, alguien rompió un término (within/reasignación/Domar).
    # En el modo bug (renorm=False) la reconciliación es legítimamente mayor: ahí es
    # donde aflora el sesgo de las horas sin desglose volcadas, así que NO se exige.
    recon_acc = float(annual.loc[y0:y1, "reconciliation"].sum())
    if renorm and abs(recon_acc) >= RECON_BOUND:
        raise AssertionError(
            f"INV-4 violado: |reconciliación| acumulada {recon_acc:+.3f} p.p. "
            f">= {RECON_BOUND}. La reasignación+Domar no están capturando el residuo.")

    return DecompositionResult(
        country=data.country, deflator=deflator, lp_family=data.lp_family,
        renorm=renorm, period=period, annual=annual, accumulated=accumulated,
        contrib_coverage=data.contrib_coverage.loc[y0:y1], closure_resid=closure,
        reconciliation_acc=recon_acc)
