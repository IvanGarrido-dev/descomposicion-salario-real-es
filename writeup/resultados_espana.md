# Resultados v1 — España. Descomposición contable del salario real por hora, 1996-2019

Informe técnico. Reporta y define; no interpreta. Todos los números proceden de
`output/` (CSV certificados), de `SOURCES.md` (procedencia y MD5) o se generan
desde el modo certificado (`src/decomposition.py`); cada tabla cita su origen. El
modo certificado es `deflator="cne_p31"`, `renorm=True`, `productivity="per_hour"`,
periodo `(1996, 2019)`.

---

## 1. Resumen de resultados

Contribución acumulada por componente al crecimiento del salario real por hora,
**1996-2019 (23 años)**, en puntos porcentuales (p.p.), para los dos deflactores.

Cifras a 3 decimales (uniforme en todo el informe; coincide con el redondeo de
cabecera −10.572). Valores exactos a 4 decimales en los CSV de `output/`.

| Componente | cne_p31 (certificado) | ipc (sensibilidad) |
|---|---:|---:|
| Participación del trabajo | −6.504 | −6.504 |
| Composición laboral | 10.000 | 10.000 |
| Capital TIC | 0.621 | 0.621 |
| Capital no-TIC | 9.614 | 9.614 |
| Capital intangible | 1.758 | 1.758 |
| **PTF (intrasectorial)** | **−10.572** | **−10.572** |
| Reasignación (horas) | 0.639 | 0.639 |
| Composición del crecimiento sectorial (Domar) | 2.550 | 2.550 |
| Reconciliación (no explicado) | −0.068 | −0.068 |
| Cuña de precios | −2.293 | −3.222 |
| **Salario real (total)** | **5.746** | **4.816** |

*Fuente: `output/datos_acumulado_1996_2019.csv`.*

> **PTF (intrasectorial) = −10.572 p.p.**: componente residual de la descomposición
> de la productividad por hora — la parte no atribuida a los factores medidos
> (composición laboral y servicios de capital). Es un residuo de Solow; su contenido
> no lo identifica el método (§7). El valor depende de la convención de unidades y de
> cobertura (apéndices C–D); el signo es robusto a ambas.

La identidad cierra por construcción: la suma de los diez componentes iguala el
salario real total (residuo de cierre < 1e-9 p.p., INV-2).

---

## 2. Objeto y alcance

**Qué se mide.** El crecimiento del **salario real por hora** definido como la
**compensación laboral por hora deflactada**, $W/P_c$, con $W = \mathrm{LAB}/H$.

**Qué NO se mide.**

- No es el salario del **asalariado medio**. `LAB` es la compensación laboral total
  e incluye una **imputación de la renta laboral de los autónomos** (convención
  EUKLEMS growth accounts), de modo que la participación del trabajo $s_L$ es la
  cuota total de renta laboral, no la de los asalariados. Es una **media por hora a
  nivel agregado**, no una distribución de salarios ni una mediana.
- No mide **niveles**, sino tasas de crecimiento (deltas log acumulados).
- No mide **distribución** (dispersión, percentiles).
- El concepto es **por lugar de trabajo** (horas trabajadas en el territorio), no
  por residencia.

**Alcance.** País: España. Periodo estructural: **1996-2019 (23 años)**. Los años
**2020-2021** se reportan solo como **descriptivos**, etiquetados como
no-estructurales (§6.4, §9). **Límite duro: 2021** — la descomposición sectorial
(within, PTF) no se extiende más allá porque las contribuciones EUKLEMS terminan en
2021 (§9).

---

## 3. La identidad contable

A nivel de toda la economía, por hora trabajada, de forma **exacta**:

$$\Delta\ln\!\left(\frac{W}{P_c}\right) = \Delta\ln(s_L) + \Delta\ln\!\left(\frac{VA_Q}{H}\right) + \left[\,\Delta\ln(P_{VA}) - \Delta\ln(P_c)\,\right]$$

Definición de cada término (unidades: todas son tasas de crecimiento, delta log;
las contribuciones se expresan en p.p.):

