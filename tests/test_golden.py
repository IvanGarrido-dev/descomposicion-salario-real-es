"""INV-5 — el golden es el CONTRATO: ES, modo por defecto, byte a byte.

Cualquier cambio de número no intencionado rompe este test. El golden congela el
único modo certificado (cne_p31, renorm INV-3, per_hour). El modo bug (renorm=False)
NO se certifica: existe solo para pedagogía del writeup.
"""
from conftest import GOLDEN


def test_golden_default_matches(es):
    from decomposition import decompose, COMPONENT_KEYS
    r = decompose(es, deflator="cne_p31", renorm=True, period=(1996, 2019))
    recomputed = r.annual[COMPONENT_KEYS + ["g_real"]].to_csv(float_format="%.8f")
    with open(GOLDEN, "r", encoding="utf-8", newline="") as f:
        frozen = f.read()
    # normaliza fin de línea para no depender del SO
    assert recomputed.replace("\r\n", "\n") == frozen.replace("\r\n", "\n")
