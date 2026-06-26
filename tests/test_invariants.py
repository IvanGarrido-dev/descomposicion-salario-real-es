"""INV-1..INV-4 — la red que hace reales las invariantes del DESIGN §2/§8."""
import os

import numpy as np
import pytest

from conftest import DATA_DIR

NEVER_COVERED = {"C20", "C21", "C26", "C27", "T", "U"}
PARTIAL = ["C19"]


# --- INV-1: familia LP coherente con la identidad por hora (recomputada) -----
def test_inv1_autoselects_per_hour_family(es):
    assert es.lp_family == "LP1"


def test_inv1_certifies_against_recomputed_not_label(es):
    """La familia elegida casa con Δln(VA_Q/H) RECOMPUTADO; la otra diverge ~7 p.p."""
    import numpy as np
    from data_loading import load_sheet
    GA = os.path.join(DATA_DIR, "euklems_2024", "ES_growth accounts.xlsx")
    g_hour = {y: 100.0 * (np.log(es.vaq[y] / es.vaq[y - 1]) - np.log(es.hours[y] / es.hours[y - 1]))
              for y in es.dyears}
    errs = {fam: max(abs(load_sheet(GA, f"{fam}_G").loc["TOT"][y] - g_hour[y]) for y in es.dyears)
            for fam in ("LP1", "LP2")}
    assert errs["LP1"] < 1e-3                 # match al nivel de redondeo de la hoja
    assert errs["LP2"] > 1.0                  # separación dominante (en ES ~7 p.p.)
    assert errs["LP2"] > errs["LP1"] * 1e3


def test_inv1_raises_if_no_family_matches(es):
    """Si se rompe la coherencia, el selector DEBE fallar, no elegir. Se perturba
    VA_Q con una tendencia anual (un factor constante se cancelaría en Δln)."""
    import pandas as pd
    from data_loading import select_lp_family
    GA = os.path.join(DATA_DIR, "euklems_2024", "ES_growth accounts.xlsx")
    trend = pd.Series({y: 1.02 ** i for i, y in enumerate(es.vaq.index)})
    bad_vaq = es.vaq * trend                  # mete ~2 p.p./año en Δln(VA_Q/H): no casa ninguna
    with pytest.raises(AssertionError):
        select_lp_family(GA, bad_vaq, es.hours, es.dyears)


# --- INV-2: cierre de identidad < 1e-9 en todos los modos --------------------
@pytest.mark.parametrize("deflator", ["cne_p31", "ipc"])
@pytest.mark.parametrize("renorm", [True, False])
def test_inv2_identity_closes(es, deflator, renorm):
    from decomposition import decompose
    r = decompose(es, deflator=deflator, renorm=renorm, period=(1996, 2019))
    assert r.closure_resid < 1e-9


# --- INV-3: cobertura, distinguiendo horas (100%) de contribuciones (~95,8%) --
def test_inv3_hours_coverage_is_total(es):
    assert np.allclose(es.hours_coverage.values, 1.0, atol=1e-9)


def test_inv3_contribution_coverage_known(es):
    assert abs(es.contrib_coverage.mean() - 0.958) < 2e-3      # ~4,2% no cubierto
    assert set(es.never_covered) == NEVER_COVERED
    assert es.partial_covered == PARTIAL
    assert len(es.covered_full) == 33 - len(NEVER_COVERED) - len(PARTIAL)  # 26


# --- INV-4: within + reasignación(OP) + Domar + reconciliación = c_prod -------
def test_inv4_productivity_fully_decomposed(es, result_default):
    """Los cuatro canales reconstruyen la productividad agregada por hora, exacto."""
    a = result_default.annual
    parts = a[["comp_lab", "cap_tic", "cap_notic", "cap_intang", "ptf",
               "reallocation", "domar", "reconciliation"]].sum(axis=1)
    c_prod = {y: 100.0 * (np.log(es.vaq[y] / es.vaq[y - 1]) - np.log(es.hours[y] / es.hours[y - 1]))
              for y in es.dyears}
    assert (parts - [c_prod[y] for y in a.index]).abs().max() < 1e-9


def test_inv4_reconciliation_bounded(es, result_default):
    """El 'no explicado' acumulado debe ser pequeño: reasignación+Domar SÍ capturan
    el residuo. Si un cambio futuro lo dispara, rompió un término."""
    from decomposition import RECON_BOUND
    assert abs(result_default.reconciliation_acc) < RECON_BOUND
    assert abs(result_default.reconciliation_acc + 0.068) < 5e-3   # valor conocido ES


def test_inv4_between_opens_into_two_meaningful_channels(es, result_default):
    """La reasignación de horas (OP) es pequeña; el grueso del viejo 'between' es
    Domar (composición del crecimiento), no trasvase de horas."""
    a = result_default.accumulated
    assert abs(a["reallocation"] - 0.639) < 5e-3    # a DÓNDE van las horas (pequeño)
    assert abs(a["domar"] - 2.550) < 5e-3           # QUÉ ramas crecen en output (grueso)
    assert a["domar"] > a["reallocation"] * 3       # el Domar domina


# --- Termómetro PTF: régimen LP1 (≈ -10), no LP2 (≈ -12,3) --------------------
def test_ptf_thermometer(es):
    from decomposition import decompose
    cert = decompose(es, deflator="cne_p31", renorm=True, period=(1996, 2019))
    bug = decompose(es, deflator="cne_p31", renorm=False, period=(1996, 2019))
    assert abs(cert.accumulated["ptf"] - (-10.572)) < 5e-3     # certificado
    assert abs(bug.accumulated["ptf"] - (-10.090)) < 5e-3      # modo bug (writeup)
    # acoplamiento: OP y Domar NO dependen de renorm (salen de va_ind/vaq_ind), así
    # que el delta del within TOTAL compensa exacto al de la reconciliación.
    within_keys = ["comp_lab", "cap_tic", "cap_notic", "cap_intang", "ptf"]
    d_within = sum(bug.accumulated[k] - cert.accumulated[k] for k in within_keys)
    d_recon = bug.accumulated["reconciliation"] - cert.accumulated["reconciliation"]
    assert abs(d_within + d_recon) < 1e-6
    assert abs(bug.accumulated["reallocation"] - cert.accumulated["reallocation"]) < 1e-9   # OP invariante
    assert abs(bug.accumulated["domar"] - cert.accumulated["domar"]) < 1e-9                 # Domar invariante
    # el modo bug afloja la PTF (menos negativa) e infla la reconciliación en paralelo
    assert bug.accumulated["ptf"] > cert.accumulated["ptf"] and d_recon > 0