| Símbolo | Definición | Variable EUKLEMS / INE |
|---|---|---|
| $W = \mathrm{LAB}/H$ | Compensación laboral por hora (nominal) | `LAB` / `H_EMP` |
| $s_L = \mathrm{LAB}/VA$ | Participación del trabajo en el VAB | `LAB` / `VA_CP` |
| $VA_Q/H$ | Productividad real por hora (VAB en volumen / horas) | `VA_Q` / `H_EMP` |
| $P_{VA} = VA/VA_Q$ | Deflactor implícito del VAB | `VA_CP` / `VA_Q` |
| $P_c$ | Deflactor del consumo (cne_p31 o ipc) | CNE P.31 / IPC INE |

El término central, $\Delta\ln(VA_Q/H)$, se abre a su vez en cinco factores
intrasectoriales (within) más dos términos de cambio estructural (reasignación,
Domar) y un residuo de reconciliación (§5). El término entre corchetes es la **cuña
de precios** $\Delta\ln(P_{VA}) - \Delta\ln(P_c)$.

Es una **identidad contable exacta**, no un modelo causal: cierra por construcción
y no implica dirección de causalidad entre sus términos.

---

## 4. Datos y procedencia

Detalle completo y MD5 en `SOURCES.md`. Resumen:

| Fuente | Contenido | Identificadores |
|---|---|---|
| EUKLEMS & INTANProd 2024 (LLEE) | Cuentas de crecimiento y nacionales, España, 1995-2021 | `ES_growth accounts.xlsx`, `ES_national accounts.xlsx` (+labour, capital) |
| INE — IPC | IPC base 1992 (1995-2001) y ver.2 base actual (2002-2025) | tablas 269, 76144 |
| INE — IPC enlazado | Enlace 2001→2002 reconstruido | tablas 24077 / `IPC290751`, 76134 / `IPC290750` |
| INE — CNE | Deflactor implícito del consumo de los hogares (P.31) | tablas 67823 (nominal), 67824 (volumen) |

- **Partición sectorial:** 33 ramas NACE Rev. 2, partición MECE (cobertura del 100 %
  de las horas; §6, apéndice B).
- **Concepto de salario:** $W = \mathrm{LAB}/H$ (§2).
- **Enlace IPC 2001→2002:** reconstruido desde la serie enlazada del INE, no
  hard-codeado. Resultado: inflación media 2002 = **3,5278 %** (`SOURCES.md`).
- **MD5:** los ocho ficheros de entrada tienen MD5 certificado en `SOURCES.md`,
  verificable con `python data/download_data.py`.

---

## 5. Método

### 5.1 Selección de la familia de contribuciones LP (INV-1)

EUKLEMS publica dos familias de contribuciones a la productividad: `LP1*` (por hora
trabajada) y `LP2*` (por persona empleada). La familia **no se hard-codea**: el
código la **selecciona** comparando la tasa publicada `LP*_G` con la productividad
recomputada desde `VA_Q` y `H`, y exige coincidencia inequívoca.

| año | `LP1_G` | $100\,\Delta\ln(VA_Q/H)$ | `LP2_G` | $100\,\Delta\ln(VA_Q/\mathrm{EMP})$ |
|---:|---:|---:|---:|---:|
| 1996 | 0.8601 | 0.8601 | 1.1198 | 1.1198 |
| 2009 | 2.8388 | 2.8388 | 3.1951 | 3.1951 |
| 2014 | 0.0413 | 0.0413 | 0.0436 | 0.0436 |
| 2020 | 0.1302 | 0.1302 | −7.0037 | −7.0037 |
| 2021 | −0.8881 | −0.8881 | 3.5427 | 3.5427 |

*Generado desde el modo certificado (`LP*_G`, `VA_Q`, `H_EMP`, `EMP`).*

