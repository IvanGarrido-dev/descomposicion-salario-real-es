# CLAUDE.md — Seguimiento del proyecto

> Documento de **seguimiento operativo**, cargado cada sesión. La **fuente de
> verdad del diseño es [DESIGN.md](DESIGN.md)** — aquí no se redecide nada: se
> rastrea estado, se anclan hechos ya verificados y se anota la decisión viva.
> Si algo de aquí contradice DESIGN.md, manda DESIGN.md (y se corrige esto).

## Qué es

Descomposición contable del crecimiento del salario real por hora (EUKLEMS &
INTANProd 2024, LLEE + deflactores INE/CNE). Reescritura limpia de un proyecto
previo que tenía 3 errores **de diseño** (unidades híbridas, `between` cajón-
residuo, lenguaje causal sobre un residuo). El objetivo: que esos 3 fallos sean
**imposibles por construcción**. Detalle en DESIGN.md §0.

## Reglas de trabajo (innegociables)

- Trabajar **solo dentro de `decomp_ivan/`**. No tocar otros proyectos del repo
  (Descomposición salarios reales, Decrecimiento, horas epa, Toy model TNT). Esa
  carpeta vecina solo se usa como **origen de datos ya verificados** (lectura).
- **v1 = España, impecable, antes que nada.** No se arranca v2 (multi-país)
  hasta que v1 pase todos los tests y tenga su pieza escrita (DESIGN §1, §9.6).
- **Datos, no invención.** Ninguna serie embebida como literal en `.py`
  (INV-5). Toda serie nueva: CSV en `data/` + procedencia en `SOURCES.md` + MD5.
- Antes de generar código nuevo, comprobar el invariante que lo sustenta y
  **testearlo**, no asumirlo. "Más rápido de lo que se ejecuta" es el antipatrón.

## Hechos verificados (anclados — no re-derivar)

- **INV-1 (cornerstone) ✔ verificado 2026-06-24** al nivel TOT, 1996-2021:
  - `LP1_G` ≡ Δln(VA_Q/H)  (por **hora**) — error máx **0.0**
  - `LP2_G` ≡ Δln(VA_Q/EMP) (por **persona**) — error máx **0.0**
  - Difieren de verdad: `LP1_G` vs Δln(VA_Q/EMP) diverge hasta **7,13 p.p.** (2020).
  - ⇒ La identidad por hora exige familia **LP1**. El proyecto viejo usaba LP2
    (por persona) sobre identidad por hora: mismatch que infla la PTF intrasectorial
    ~2,2 p.p. (−12,30 → −10,09 acum. 1996-2019). El código **autoselecciona** la
    familia (no la hardcodea) y asierta coincidencia exacta (INV-1, DESIGN §2).
- **Cobertura ES (INV-3):** 33 ramas (partición MECE, 100 % de horas). Sin
  desglose completo: `C20, C21, C26, C27, T, U` (NaN todos los años) + `C19`
  parcial (solo PTF 2020-21). Horas no cubiertas ≈ **4,2 %** medio. Idéntico en
  LP1 y LP2.
- **Deflactor (DESIGN §5):** enlace IPC 2001→2002 real = **3,5278 %** (no el 3,5 %
  hardcodeado). `cne_p31` vs `ipc` difieren ~0,9 p.p. en salario real acum. (banda).
- **Periodo:** default **1996-2019 = 23 años** (NO "30"). 2020-21 solo descriptivo.
- **⚠ Artefacto 2020 (CNE):** `dln_deflactor` P31 de 2020 ≈ **+0,0003** (casi plano)
  es un **artefacto del punto de referencia** (el índice de volumen tiene ref.
  2020=100, así que el cociente nominal/volumen queda pegado al ancla ese año). NO
  es verdad económica (el deflactor real del consumo en 2020 no fue plano).
  Inocuo para 1996-2019; **al tocar 2020-2021 en el writeup, declararlo**.
- **INV-1 precisión:** la selección de familia se certifica contra la productividad
  por hora **recomputada** (Δln(VA_Q/H)) + separación dominante (~7 p.p.), no contra
  la etiqueta `LP*_G`. El match alcanzable es ~5e-7 p.p. (LLEE redondea); el 1e-9
  estricto solo aplica al cierre de identidad recomputado (INV-2).
- **PTF certificada (acum. 1996-2019, default cne_p31):**
  - **−10,572 = LP1 + renorm INV-3** → cifra de cabecera certificada (golden).
  - **−10,09 = LP1 SIN renorm** → modo bug (`renorm=False`), solo para el writeup
    (muestra que sin renorm la PTF afloja +0,48 y el residuo se infla +0,46, acoplados).
  - **Sesgo de la renorm: va hacia lo NEGATIVO.** Imputa las ~4,2% de horas sin
    desglose (química, farma, electrónica, eléctrico, T, U) a la media; pero esas
    ramas tech son de PTF probablemente ALTA, así que renormalizar subestima su
    aportación y exagera levemente lo negativo de la PTF agregada. Writeup: decir
    "−10,6, con sesgo conocido hacia lo negativo por imputar las ramas tech sin
    desglose". No cambia el número; es para no esconder de qué pie cojea.
