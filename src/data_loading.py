#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data_loading.py — Carga de datos por país y GATE de cobertura (INV-3).

Hace I/O (lee xlsx/csv); `decompose` no. Entrega un `CountryData` inmutable que
ya trae:
  - los agregados y las contribuciones por rama de la familia LP **coherente con
    la identidad por hora** (INV-1: autoseleccionada, no hardcodeada);
  - la **máscara de cobertura expuesta** (factor x rama x año), distinguiendo
    cobertura EN HORAS (=100%) de cobertura DE CONTRIBUCIONES (~95,8% en ES);
  - las series de deflactor (ipc, cne_p31) como Δln Pc anual.

Decisiones de diseño ancladas (ver DESIGN.md / CLAUDE.md):
  * INV-1: se selecciona la familia cuyo `LP*_G` (TOT) ≡ 100·Δln(VA_Q/H). A plena
    precisión la coincidente casa a ~4e-7 p.p. y la otra diverge ~7 p.p.; LLEE
    publica `LP*_G` redondeado, por eso la tolerancia operativa es 1e-4 p.p.
    (más laxa que el 1e-9 del DESIGN, que asumía precisión infinita).
  * INV-3: la cobertura se evalúa POR FACTOR Y AÑO. No se renormaliza aquí (eso es
    de `decompose`); aquí se EXPONE la máscara para que la renormalización del
    within se haga por-factor-y-año y nunca global (C19 es parcial: PTF hasta 2019).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

# Partición MECE de 33 ramas (EUKLEMS). v1 = ES; v2 la generalizará por país.
PART_MANUF = ["C10-C12", "C13-C15", "C16-C18", "C19", "C20", "C21",
              "C22-C23", "C24-C25", "C26", "C27", "C28", "C29-C30", "C31-C33"]
PART_SECT = ["A", "B", "D", "E", "F", "G", "H", "I", "J", "K", "L",
             "M", "N", "O", "P", "Q", "R", "S", "T", "U"]
PART = PART_MANUF + PART_SECT

# factor -> sufijo de hoja de contribución (común a las familias LP1/LP2)
FACTOR_SUFFIX = {
    "comp_lab":   "ConLC",
    "cap_tic":    "ConTangICT",
    "cap_notic":  "ConTangNICT",
    "cap_intang": "ConIntang",
    "ptf":        "ConTFP",
}
FACTORS = tuple(FACTOR_SUFFIX)

# INV-1 se certifica contra la productividad por hora RECOMPUTADA (Δln(VA_Q/H)),
# no contra la etiqueta LP*_G de LLEE. Matiz de precisión: TODAS las celdas de la
# hoja LLEE vienen redondeadas (~6 cifras), así que el match alcanzable contra el
# dato recomputado desde VA_Q y H es ~5e-7 p.p., no 1e-9 (el 1e-9 estricto solo
# vive en cantidades recomputadas de extremo a extremo: el cierre de identidad,
# INV-2). La SELECCIÓN no depende de ese umbral fino: la separación entre familias
# es ~7 p.p. (1e7×), así que la familia coherente es inequívoca.
LP_MATCH_TOL  = 1e-3    # p.p.: sanity de que la familia elegida casa con g_hour recomputado
LP_SEPARATION = 1e3     # la otra familia debe errar >=1000x más (en ES, ~1e7x)


# ---------------------------------------------------------------------------
# Utilidades de carga
# ---------------------------------------------------------------------------
def load_sheet(path: str, sheet: str) -> pd.DataFrame:
    """DataFrame indexado por código NACE, columnas = años (int)."""
    df = pd.read_excel(path, sheet_name=sheet).set_index("nace_r2_code")
    yrs = [c for c in df.columns if str(c).strip().isdigit()]
    out = df[yrs].apply(pd.to_numeric, errors="coerce")
    out.columns = [int(c) for c in out.columns]
    return out


def _dln(s: pd.Series, y: int) -> float:
    return float(np.log(s[y] / s[y - 1]))