- `LP1_G` $\equiv 100\,\Delta\ln(VA_Q/H)$: error máximo **3.94e-07 p.p.** (1996-2021).
- `LP2_G` $\equiv 100\,\Delta\ln(VA_Q/\mathrm{EMP})$: error máximo **3.08e-07 p.p.**
- Divergencia `LP1_G` frente a la productividad **por persona**: hasta **7.1339 p.p.**
  (2020), por el desplome de horas/persona en la pandemia.

La identidad del documento es **por hora**; por coherencia de unidades exige la
familia **LP1**. El selector certifica esta elección por (a) coincidencia con la
productividad por hora recomputada (límite de redondeo de la hoja, ~5e-7 p.p.) y
(b) separación dominante (~7 p.p.) frente a la otra familia.

### 5.2 within: contribuciones intrasectoriales (INV-3)

El within es la suma ponderada Törnqvist de las contribuciones por rama (familia
LP1), con pesos iguales a la media de las cuotas de horas de $t-1$ y $t$,
**renormalizada** sobre las ramas con desglose completo. La cobertura se evalúa por
factor y año; las ramas sin desglose (apéndice B) no se tratan como cero en
silencio: sus pesos se redistribuyen entre las ramas con dato (esto es un supuesto,
no una corrección neutra; §9).

### 5.3 between constructivo (DESIGN §4)

El término que el residuo agregado de productividad ($\Delta\ln(VA_Q/H) -$ within)
recoge se abre en **dos términos con significado** más un residuo:

- **Reasignación (horas):** término Olley-Pakes estático sobre **niveles nominales**
  (VAB nominal por hora, comparable entre ramas en euros). Mide **a dónde van las
  horas** (hacia/desde ramas de mayor/menor productividad nominal relativa):
  $\sum_i \Delta s_{it}\,\ln(y_{it}/\bar y_t)$, con $s$ cuota de horas e $y$ VAB
  nominal por hora.
- **Composición del crecimiento sectorial (Domar):** $\sum_i (v_{it} - w_{it})\,\Delta\ln(VAQ_{it})$,
  con $v$ cuota de VA nominal, $w$ cuota de horas, $\Delta\ln(VAQ_i)$ crecimiento
  real del output por rama. Mide **qué ramas crecen en output**.
- **Reconciliación:** $\Delta\ln(VA_Q/H) - \text{within} - \text{reasignación} - \text{Domar}$.
  Se reporta **siempre visible**; acotada por test (|reconciliación| < 0,2 p.p.
  acumulado, INV-4).

**Limitación declarada (DESIGN §4):** la reasignación usa **niveles nominales** y el
within/Domar usan **crecimientos reales**. En ningún punto se comparan **niveles** de
`VA_Q` encadenados entre ramas (los volúmenes encadenados no son aditivos ni
comparables en nivel). La descomposición **mezcla niveles nominales con crecimientos
reales**: es la opción menos mala con datos encadenados, no una descomposición
perfecta.

### 5.4 Deflactor

- **cne_p31** (certificado): deflactor implícito del gasto en consumo final de los
  hogares de la Contabilidad Nacional (Paasche encadenado). Es **coherente** con el
  resto del marco, que es contabilidad nacional.
- **ipc** (sensibilidad): índice de precios de consumo del INE (Laspeyres, cesta
  fija).

Miden objetos distintos (Paasche encadenado vs Laspeyres de cesta fija). El default
es **cne_p31** por coherencia interna del marco; el **ipc** se reporta como banda de
sensibilidad (§6.1, apéndice E). No se elige un ganador en el texto.

---

## 6. Resultados detallados

### 6.1 Acumulado 1996-2019, dos deflactores

Ver la tabla de §1 (`output/datos_acumulado_1996_2019.csv`). Solo dos filas
dependen del deflactor: el salario real total (5.746 vs 4.816) y la cuña de precios
(−2.293 vs −3.222); el resto es idéntico. Banda del deflactor en el salario real:
**0,93 p.p.** (apéndice E).

### 6.2 Apertura del término between

$$\underbrace{0.639}_{\text{Reasignación (horas)}} + \underbrace{2.550}_{\text{Domar}} + \underbrace{(-0.068)}_{\text{Reconciliación}} = 3.121$$