- **Apertura del viejo `between` (acum. 1996-2019, default):** = **Reasignación
  (horas) 0.64 + Composición del crecimiento sectorial (Domar) 2.55 + Reconciliación
  −0.07**. Lectura económica (oro para el writeup, corrige al proyecto viejo): el
  "between" positivo NO es sobre todo trasvase de horas (eso es pequeño, 0.64); el
  grueso (2.55) es que **las ramas intensivas en VA crecieron más en output** —
  composición del crecimiento, no reasignación de mano de obra. Nombres que NO se
  deben fundir: **Reasignación = a dónde van las horas**; **Domar = qué ramas crecen
  en output**. No llamar al Domar "cambio estructural" a secas (abarca ambos canales).
  La reconciliación −0.07 se mantiene VISIBLE en la tabla (credencial de anatomía
  casi completa), nunca absorbida.

## Estado al cierre de sesión (2026-06-25)

**v1 (España) CERRADA.** §0–§6 hechos y testeados (14/14). Núcleo + driver (3 CSV +
9 PNG) + README + reproducibilidad (INV-5: clon limpio reproduce −10.572/golden/14-14
con pandas 3.0/numpy 2.5) + informe `writeup/resultados_espana.md` (revisado con Ivan).
Golden congelado. **Nada commiteado** (Ivan decide dónde/cuándo). **Retomar por v2**
(multi-país: misma función con `country`, sin reescribir; no arrancar hasta querer
abrirla). Antes de tocar nada: `python -m pytest tests/ -q` = 14 passed; `python
src/run.py` regenera salidas.

## Estado de ejecución (DESIGN §9)

Leyenda: ⬜ pendiente · 🟡 en curso · ✅ hecho y testeado

- ✅ **0. Andamiaje** — esqueleto, datos copiados+MD5, `CLAUDE.md`, `SOURCES.md`,
  `pyproject.toml`, `.gitignore`. (INV-1 verificado.)
- ✅ **1. Datos** — `src/data_loading.py` (`CountryData` + gate INV-3 + LP auto-select),
  `data/build_deflactores.py` + `ipc_enlazado.csv`/`cne_p31.csv` con MD5 en `SOURCES.md`.
  ✅ `data/download_data.py` (verifica MD5 contra SOURCES.md; regenera CSV vía INE;
  documenta fuentes — EUKLEMS/IPC xlsx con descarga MANUAL, sin URLs inventadas).
- ✅ **INV-5 (reproducibilidad) CERRADO (2026-06-25)** — datos ES versionados (gitignore
  ya no los excluye; +scratchpad/ ignorado), `[build-system]`+`py-modules` en pyproject
  (`-e .` instala módulos importables sin depender de `sys.path.insert`), README
  `pip install -e .[dev]` + sección **Datos**. Repro en clon limpio (venv nuevo, deps
  más nuevas pandas 3.0.3/numpy 2.5.0, SIN copiar datos a mano): PTF −10.572, golden
  byte a byte, 14/14, MD5 = SOURCES.md. (NO commiteado: Ivan decide.)
- ✅ **2. Núcleo** — `src/decomposition.py` (pura: identidad + within LP1 renorm
  INV-3; flag `renorm` default True, False=bug). Golden `tests/golden_es.csv`
  congelado (cne_p31/renorm/per_hour). Tests `test_invariants.py`+`test_golden.py`:
  **12/12 verde**. ptf certificada = −10.572.
- ✅ **3. Reasignación** — `src/reallocation.py` con DOS términos (decisión A de Ivan):
  **Reasignación (horas)** = OP niveles nominales (0.64) + **Composición del
  crecimiento sectorial (Domar)** = Σ(v−w)·Δln(VAQ) (2.55) + **Reconciliación
  visible** (−0.07). El núcleo abre el viejo `between` en estos tres; golden
  re-congelado (10 componentes); INV-4 (within+OP+Domar+recon=c_prod, |recon|<0.2 en
  modo certificado). Tests **14/14 verde**. DESIGN §4/§8 corregido a dos términos
  (defecto de la especificación, sacado por el diagnóstico de §3).
  ⚠️ Regla intacta: Domar usa CRECIMIENTOS Δln(VAQ), nunca niveles encadenados.
- ✅ **4. Driver** — `src/run.py`: carga ES, modo certificado, escribe en `output/`
  **3 CSV** (anual, acumulado, etapas) + **9 PNG**: g1 anual, g2 etapas, g3 anatomía
  (waterfall), g4 apertura del between, g5 termómetro PTF (−12,30/−10,09/−10,57),
  g6 banda deflactor, g7 cobertura, g8 trayectoria PTF, g9 ranking acumulado
  (formato del viejo recuperado, datos certificados + etiquetas honestas). Consola ascii-safe.
  Añadido `load_country(force_family=)` SOLO diagnóstico (termómetro LP2). Etiquetado
  disciplinado (23 años, COVID/artefacto marcados, Domar≠cambio estructural).
  **Restyle (2026-06-25):** paleta **basada en azul** (máquina productiva en azules/teal;
  lastres —particip., PTF ladrillo, cuña ámbar— en acentos cálidos) + layout
  determinista (`_finish`: banda inferior reservada para leyenda y fuente, sin
  `bbox_inches='tight'`) que elimina los solapes leyenda/fuente/título.
