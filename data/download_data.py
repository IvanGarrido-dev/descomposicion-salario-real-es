#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_data.py — Trazabilidad ejecutable de los inputs (INV-5).

NO es la vía normal de reproducción. Los datos de España van COMMITEADOS en el
repo (son pequeños), así que **clonar + correr funciona sin ejecutar esto**. Este
script sirve para:
  1. VERIFICAR que los inputs presentes coinciden con los MD5 de SOURCES.md
     (parsea SOURCES.md como única fuente de verdad). Aborta (exit 1) si algo no
     cuadra: un fichero con MD5 distinto NO es el certificado.
  2. REGENERAR los CSV de deflactores desde INE  (--regenerate-csv -> build_deflactores.py).
  3. DOCUMENTAR de dónde se baja cada xlsx externo para actualizar a una release
     nueva.

HONESTIDAD DE URLS (importante): NO se inventan enlaces directos. Para EUKLEMS y
para los IPC xlsx no hay una URL directa que reproduzca byte a byte el export
concreto que usamos (la página de EUKLEMS es un portal con formulario; los xlsx de
INE que tenemos son exports filtrados). Por eso se documenta la PÁGINA OFICIAL y se
marca descarga MANUAL (ver kind='manual'). Si bajas el fichero y su MD5 no coincide
con SOURCES.md, no es el certificado: investígalo, no lo fuerces.

Uso:
    python data/download_data.py                 # verifica MD5 de lo presente
    python data/download_data.py --regenerate-csv # regenera ipc_enlazado.csv y cne_p31.csv
    python data/download_data.py --where          # imprime de dónde sale cada input
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))      # .../data
ROOT = os.path.dirname(BASE)
SOURCES_MD = os.path.join(ROOT, "SOURCES.md")

EUKLEMS_PORTAL = "https://euklems-intanprod-llee.luiss.it/download/"   # release 2024
INE_TABLA = "https://www.ine.es/jaxiT3/Tabla.htm?t={}"

# ruta relativa a data/  ->  (descripción de la fuente oficial, modo)
#   manual    : se descarga a mano desde la página oficial (no hay URL directa verificable)
#   generated : lo produce build_deflactores.py descargando de INE (sí reproducible)
REGISTRY = {
    "euklems_2024/ES_growth accounts.xlsx":   (f"EUKLEMS & INTANProd 2024 (LLEE), España. Portal: {EUKLEMS_PORTAL}", "manual"),
    "euklems_2024/ES_national accounts.xlsx": (f"EUKLEMS & INTANProd 2024 (LLEE), España. Portal: {EUKLEMS_PORTAL}", "manual"),
    "euklems_2024/ES_labour accounts.xlsx":   (f"EUKLEMS & INTANProd 2024 (LLEE), España. Portal: {EUKLEMS_PORTAL}", "manual"),
    "euklems_2024/ES_capital accounts.xlsx":  (f"EUKLEMS & INTANProd 2024 (LLEE), España. Portal: {EUKLEMS_PORTAL}", "manual"),
    "deflactores/269.xlsx":   ("INE, IPC base 1992, medias anuales 1995-2001 — tabla 269 (sistema jaxi antiguo). "
                               "TODO: sin URL directa verificada; descarga manual desde INEbase (IPC, cambios de base).", "manual"),
    "deflactores/76144.xlsx": (f"INE, IPC ver.2 base actual — tabla 76144. Página: {INE_TABLA.format(76144)} "
                               "(exportar a XLSX; el export puede no reproducir byte a byte el fichero certificado).", "manual"),
    "deflactores/ipc_enlazado.csv": ("Generado por data/build_deflactores.py (descarga INE: tablas 24077/76134 + IPC xlsx).", "generated"),
    "deflactores/cne_p31.csv":      ("Generado por data/build_deflactores.py (descarga INE: tablas 67823/67824).", "generated"),
}


def parse_sources_md5(path=SOURCES_MD):
    """Extrae {nombre_fichero: md5} de las tablas markdown de SOURCES.md."""
    out = {}
    name_re = re.compile(r"([\w .()\-]+?\.(?:xlsx|csv))")
    md5_re = re.compile(r"\b([0-9a-fA-F]{32})\b")
    with open(path, encoding="utf-8") as f:
        for line in f:
            m5 = md5_re.search(line)
            if not m5:
                continue
            nm = name_re.search(line)
            if nm:
                out[nm.group(1).strip()] = m5.group(1).lower()
    return out


def md5_of(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def verify(expected):
    """Devuelve (ok, mismatch, missing) como listas de rutas relativas a data/."""
    ok, mismatch, missing = [], [], []
    for rel in REGISTRY:
        path = os.path.join(BASE, *rel.split("/"))
        base = os.path.basename(rel)
        exp = expected.get(base)
        if not os.path.exists(path):
            missing.append(rel)
        elif exp is None:
            mismatch.append((rel, "sin MD5 en SOURCES.md"))
        elif md5_of(path) != exp:
            mismatch.append((rel, f"MD5 {md5_of(path)[:8]}… != {exp[:8]}… (SOURCES.md)"))
        else:
            ok.append(rel)
    return ok, mismatch, missing


def regenerate_csv():
    print(">> Regenerando CSV de deflactores con build_deflactores.py (descarga INE)…")
    return subprocess.call([sys.executable, os.path.join(BASE, "build_deflactores.py")])


def main():
    ap = argparse.ArgumentParser(description="Trazabilidad/verificación de inputs (INV-5).")
    ap.add_argument("--regenerate-csv", action="store_true",
                    help="Regenera los CSV de deflactores desde INE (build_deflactores.py).")
    ap.add_argument("--where", action="store_true", help="Imprime la fuente oficial de cada input.")
    args = ap.parse_args()

    if args.where:
        print("Procedencia de cada input (detalle y MD5 en SOURCES.md):")
        for rel, (src, kind) in REGISTRY.items():
            print(f"  [{kind:9s}] {rel}\n               {src}")
        return 0

    if args.regenerate_csv:
        rc = regenerate_csv()
        if rc != 0:
            print("!! build_deflactores.py falló (¿faltan los IPC xlsx de entrada?).")
            return rc

    expected = parse_sources_md5()
    ok, mismatch, missing = verify(expected)

    print(f"=== Verificación de inputs contra SOURCES.md ({len(REGISTRY)} ficheros) ===")
    for rel in ok:
        print(f"  OK        {rel}")
    for rel, why in mismatch:
        print(f"  MISMATCH  {rel}  -> {why}")
    for rel in missing:
        src, kind = REGISTRY[rel]
        accion = ("regenerar: python data/download_data.py --regenerate-csv"
                  if kind == "generated" else f"descarga MANUAL desde: {src}")
        print(f"  FALTA     {rel}\n              {accion}")

    if mismatch:
        print("\nABORTA: hay ficheros cuyo MD5 no coincide con SOURCES.md. No son los certificados.")
        return 1
    if missing:
        print("\nFaltan inputs (ver acciones arriba). En un clon normal NO deberían faltar: van en git.")
        return 2
    print("\nTodo coincide con SOURCES.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