*Fuente: `output/datos_acumulado_1996_2019.csv`.* Los tres componentes son
independientes del deflactor y de la convención LP/renorm (apéndices C–D). La
reconciliación (−0.068) queda dentro de la cota INV-4 (|·| < 0,2 p.p.).

### 6.3 Serie anual

Serie completa por componente, 1996-2021, en `output/datos_anual.csv` (apéndice A
reproduce la tabla íntegra). Extracto de los primeros años (cne_p31, p.p.):

| año | Particip. | Comp.lab | Cap.no-TIC | PTF | Reasig. | Domar | Recon. | Cuña | Salario real |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1996 | −1.241 | 0.596 | 0.628 | 0.174 | 0.059 | −0.619 | −0.049 | 0.500 | 0.119 |
| 1997 | 0.545 | 0.119 | 0.150 | −0.586 | 0.265 | −0.187 | −0.252 | −0.563 | −0.519 |
| 1998 | 0.500 | 0.145 | −0.004 | −1.014 | 0.314 | −0.190 | −0.293 | 0.738 | 0.204 |
| 1999 | −0.310 | 0.136 | 0.180 | −0.953 | 0.408 | 0.117 | −0.487 | 0.103 | −0.759 |
| 2000 | −0.580 | 0.170 | 0.132 | −0.048 | 0.223 | 0.227 | −0.272 | −0.826 | −0.913 |

*Fuente: `output/datos_anual.csv` (columnas Capital TIC y Capital intangible
omitidas en el extracto por espacio; completas en el CSV y en el apéndice A).*

### 6.4 Etapas (medias anuales)

Contribución media anual (p.p./año) por etapa. Las tres primeras son estructurales;
**2020-2021 es solo descriptivo** (etiqueta no-estructural).

| Etapa | años | PTF | Reasig. | Domar | Particip. | Salario real (media) | Salario real (acum.) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1996-2007 Expansión | 12 | −0.861 | 0.133 | 0.233 | −0.506 | −0.039 | −0.464 |
| 2008-2013 Crisis y devaluación interna | 6 | −0.487 | −0.185 | 0.245 | −0.300 | 0.431 | 2.587 |
| 2014-2019 Recuperación | 6 | 0.446 | 0.024 | −0.285 | 0.227 | 0.604 | 3.623 |
| *2020-2021 COVID (descriptivo)* | 2 | −2.742 | 0.739 | 0.582 | 2.262 | 2.678 | 5.356 |

*Fuente: `output/datos_etapas.csv` (columnas de capital omitidas por espacio;
completas en el CSV).*

> **Nota (2020-2021, no-estructural).** Los valores positivos de participación del
> trabajo (+2.262/año) y de salario real (+2.678/año) en la etapa COVID reflejan el
> **colapso de las horas trabajadas y la cobertura ERTE** (compensación contable
> mantenida sobre un denominador de horas hundido), no una mejora real del salario.
> No deben leerse como efecto estructural (§9).

### 6.5 Figuras

En `output/` (generadas por `python src/run.py`):

| Fig. | Contenido |
|---|---|
| [g1](../output/g1_descomposicion_anual.png) | Descomposición anual 1996-2021 (COVID sombreado) |
| [g2](../output/g2_descomposicion_etapas.png) | Contribuciones medias por etapa |
| [g3](../output/g3_anatomia_acumulada.png) | Anatomía acumulada 1996-2019 (cascada) |
| [g4](../output/g4_apertura_between.png) | Apertura del between (reasignación + Domar + reconciliación) |
| [g5](../output/g5_termometro_ptf.png) | PTF bajo LP2 / LP1 sin renorm / LP1 renorm |
| [g6](../output/g6_banda_deflactor.png) | Banda del deflactor (cne_p31 vs ipc) |
| [g7](../output/g7_cobertura_contribuciones.png) | Cobertura en horas vs de contribuciones (INV-3) |
| [g8](../output/g8_ptf_trayectoria.png) | PTF: contribución anual y acumulada |
| [g9](../output/g9_ranking_acumulado.png) | Ranking de componentes, acumulado 1996-2019 |