- ✅ **5. README** — `README.md`: qué es / cómo correrlo / qué NO afirma. Capa de
  honestidad completa (anatomía no causa; qué cabe dentro del residuo: mala
  asignación, márgenes (método asume competencia perfecta, no los ve), utilización,
  intangibles; sesgos declarados; sin recetas de política; benchmark = "¿outlier?"
  no "¿real la PTF?"). Resultado de cabecera y garantías INV-1..5.
- ✅ **6. v1 cerrada** — INV-5 (reproducibilidad) cerrado: datos ES versionados,
  `[build-system]`+`py-modules`, `download_data.py`, README install `[dev]`. Repro en
  clon limpio (pandas 3.0/numpy 2.5): PTF −10.572, golden idéntico, 14/14. Informe
  de resultados `writeup/resultados_espana.md` escrito y revisado con Ivan (aséptico,
  3 dec. uniforme, capa de honestidad seca, apéndices A-F). Nada commiteado.
  Nota: extender a 2020-2026 NO viable para la anatomía (EUKLEMS acaba en 2021); macro
  2020-24 vía CNE sería panel aparte. **v2 (multi-país) NO arrancada** — siguiente fase.

**Siguiente paso concreto:** §6 — validar v1 de punta a punta (tests verdes +
`run.py` regenera salidas) y escribir la pieza de España apoyada en `output/` y la
capa de honestidad del README. Solo tras cerrar v1: v2 multi-país.

## Mapa de archivos

```
decomp_ivan/
├── DESIGN.md            # diseño (fuente de verdad)
├── CLAUDE.md            # este seguimiento
├── README.md            # qué es / cómo correrlo / qué NO afirma  ✔
├── SOURCES.md · pyproject.toml · .gitignore  ✔
├── data/
│   ├── euklems_2024/    # ES_{growth,national,labour,capital} accounts.xlsx  ✔
│   ├── deflactores/     # 269/76144.xlsx + ipc_enlazado.csv + cne_p31.csv  ✔
│   └── build_deflactores.py   # re-descarga INE -> CSV  ✔
├── src/                 # data_loading.py · decomposition.py · reallocation.py · run.py  ✔
├── tests/               # conftest.py · test_invariants.py · test_golden.py · golden_es.csv  ✔ (14/14)
├── output/              # 3 CSV + 9 PNG generados (gitignored)  ✔
└── writeup/             # pieza de España (§6, pendiente)
```

Nota de nombres: DESIGN §3.2 sugería raíz `descomposicion-salario-real/`; la
carpeta real es `decomp_ivan/`. Se usa la real.

## Comandos

```bash
# (cuando exista) entorno y deps
python -m pip install -e .            # usa pyproject.toml
# correr España (genera output/: 3 CSV + 9 PNG)
python src/run.py
# tests (la red que hace reales las invariantes)
python -m pytest tests/ -q
```
Entorno actual: Python 3.12 del sistema (sin venv); `matplotlib`, `pandas`,
`numpy`, `openpyxl` instalados globalmente. Consola Windows = cp1252: **no
imprimir Δ ni griego en `print()`** (usar "dln"); los CSV van en utf-8-sig.

## Registro de decisiones

- **2026-06-24** · Repo nuevo en vez de parchear el viejo (errores de diseño, no
  de implementación). · INV-1 verificado empíricamente antes de escribir código. ·
  Datos versionados en `data/` (≈2,3 MB, pequeños) con MD5 en lugar de solo URLs.
- **2026-06-24 · §1** · Deflactores generados por `build_deflactores.py` (re-descarga
  INE, sin literales). CNE re-bajada de cero reproduce exacto lo verificado. ·
  `CountryData` expone `coverage_mask` (por factor/año) + `hours_coverage` y
  `contrib_coverage` separadas. · La renormalización NO se hace en carga (es de
  `decompose`).
- **2026-06-24 · INV-1 resuelto (con Ivan):** el `1e-9` del DESIGN era ambiguo
  (defecto de redacción). Acordado: el selector compara contra la productividad por
  hora **recomputada** desde VA_Q y H (no contra la etiqueta `LP*_G`), y certifica
  por match (~5e-7, redondeo de hoja) + **separación dominante** (~7 p.p.). El 1e-9
  estricto se reserva al cierre de identidad (INV-2), que sí es recomputado. DESIGN
  §2/§8 actualizado a "1e-9 contra cantidades recomputadas".
- **[EDITORIAL pendiente]** default deflactor `cne_p31` (coherencia) vs `ipc`
  (relatabilidad). Decidido en DESIGN §5 como `cne_p31`; revisable por el autor.
