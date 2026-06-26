#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera los CSV de deflactores en data/deflactores/ desde fuentes INE verificables.
NO embebe ninguna serie como literal (INV-5): descarga de INE, deriva, escribe CSV
y SIEMPRE imprime la serie cruda con su ID de tabla para auditarla.

Dos productos (de naturaleza distinta, ver CLAUDE.md §1):
  - ipc_enlazado.csv : TRIVIAL. Índice IPC continuo 1995-2021 a partir de los dos
    ficheros del repo (269.xlsx base 1992, 76144.xlsx base actual) enlazados con el
    enlace REAL 2001->2002 (no el 3,5% a mano). El enlace se reconstruye de la serie
    enlazada del INE (tabla 24077 / IPC290751 y tabla 76134 / IPC290750).
  - cne_p31.csv : FRÁGIL. Gasto en consumo final de los hogares (P.31), CNE.
    Fuente nueva (no está en el repo). REGLA DE ORO: se baja de INE y se imprime
    cruda. Agregación anual EXACTA: nominal = SUMA de los 4T (tabla 67823);
    índice de volumen = MEDIA de los 4T (tabla 67824); SIEMPRE 'Datos no ajustados'.
    Si la descarga falla, el script PARA con error (no inventa, no interpola).
"""
import csv as csvmod
import io
import json
import math
import os
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
DEFL = os.path.join(BASE, "deflactores")
IPC_OLD = os.path.join(DEFL, "269.xlsx")      # base 1992, 1995-2001
IPC_NEW = os.path.join(DEFL, "76144.xlsx")    # base actual, 2002-2025

INE = "https://servicios.ine.es/wstempus/js/ES"
JAXI = "https://www.ine.es/jaxiT3/files/t/csv_bdsc"


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "decomp-ivan/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def read_ipc_xlsx(path):
    """Lee 269/76144: año -> índice (medias anuales). Reusa la lógica del repo."""
    import pandas as pd
    raw = pd.read_excel(path, sheet_name=0, header=None)
    out = {}
    for _, row in raw.iterrows():
        a, b = row[0], row[1]
        try:
            y = int(float(a))
        except (TypeError, ValueError):
            continue
        if 1900 < y < 2100 and pd.notna(b):
            out[y] = float(b)
    return out


# ---------------------------------------------------------------------------
# 1) Enlace REAL 2001->2002 desde la serie enlazada del INE
# ---------------------------------------------------------------------------
def linked_2002_inflation():
    """Inflación media anual 2002 reconstruida de la serie enlazada del INE.
    Índice mensual 2002 (tabla 24077 / IPC290751) + variación anual YoY 2002
    (tabla 76134 / IPC290750):  I_2001m = I_2002m / (1 + YoY_m/100).
    Devuelve (infl_2002, I2001_media, I2002_media)."""
    idx = json.loads(fetch(f"{INE}/DATOS_SERIE/IPC290751?nult=900"))
    I2002 = {d["FK_Periodo"]: d["Valor"] for d in idx["Data"] if d["Anyo"] == 2002}
    var = json.loads(fetch(f"{INE}/DATOS_TABLA/76134?date=20020101:20021201"))
    anual = next(s for s in var if s["COD"] == "IPC290750")["Data"]
    YoY = {d["FK_Periodo"]: d["Valor"] for d in anual if d["Anyo"] == 2002}
    if len(I2002) != 12 or len(YoY) != 12:
        raise SystemExit("PARA: INE no devolvió 12 meses para el enlace 2002. No se inventa.")
    I2001 = {m: I2002[m] / (1 + YoY[m] / 100.0) for m in range(1, 13)}
    m2002 = sum(I2002.values()) / 12.0
    m2001 = sum(I2001.values()) / 12.0
    return m2002 / m2001 - 1.0, m2001, m2002


# ---------------------------------------------------------------------------
# 2) CNE P.31 (frágil): nominal=Σ4T (67823), índice volumen=media4T (67824)
# ---------------------------------------------------------------------------
def cne_annual(table_id, agg):
    """Anualiza 'Gasto en consumo final de los hogares', 'Datos no ajustados',
    'Dato base'.  agg='sum' (nominal, flujo) | 'mean' (índice de volumen)."""
    data = fetch(f"{JAXI}/{table_id}.csv").decode("utf-8-sig")
    rows = list(csvmod.reader(io.StringIO(data), delimiter=";"))
    from collections import defaultdict
    q = defaultdict(dict)
    for r in rows[1:]:
        if len(r) < 10:
            continue
        niveles = [r[i].strip() for i in range(1, 7) if r[i].strip()]
        label = niveles[-1] if niveles else ""
        tipo, valoracion, periodo, total = r[0], r[7], r[8], r[9]
        if label != "Gasto en consumo final de los hogares":
            continue
        if not tipo.startswith("Datos no ajustados") or valoracion != "Dato base":
            continue
        if "T" not in periodo:
            continue
        y, _, qq = periodo.partition("T")
        v = total.strip().replace(".", "").replace(",", ".")
        if v:
            q[int(y)][int(qq)] = float(v)
    out = {}
    for y, qs in q.items():
        if len(qs) == 4:                       # solo años con los 4 trimestres
            out[y] = sum(qs.values()) if agg == "sum" else sum(qs.values()) / 4.0
    return out


def main():
    print("=== build_deflactores.py — descarga INE, sin literales embebidos ===\n")

    # --- IPC enlazado (trivial) ----------------------------------------------
    ipc_old = read_ipc_xlsx(IPC_OLD)           # base 1992: 1995-2001
    ipc_new = read_ipc_xlsx(IPC_NEW)           # base actual: 2002-2025
    infl2002, m2001, m2002 = linked_2002_inflation()
    print("IPC enlace REAL 2001->2002 (tablas INE 24077/IPC290751 + 76134/IPC290750):")
    print(f"  media anual indice 2001={m2001:.5f}  2002={m2002:.5f}  "
          f"-> inflacion 2002 = {infl2002*100:.4f}%  (vs 3,5% a mano)\n")

    # Índice continuo: ancla en base actual (2002-2021) y retropropaga 1995-2001
    # con los factores intrabase de 269 y el enlace real en 2002 (todo invariante
    # a la base salvo el cruce 2002).
    idx = {y: ipc_new[y] for y in range(2002, 2022)}
    idx[2001] = idx[2002] / (1 + infl2002)
    for y in range(2001, 1995, -1):            # 2001->2000->...->1996  da 2000..1995
        idx[y - 1] = idx[y] / (ipc_old[y] / ipc_old[y - 1])
    ipc_rows = [(y, round(idx[y], 6)) for y in range(1995, 2022)]

    # --- CNE P.31 (frágil) ---------------------------------------------------
    nominal = cne_annual(67823, "sum")         # Mn€, suma 4T
    vol_idx = cne_annual(67824, "mean")        # índice vol., media 4T
    yrs = [y for y in range(1995, 2022) if y in nominal and y in vol_idx]
    if yrs != list(range(1995, 2022)):
        raise SystemExit(f"PARA: CNE no cubre 1995-2021 completo (tengo {min(yrs)}-{max(yrs)}). No se interpola.")
    print("CNE P.31 hogares — SERIE CRUDA (tabla 67823 nominal Mn€ / 67824 idx volumen ref.2020=100):")
    print("  datos NO ajustados; nominal=suma 4T; indice volumen=media 4T")
    print("  año |    nominal |   vol_idx | dln_nom | dln_vol | dln_deflactor")
    prev = None
    for y in range(1995, 2022):
        if prev is not None:
            dn = math.log(nominal[y] / nominal[prev])
            dv = math.log(vol_idx[y] / vol_idx[prev])
            print(f"  {y} | {nominal[y]:10.0f} | {vol_idx[y]:9.4f} | {dn:+.4f} | {dv:+.4f} | {dn-dv:+.5f}")
        else:
            print(f"  {y} | {nominal[y]:10.0f} | {vol_idx[y]:9.4f} |    base |    base |     base")
        prev = y

    # --- Escritura de CSV ----------------------------------------------------
    os.makedirs(DEFL, exist_ok=True)
    ipc_path = os.path.join(DEFL, "ipc_enlazado.csv")
    with open(ipc_path, "w", newline="", encoding="utf-8") as f:
        w = csvmod.writer(f)
        w.writerow(["anio", "ipc_index"])      # índice continuo; dlnPc = log-dif
        w.writerows(ipc_rows)
    cne_path = os.path.join(DEFL, "cne_p31.csv")
    with open(cne_path, "w", newline="", encoding="utf-8") as f:
        w = csvmod.writer(f)
        w.writerow(["anio", "p31_nominal_mn_eur", "p31_vol_idx_2020"])
        for y in range(1995, 2022):
            w.writerow([y, round(nominal[y], 3), round(vol_idx[y], 6)])

    print(f"\nEscritos:\n  {ipc_path}\n  {cne_path}")


if __name__ == "__main__":
    main()