*(Los PNG están en `output/` —gitignored, regenerables con `python src/run.py`—;
los enlaces son relativos a este documento.)*

---

## 7. Qué contiene el residuo (PTF)

La PTF intrasectorial (−10.572 p.p.) es un **residuo**: agrega, sin distinguirlas,
varias magnitudes que el método no separa:

- **Mala asignación del capital** entre ramas o usos.
- **Márgenes** (poder de mercado): el método asume **competencia perfecta** (las
  cuotas de renta de los factores se igualan a sus elasticidades). Bajo ese supuesto,
  un cambio en los márgenes **no es observable** por separado y queda dentro del
  residuo. **Punto ciego declarado** (§9), no conclusión.
- **Infrautilización de capacidad** (el capital medido no se usa al 100 %).
- **Mismeasurement de intangibles** (I+D, software, capital organizativo).

Marco: la contabilidad **sitúa el origen** del componente en el residuo; **no
identifica su contenido**. *Señala dónde cavar, no qué hay enterrado.* No se derivan
de aquí recetas de política.

---

## 8. Garantías (invariantes y tests)

| Invariante | Qué certifica |
|---|---|
| INV-1 | La familia LP se selecciona contra $\Delta\ln(VA_Q/H)$ recomputado (no contra la etiqueta), con separación dominante. |
| INV-2 | La identidad cierra a < 1e-9 p.p. en todos los modos. |
| INV-3 | Cobertura real distinguida: en horas (100 %) vs de contribuciones (95,749 % de media, 1996-2019); reportada, no asumida. |
| INV-4 | within + reasignación + Domar + reconciliación = $\Delta\ln(VA_Q/H)$; reconciliación acotada, |·| < 0,2 p.p. |
| INV-5 | Datos versionados con procedencia y MD5; sin series embebidas en código; modo por defecto congelado contra un golden. |

**14 tests** (`tests/`) verdes. Golden congelado (`tests/golden_es.csv`), comparado
byte a byte. Reproducibilidad desde cero verificada en entorno limpio con
dependencias más nuevas (pandas 3.0.3, numpy 2.5.0): PTF −10.572 y golden idéntico
(§10).

---

## 9. Límites declarados

- **Corte 2021.** La descomposición sectorial (within, PTF) no pasa de 2021: las
  contribuciones EUKLEMS terminan ahí. Extenderla requiere una añada EUKLEMS más
  nueva, no empalmar otra fuente.
- **2020-2021 descriptivo.** Horas con saltos extremos (pandemia); no usar para
  conclusiones estructurales.
- **Artefacto-2020 del deflactor.** El deflactor implícito del consumo de 2020 sale
  ≈ 0 porque 2020 es el **año de referencia** del índice de volumen de la CNE
  (volumen 2020 = 100): el cociente nominal/volumen queda pegado al ancla ese año.
  Es un artefacto del punto de referencia, no una medida del deflactor real de 2020.
  Inocuo para 1996-2019.
- **Sesgo de la renormalización.** Las ramas sin desglose completo (≈ 4,25 % de las
  horas de media) se imputan a la media de las ramas con dato. Como son ramas de PTF
  presumiblemente alta (química, farmacia, electrónica, material eléctrico; apéndice
  B), la renormalización empuja la PTF agregada **un poco más negativa** de lo que
  sería con dato real. Se declara la **dirección** del sesgo; no se corrige.
- **Banda del deflactor.** El salario real acumulado depende del deflactor: 5.746
  (cne_p31) vs 4.816 (ipc); banda ≈ **0,93 p.p.** (apéndice E).
- **7 ramas sin desglose completo.** C20, C21, C26, C27, T, U (sin desglose ningún
  año) y C19 (parcial; sin PTF en 2020-2021). Apéndice B.
- **Márgenes invisibles.** El supuesto de competencia perfecta impide ver cambios en
  los márgenes; quedan dentro del residuo (§7). Punto ciego, no conclusión.
