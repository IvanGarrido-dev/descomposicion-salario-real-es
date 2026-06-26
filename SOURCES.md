# SOURCES.md — Procedencia y checksums de los datos

Cumple INV-5 (DESIGN §2): cada fichero tiene release, fecha de extracción, origen
y MD5. Ninguna serie va embebida como literal en el código.

## EUKLEMS & INTANProd 2024 (LLEE) — solo España

- Release: **2024**, producido por LLEE (Luiss Lab of European Economics).
- Origen: copia verificada del proyecto previo del repo (descarga LLEE original).
  `download_data.py` documentará las URLs oficiales y verificará estos MD5.
- Fecha de incorporación a este repo: **2026-06-24**.

| Fichero (`data/euklems_2024/`)   | MD5                              |
|----------------------------------|----------------------------------|
| ES_growth accounts.xlsx          | 3ff606d81ff9067cfbbc8c28c14ed99a |
| ES_national accounts.xlsx        | 3e2580a82d95b0a9781963b9daec1d06 |
| ES_labour accounts.xlsx          | 2600d02e47e5a097c870fc69a698780f |
| ES_capital accounts.xlsx         | f005c7489590ef8734c0592391070bad |

Hojas usadas: `VA_Q`, `VA_CP` (growth), `H_EMP`, `EMP` (national), familias de
contribución `LP1Con*`/`LP2Con*` y tasas `LP1_G`/`LP2_G` (growth). La familia se
**autoselecciona** verificando `LP*_G` ≡ Δln(VA_Q/H) (INV-1).

## Deflactores INE

### IPC (índice de precios de consumo)
| Fichero (`data/deflactores/`) | Contenido                          | MD5                              |
|-------------------------------|------------------------------------|----------------------------------|
| 269.xlsx                      | IPC base 1992, medias anuales 1995-2001 | 3afb1b931ac187c2f61a941595025e45 |
| 76144.xlsx                    | IPC ver.2 base actual, 2002-2025   | 3d00c7836625118a639a939390f6830a |

Enlace 2001→2002 **no hardcodeado**: se reconstruye con la serie general nacional
enlazada del INE (tabla **24077** / serie `IPC290751`, índice mensual; tabla
**76134** / serie `IPC290750`, variación anual). Resultado verificado: inflación
media 2002 = **3,5278 %**. Descarga API INE: 2026-06-24.

### CNE — deflactor implícito del consumo de los hogares (P.31)
Derivado como nominal/volumen de Contabilidad Nacional (enfoque demanda):
- Nominal (precios corrientes, Mn€): tabla **67823**.
- Volumen encadenado (índice, ref. 2020=100): tabla **67824**.
- Línea "Gasto en consumo final de los hogares", datos no ajustados; anual = suma
  de 4T (nominal) y media de 4T (índice). Descarga API/CSV INE: 2026-06-24.

### CSV de deflactores generados (por `data/build_deflactores.py`, 2026-06-24)
El script descarga de INE, imprime la serie cruda con su ID de tabla y escribe:

| Fichero (`data/deflactores/`) | Contenido                                   | MD5                              |
|-------------------------------|---------------------------------------------|----------------------------------|
| ipc_enlazado.csv              | índice IPC continuo 1995-2021 (enlace real 2002) | 0e4f2a452ea41cf44ad8e6cf44ca358e |
| cne_p31.csv                   | P.31 nominal (Mn€) + índice volumen, 1995-2021   | 07566fc0516e5b9e39cfac9bf2f40723 |

Reproducible: `python data/build_deflactores.py` (re-descarga INE; valores idénticos
verificados). El módulo `src/data_loading.py` los lee y deriva Δln Pc; no hay series
embebidas en código (INV-5).
