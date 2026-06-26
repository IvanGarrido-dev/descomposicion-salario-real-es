#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reallocation.py — Término de reasignación CONSTRUCTIVO (DESIGN §4). Función pura.

El cajón-residuo del proyecto viejo ("between = agregado − Σwithin") mezclaba
reasignación real + cuña horas/persona + NaN + error de reconciliación, y se
etiquetaba "reasignación sectorial". Aquí la reasignación se CONSTRUYE y el
residuo de reconciliación se reporta aparte, sin renombrar.

⚠ REGLA INNEGOCIABLE (el error de encadenamiento): los VA_Q son volúmenes
ENCADENADOS; sus NIVELES no son aditivos ni comparables entre ramas. La
reasignación se construye SOLO con niveles NOMINALES (VAB corriente por hora, en
euros, sí comparables entre ramas). Aquí NO entra ningún VA_Q: solo va_ind
(nominal) y hours_ind. Si algún día ves un VA_Q de dos ramas restándose o en una
covarianza, es el bug de encadenamiento.

    reasignación_t = Σ_i Δs_it · ln( y_it / ȳ_t )

con s_it = cuota de horas de la rama i, y_it = VAB nominal por hora de la rama i,
ȳ_t = VAB nominal por hora agregado. Capta el movimiento de horas hacia/desde
ramas de mayor/menor productividad NOMINAL relativa (Olley-Pakes estático).

Cobertura: y_it = va_ind/hours_ind requiere VAB NOMINAL por rama. En ES, 6 ramas
(C20, C21, C26, C27, T, U) tienen horas pero NO desglose de VA_CP (y U además 0
horas), igual que les falta el desglose de contribuciones. Así que la reasignación
se construye sobre las ramas CUBIERTAS (VAB nominal finito y horas>0), con cuotas
RENORMALIZADAS dentro de lo cubierto — coherente con la renorm del within (INV-3).
Detalle limpio: como Σ Δs_i (cuotas que suman 1) = 0, la elección de ȳ es
irrelevante al valor del término; se deja ȳ = media cubierta por interpretabilidad.
Lo que las 6 ramas hacen al moverse cae, honestamente, al residuo de reconciliación.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _covered_year(data, y) -> list:
    """Ramas decomponibles en el año y: VAB nominal y VA_Q POSITIVOS y horas>0 en y
    y en y-1 (positivos porque se toma ln; el VAB/VA_Q de una rama puede ser negativo,
    p. ej. C19 refino en 2020, y ahí no es decomponible por este método). La cobertura
    es POR AÑO, igual que el within. Misma cobertura para OP y Domar -> consistencia."""
    ok = ((data.va_ind[y] > 0) & (data.va_ind[y - 1] > 0)
          & (data.vaq_ind[y] > 0) & (data.vaq_ind[y - 1] > 0)
          & (data.hours_ind[y] > 0) & (data.hours_ind[y - 1] > 0))
    return ok[ok].index.tolist()


def reallocation(data, dyears, return_coverage: bool = False):
    """Σ_i Δs_it · ln(y_it/ȳ_t) por año (fracción), Olley-Pakes estático sobre
    NIVELES NOMINALES, restringido a las ramas cubiertas ESE año, con cuotas
    renormalizadas dentro de lo cubierto. Si return_coverage, devuelve también las
    ramas excluidas por año (transparencia, no se silencia)."""
    out, dropped = [], {}
    allb = set(data.branches)
    for y in dyears:
        cov = _covered_year(data, y)
        dropped[y] = sorted(allb - set(cov))
        h1 = data.hours_ind.loc[cov, y]
        h0 = data.hours_ind.loc[cov, y - 1]
        s1 = h1 / h1.sum()                             # cuotas DENTRO de lo cubierto
        s0 = h0 / h0.sum()
        ds = s1 - s0                                   # Σ ds = 0 por construcción
        y_i = data.va_ind.loc[cov, y] / h1             # VAB NOMINAL por hora (€), comparable
        ybar = data.va_ind.loc[cov, y].sum() / h1.sum()
        rel = np.log(y_i / ybar)
        if not np.isfinite(rel).all():
            bad = rel.index[~np.isfinite(rel)].tolist()
            raise ValueError(f"reasignación {y}: log no finito en ramas {bad} "
                             f"(VAB nominal <=0 inesperado). No se silencia.")
        out.append(float((ds * rel).sum()))
    s = pd.Series(out, index=list(dyears))
    return (s, dropped) if return_coverage else s


def domar(data, dyears) -> pd.Series:
    """Componente Domar: Σ_i (v_it − w_it)·Δln(VAQ_it) por año (fracción).

    v_i = cuota de VA NOMINAL, w_i = cuota de HORAS, Δln(VAQ_i) = crecimiento real
    del output de la rama. Capta que el output crece de forma DESIGUAL por rama: las
    ramas con cuota de VA mayor que su cuota de horas (alta productividad) creciendo
    más en output empujan la productividad agregada por encima de la media ponderada
    por horas del within. Es el segundo canal de cambio estructural, distinto de la
    reasignación de horas (OP).

    ⚠ Usa Δln(VAQ_i): CRECIMIENTOS de volumen encadenado (válidos), NUNCA niveles de
    VA_Q entre ramas. Cuotas medias de t-1 y t. Cobertura por año (igual que OP)."""
    out = []
    for y in dyears:
        cov = _covered_year(data, y)
        v = ((data.va_ind.loc[cov, y] / data.va[y]
              + data.va_ind.loc[cov, y - 1] / data.va[y - 1]) / 2.0)      # cuota VA nominal
        w = ((data.hours_ind.loc[cov, y] / data.hours[y]
              + data.hours_ind.loc[cov, y - 1] / data.hours[y - 1]) / 2.0)  # cuota horas
        dlnvaq = np.log(data.vaq_ind.loc[cov, y] / data.vaq_ind.loc[cov, y - 1])
        out.append(float(((v - w) * dlnvaq).sum()))
    return pd.Series(out, index=list(dyears))


def split_residual(data, prod_resid: pd.Series, dyears) -> pd.DataFrame:
    """Abre el residuo de productividad en DOS términos con significado + el 'no
    explicado' honesto:

        prod_resid = reasignación_horas (OP) + domar + reconciliación

    - reasignación_horas (OP, niveles nominales): a DÓNDE van las horas.
    - domar (crecimientos reales, pesos VA): QUÉ ramas crecen en output.
    - reconciliación = prod_resid − OP − domar: lo que ninguno de los dos nombra.
      Debe ser pequeño (en ES ~ −0,07 p.p. acum.); si se dispara, alguien rompió
      un término. NO se renombra ni se absorbe: se reporta visible (INV-4)."""
    op = reallocation(data, dyears)
    dm = domar(data, dyears)
    return pd.DataFrame({
        "reallocation": op,
        "domar": dm,
        "reconciliation": prod_resid - op - dm,
    })