- **Media, no distribución.** $W = \mathrm{LAB}/H$ es una media por hora a nivel
  agregado; no informa de dispersión ni de salarios individuales.
- **Concepto por lugar de trabajo.** Horas trabajadas en el territorio, no por
  residencia.

---

## 10. Reproducibilidad

```bash
git clone <repo> && cd decomp_ivan
python -m pip install -e .[dev]
python src/run.py            # genera output/: 3 CSV + 9 PNG; PTF −10.572
python -m pytest tests/ -q   # 14 passed; golden byte a byte
```

Los datos de España van incluidos en el repo (versionados; ~2,3 MB), de modo que
clonar y correr funciona sin descargar nada. Verificación de reproducibilidad en
clon limpio + venv nuevo: **PTF −10.572, golden idéntico, 14/14**, con dependencias
más nuevas que las del entorno de desarrollo.

**Estado de `data/download_data.py`** (trazabilidad, no vía obligatoria):

- Los **CSV de deflactores** son regenerables desde INE (`build_deflactores.py`),
  byte a byte.
- Los **xlsx** (EUKLEMS, IPC) se actualizan a mano desde su fuente oficial: no hay
  URL directa verificable que reproduzca byte a byte el export concreto. En
  particular, exportar la tabla INE 76144 puede **no** reproducir byte a byte el
  fichero certificado — limitación de la fuente (formato del export), no del
  proyecto. `download_data.py` documenta las fuentes y verifica el MD5; aborta si no
  coincide.

---

## Apéndice A — Tabla anual completa (1996-2021)

Todos los componentes, p.p., modo certificado (cne_p31). **2020-2021 marcado como
descriptivo (no-estructural).** Fuente: `output/datos_anual.csv`.

| año | Particip. | Comp.lab | Cap.TIC | Cap.no-TIC | Cap.intang | PTF | Reasig. | Domar | Recon. | Cuña | Salario real |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1996 | −1.241 | 0.596 | 0.047 | 0.628 | 0.024 | 0.174 | 0.059 | −0.619 | −0.049 | 0.500 | 0.119 |
| 1997 | 0.545 | 0.119 | 0.020 | 0.150 | −0.031 | −0.586 | 0.265 | −0.187 | −0.252 | −0.563 | −0.519 |
| 1998 | 0.500 | 0.145 | 0.017 | −0.004 | −0.010 | −1.014 | 0.314 | −0.190 | −0.293 | 0.738 | 0.204 |
| 1999 | −0.310 | 0.136 | 0.028 | 0.180 | 0.021 | −0.953 | 0.408 | 0.117 | −0.487 | 0.103 | −0.759 |
| 2000 | −0.580 | 0.170 | 0.038 | 0.132 | 0.024 | −0.048 | 0.223 | 0.227 | −0.272 | −0.826 | −0.913 |

*Extracto. La tabla íntegra 1996-2021 (incluidos 2001-2019 y los descriptivos
2020-2021) está en `output/datos_anual.csv`; 2020 y 2021 figuran allí y deben
leerse con la etiqueta no-estructural (§9). Valores 2020/2021 de referencia: PTF
−7.373 (2020) y 1.888 (2021); salario real 6.261 (2020) y −0.905 (2021).*

---

## Apéndice B — Cobertura por rama y año

Las 33 ramas (partición MECE) cubren el **100 % de las horas**. La cobertura de
**contribuciones** es menor: 6 ramas no tienen desglose ningún año y 1 lo tiene
parcial.

- **Desglose completo:** 26 ramas.
- **Sin desglose ningún año (6):** C20, C21, C26, C27, T, U.
- **Desglose parcial (1):** C19 (sin PTF en 2020-2021).

% de horas con cobertura de contribuciones, por año (modo certificado):