# ---------------------------------------------------------------------------
# INV-1: selección de familia LP coherente con la identidad por hora
# ---------------------------------------------------------------------------
def select_lp_family(growth_path: str, vaq: pd.Series, hours: pd.Series,
                     dyears: list[int], match_tol: float = LP_MATCH_TOL,
                     separation: float = LP_SEPARATION) -> str:
    """Selecciona la familia ("LP1"/"LP2") cuya productividad coincide con la
    productividad por hora RECOMPUTADA de la identidad, 100·Δln(VA_Q/H).

    Certifica INV-1 por dos vías, no por un umbral mágico:
      (a) la familia elegida casa con g_hour recomputado a nivel de redondeo de
          la hoja LLEE (< match_tol);
      (b) la otra familia yerra >= separation× más (en ES ~1e7×): elección inequívoca.
    Compara contra g_hour (recomputado de VA_Q y H), NO contra la etiqueta LP*_G."""
    g_hour = pd.Series({y: 100.0 * (_dln(vaq, y) - _dln(hours, y)) for y in dyears})
    errs = {fam: float(max(abs(load_sheet(growth_path, f"{fam}_G").loc["TOT"][y] - g_hour[y])
                           for y in dyears))
            for fam in ("LP1", "LP2")}
    best = min(errs, key=errs.get)
    second = min(e for f, e in errs.items() if f != best)
    if errs[best] >= match_tol:
        raise AssertionError(
            f"INV-1: ninguna familia casa con la productividad por hora recomputada "
            f"(mejor err={errs[best]:.2e} p.p. >= {match_tol}). Errores={errs}.")
    if second < errs[best] * separation:
        raise AssertionError(
            f"INV-1: separación insuficiente entre familias (mejor={errs[best]:.2e}, "
            f"segunda={second:.2e}). La elección sería ambigua. Errores={errs}.")
    return best


# ---------------------------------------------------------------------------
# Deflactores -> Δln Pc anual
# ---------------------------------------------------------------------------
def load_deflators(defl_dir: str, dyears: list[int]) -> dict[str, pd.Series]:
    """Lee data/deflactores/*.csv y devuelve {nombre: Δln Pc} (índice = dyears)."""
    ipc = pd.read_csv(os.path.join(defl_dir, "ipc_enlazado.csv")).set_index("anio")["ipc_index"]
    cne = pd.read_csv(os.path.join(defl_dir, "cne_p31.csv")).set_index("anio")
    nom, vol = cne["p31_nominal_mn_eur"], cne["p31_vol_idx_2020"]
    out = {
        "ipc": pd.Series({y: float(np.log(ipc[y] / ipc[y - 1])) for y in dyears}),
        "cne_p31": pd.Series({y: float(np.log(nom[y] / nom[y - 1]) - np.log(vol[y] / vol[y - 1]))
                              for y in dyears}),
    }
    return out


# ---------------------------------------------------------------------------
# CountryData
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CountryData:
    country: str
    years: list
    dyears: list
    branches: list
    factors: tuple
    lp_family: str
    # agregados TOT (Series por año)
    lab: pd.Series           # compensación laboral nominal (LAB)
    va: pd.Series            # VA precios corrientes (VA_CP)
    vaq: pd.Series           # VA volumen encadenado (VA_Q)
    hours: pd.Series         # horas trabajadas (H_EMP)
    emp: pd.Series           # ocupados (EMP)  [diagnóstico / INV-1]
    # por rama
    hours_ind: pd.DataFrame  # H_EMP por rama (filas=rama, cols=años)
    va_ind: pd.DataFrame     # VA_CP por rama (NOMINAL, comparable entre ramas) -> §3 reasignación OP
    vaq_ind: pd.DataFrame    # VA_Q por rama (volumen encadenado; SOLO crecimientos) -> §3 Domar
    contrib: dict            # factor -> DataFrame contribuciones por rama (p.p.), familia auto
    # cobertura (INV-3) EXPUESTA
    coverage_mask: dict      # factor -> DataFrame bool (rama×año, True = dato válido)
    covered_full: list       # desglose completo TODOS los años
    never_covered: list      # sin desglose en NINGÚN año
    partial_covered: list    # desglose parcial
    hours_coverage: pd.Series     # cobertura EN HORAS por año (=1.0)
    contrib_coverage: pd.Series   # cobertura DE CONTRIBUCIONES por año (~0.958)
    # deflactores
    deflators: dict          # nombre -> Δln Pc anual

    # --- helpers de cobertura (INV-3), para que decompose no recalcule a escondidas
    def covered_year_mask(self, factor: str) -> pd.DataFrame:
        """bool rama×año: True si la contribución de ese factor existe ese año."""
        return self.coverage_mask[factor]