| año | horas % | contrib % | sin desglose % | | año | horas % | contrib % | sin desglose % |
|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 1996 | 100.0 | 95.12 | 4.88 | | 2008 | 100.0 | 96.00 | 4.00 |
| 1997 | 100.0 | 95.22 | 4.78 | | 2009 | 100.0 | 95.87 | 4.13 |
| 1998 | 100.0 | 95.21 | 4.79 | | 2010 | 100.0 | 95.68 | 4.32 |
| 1999 | 100.0 | 95.19 | 4.81 | | 2011 | 100.0 | 95.68 | 4.32 |
| 2000 | 100.0 | 95.25 | 4.75 | | 2012 | 100.0 | 95.78 | 4.22 |
| 2001 | 100.0 | 95.31 | 4.69 | | 2013 | 100.0 | 95.84 | 4.16 |
| 2002 | 100.0 | 95.53 | 4.47 | | 2014 | 100.0 | 96.04 | 3.96 |
| 2003 | 100.0 | 95.60 | 4.40 | | 2015 | 100.0 | 96.21 | 3.79 |
| 2004 | 100.0 | 95.70 | 4.30 | | 2016 | 100.0 | 96.24 | 3.76 |
| 2005 | 100.0 | 95.81 | 4.19 | | 2017 | 100.0 | 96.21 | 3.79 |
| 2006 | 100.0 | 95.93 | 4.07 | | 2018 | 100.0 | 96.17 | 3.83 |
| 2007 | 100.0 | 96.00 | 4.00 | | 2019 | 100.0 | 96.37 | 3.63 |

Media 1996-2019: contribuciones cubiertas **95,749 %** (mínimo 95,124 % en 1996);
horas sin desglose **≈ 4,25 %** de media. *Generado desde el modo certificado
(`CountryData.contrib_coverage`).*

---

## Apéndice C — Robustez de especificación: LP1 vs LP2

Contribución acumulada 1996-2019 (p.p., cne_p31), bajo la familia certificada (LP1,
por hora) y la familia por persona (LP2). **LP2 es la convención INCONSISTENTE con
la identidad por hora** (§5.1); se muestra solo como diagnóstico. Para aislar el
efecto de la familia, ambas columnas se calculan **sin renormalizar** (LP2 con
renorm dispara INV-4: su reconciliación acumulada es +3.312 p.p., evidencia de la
inconsistencia).

| Componente | LP1 renorm (cert.) | LP1 sin renorm | LP2 sin renorm |
|---|---:|---:|---:|
| Participación del trabajo | −6.504 | −6.504 | −6.504 |
| Composición laboral | 10.000 | 9.574 | 9.574 |
| Capital TIC | 0.621 | 0.595 | 0.558 |
| Capital no-TIC | 9.614 | 9.196 | 8.272 |
| Capital intangible | 1.758 | 1.684 | 1.612 |
| **PTF (intrasectorial)** | **−10.572** | **−10.090** | **−12.303** |
| Reasignación (horas) | 0.639 | 0.639 | 0.639 |
| Composición del crecimiento sectorial (Domar) | 2.550 | 2.550 | 2.550 |
| Reconciliación (no explicado) | −0.068 | 0.394 | 3.640 |
| Cuña de precios | −2.293 | −2.293 | −2.293 |
| Salario real (total) | 5.746 | 5.746 | 5.746 |

*Generado desde el modo certificado (`decompose` con `force_family`).* Lectura: el
**signo** de la PTF es **robusto** a la convención (negativo en los tres casos); su
**magnitud** y el **reparto PTF↔reconciliación/between** dependen de la convención
(unidades por hora vs por persona, y renorm vs no-renorm). Reasignación y Domar son
invariantes (proceden de `VA_CP`/`VA_Q`, no de las contribuciones LP).

---

## Apéndice D — Renorm vs no-renorm

Modo certificado (renorm, INV-3) frente a modo sin renormalizar (las contribuciones
NaN se tratan como 0 y su peso en horas cae al residuo), familia LP1, cne_p31.

**La renormalización redistribuye el peso de las ramas sin desglose sobre los CINCO
factores within (no solo la PTF).** Por eso aquí se muestran los cinco, no únicamente
la PTF: de lo contrario el movimiento de, p. ej., composición laboral (10.000 vs
9.574) parecería inexplicado.