def load_country(country: str, data_dir: str, *,
                 years=range(1995, 2022), dyears=range(1996, 2022),
                 branches=PART, force_family: str = None) -> CountryData:
    """Carga un país desde data_dir (euklems_2024/ + deflactores/).

    force_family: SOLO para diagnóstico/ilustración (p. ej. enseñar la PTF
        incoherente de LP2 en el termómetro). Salta la autoselección INV-1. NO se
        usa en el modo certificado. Si None, se autoselecciona (lo normal)."""
    years, dyears, branches = list(years), list(dyears), list(branches)
    euk = os.path.join(data_dir, "euklems_2024")
    GA = os.path.join(euk, f"{country}_growth accounts.xlsx")
    NA = os.path.join(euk, f"{country}_national accounts.xlsx")

    VA = load_sheet(GA, "VA_CP")
    VAQ = load_sheet(GA, "VA_Q")
    lab = load_sheet(GA, "LAB").loc["TOT"]
    va = VA.loc["TOT"]
    vaq = VAQ.loc["TOT"]
    H = load_sheet(NA, "H_EMP")
    hours = H.loc["TOT"]
    emp = load_sheet(NA, "EMP").loc["TOT"]
    hours_ind = H.loc[branches]
    va_ind = VA.loc[branches]            # VAB NOMINAL por rama (niveles € comparables, §3 OP)
    vaq_ind = VAQ.loc[branches]          # VA_Q por rama (encadenado; SOLO crecimientos, §3 Domar)

    # INV-1: familia coherente con la identidad por hora (force_family solo diagnóstico)
    lp_family = force_family if force_family else select_lp_family(GA, vaq, hours, dyears)
    contrib = {k: load_sheet(GA, f"{lp_family}{suf}").loc[branches]
               for k, suf in FACTOR_SUFFIX.items()}

    # INV-3: máscara de cobertura POR FACTOR Y AÑO (True = dato válido)
    coverage_mask = {k: contrib[k].loc[:, dyears].notna() for k in FACTORS}
    # unión: una rama tiene algún factor sin dato ese año
    any_nan = coverage_mask[FACTORS[0]].copy()
    for k in FACTORS:
        any_nan = any_nan & coverage_mask[k]   # AND de validez -> rama válida si todos sus factores
    valid_all = any_nan                        # bool rama×año: True si TODOS los factores válidos
    ever_invalid = ~valid_all.all(axis=1)      # algún año inválido
    always_invalid = (~valid_all).all(axis=1)  # inválido todos los años
    covered_full = valid_all.all(axis=1)
    covered_full = covered_full[covered_full].index.tolist()
    never_covered = always_invalid[always_invalid].index.tolist()
    partial_covered = [b for b in branches if ever_invalid[b] and not always_invalid[b]]

    # Dos coberturas DISTINTAS (INV-3):
    #   - en HORAS: las 33 ramas son partición MECE -> 100% siempre
    #   - de CONTRIBUCIONES: cuota de horas de las ramas con TODOS los factores ese año
    hours_coverage = pd.Series({y: float(hours_ind[y].sum() / hours[y]) for y in dyears})
    contrib_coverage = pd.Series({
        y: float(hours_ind.loc[valid_all[y][valid_all[y]].index, y].sum() / hours[y])
        for y in dyears})

    deflators = load_deflators(os.path.join(data_dir, "deflactores"), dyears)

    return CountryData(
        country=country, years=years, dyears=dyears, branches=branches,
        factors=FACTORS, lp_family=lp_family,
        lab=lab, va=va, vaq=vaq, hours=hours, emp=emp,
        hours_ind=hours_ind, va_ind=va_ind, vaq_ind=vaq_ind, contrib=contrib,
        coverage_mask=coverage_mask, covered_full=covered_full,
        never_covered=never_covered, partial_covered=partial_covered,
        hours_coverage=hours_coverage, contrib_coverage=contrib_coverage,
        deflators=deflators)


if __name__ == "__main__":   # smoke test del gate (no se importa)
    here = os.path.dirname(os.path.abspath(__file__))
    cd = load_country("ES", os.path.join(here, "..", "data"))
    print(f"país={cd.country}  familia LP autoseleccionada (INV-1) = {cd.lp_family}")
    print(f"ramas={len(cd.branches)}  factores={cd.factors}")
    print(f"[INV-3] cobertura EN HORAS:        media={cd.hours_coverage.mean():.4f} "
          f"(min={cd.hours_coverage.min():.4f})")
    print(f"[INV-3] cobertura DE CONTRIBUCIONES: media={cd.contrib_coverage.mean():.4f} "
          f"(min={cd.contrib_coverage.min():.4f}, año min={cd.contrib_coverage.idxmin()})")
    print(f"  desglose completo: {len(cd.covered_full)} ramas")
    print(f"  sin desglose ningún año: {cd.never_covered}")
    print(f"  desglose parcial:        {cd.partial_covered}")
    for name, dpc in cd.deflators.items():
        print(f"  deflactor '{name}': dln Pc acum. 1996-2019 = "
              f"{dpc.loc[1996:2019].sum()*100:.3f} p.p.")