| Componente | renorm (certificado) | sin renorm | Δ (renorm − sin) |
|---|---:|---:|---:|
| Composición laboral | 10.000 | 9.574 | +0.426 |
| Capital TIC | 0.621 | 0.595 | +0.026 |
| Capital no-TIC | 9.614 | 9.196 | +0.417 |
| Capital intangible | 1.758 | 1.684 | +0.074 |
| **PTF (intrasectorial)** | **−10.572** | **−10.090** | **−0.481** |
| **Σ variaciones within** | | | **+0.462** |
| Reconciliación (no explicado) | −0.068 | 0.394 | −0.462 |
| Reasignación (horas) / Domar | invariantes | invariantes | 0 |

*Generado desde el modo certificado.* El cambio está **acoplado y cierra exacto**:
como reasignación y Domar son invariantes, la suma de las variaciones de los cinco
factores within iguala, con signo opuesto, la variación de la reconciliación
($\Delta$within total $= +0.462 = -\,\Delta$reconciliación). La renormalización mueve
la PTF de −10.090 a −10.572 (≈ 0,48 p.p. más negativa) y la reconciliación de +0.394
a −0.068. El modo sin renorm es el **modo no certificado** (reproduce el sesgo de
tratar como 0 las ramas sin desglose); el certificado es el renormalizado.

---

## Apéndice E — Banda del deflactor

Las únicas dos filas que dependen del deflactor (acumulado 1996-2019, p.p.):

| Fila | cne_p31 | ipc |
|---|---:|---:|
| Salario real (total) | 5.746 | 4.816 |
| Cuña de precios | −2.293 | −3.222 |

*Fuente: `output/datos_acumulado_1996_2019.csv`.* La diferencia cne_p31 − ipc es
**idéntica en ambas filas** (las dos se desplazan exactamente en $-\Delta\ln P_c$):
**+0,930 p.p.** (banda ≈ 0,93). El resto de componentes es idéntico en ambos
deflactores.

---

## Apéndice F — Glosario de variables EUKLEMS

Definiciones de la hoja *Legend* (EUKLEMS & INTANProd 2024, growth y national
accounts):

| Variable | Definición (Legend) |
|---|---|
| `VA_CP` | VAB a precios corrientes, millones de moneda nacional. |
| `VA_PYP` | VAB a precios del año anterior, millones. |
| `VA_Q` | VAB en volumen encadenado (precios de referencia), millones. *(Solo se usan sus tasas de crecimiento, invariantes a la base.)* |
| `LAB` | Compensación laboral, millones. Convención growth accounts: incluye imputación de la renta laboral de los autónomos (distinta de `COMP`, solo asalariados). |
| `CAP` | Compensación del capital, millones. |
| `H_EMP` | Horas totales trabajadas por las personas ocupadas, miles. |
| `H_EMPE` | Horas totales trabajadas por los asalariados, miles. |
| `EMP` | Número de personas ocupadas, miles. |
| `EMPE` | Número de asalariados, miles. |
| `COMP` | Remuneración de los asalariados, precios corrientes, millones *(national accounts)*. |
| `LP1_G` | Tasa de crecimiento del VAB por **hora** trabajada, delta log. |
| `LP2_G` | Tasa de crecimiento del VAB por **persona** empleada, delta log. |
| `LP1Con*` | Contribuciones al crecimiento del VAB **por hora**: `LC` composición laboral, `TangICT` capital TIC, `TangNICT` capital no-TIC, `Intang` capital intangible, `TFP` residuo (p.p.). |
| `LP2Con*` | Contribuciones análogas **por persona** empleada (p.p.). |

*Fuente: hojas `Legend` de `ES_growth accounts.xlsx` y `ES_national accounts.xlsx`.*

---

*Fin del informe. Números certificados a fecha de la última ejecución de
`python src/run.py`; modo por defecto congelado en `tests/golden_es.csv`.*
