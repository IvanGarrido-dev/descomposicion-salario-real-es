# DESIGN.md — Descomposición del salario real (modelo propio)

> Documento de diseño. Fija las decisiones **antes** de generar código. Todo lo
> marcado como **INVARIANTE** está validado empíricamente (no se discute, se
> testea). Lo marcado como **[EDITORIAL]** es una decisión revisable del autor.

---

## 0. Por qué un repo nuevo

Venimos de auditar un proyecto ajeno (ProyectSubstrack). En él encontramos tres
errores que **no son** de implementación sino de diseño, y por eso no se parchean
bien a posteriori:

1. **Unidades híbridas:** identidad por hora (`VA_Q/H`, `LAB/H`) pero `within`
   calculado con contribuciones por **persona ocupada** (familia `LP2`). Verificado:
   `LP1_G` ≡ Δln(VA_Q/H) con error 0.0000; `LP2_G` ≡ Δln(VA_Q/EMP). Mezclar las dos
   infla la PTF intrasectorial en ~2,2 p.p. (−12,30 → −10,09 acumulado 1996-2019) y
   vierte la cuña horas/persona al término de reasignación.
2. **`between` como residuo-cajón:** `between = agregado − Σwithin` recoge
   reasignación real + cuña horas/persona + NaN no cubiertos + error de
   reconciliación. No es un número con significado.
3. **Lenguaje causal sobre un residuo:** la PTF (un residuo de Solow) se presenta
   como mecanismo ("la ineficiencia anula el esfuerzo inversor").

El objetivo de este repo es que esas tres trampas sean **imposibles por
construcción**, no evitadas por disciplina.

---

## 1. Alcance

- **v1 = España impecable.** Se valida y se publica solo España.
- **v2 = benchmark multi-país** sobre la *misma* función, sin reescribir nada.
- La función acepta `country` desde el día 1, pero v1 no certifica más que `ES`.
- Regla anti-dispersión: no se arranca v2 hasta que v1 pase todos los tests y
  tenga su pieza escrita. (Patrón conocido: generar más rápido de lo que se
  ejecuta. v1 cierra antes de abrir v2.)

---

## 2. Invariantes del modelo (validados esta sesión → se testean)

**INV-1 · Coherencia de unidades.** La identidad es por hora. El `within` usa la
familia de contribuciones consistente con Δln(VA_Q/H). **No se hardcodea "LP1":** el
código *selecciona* la familia comparándola con la productividad por hora
**recomputada a plena precisión desde VA_Q y H** (no contra la etiqueta `LP*_G` de
LLEE, que viene redondeada). Certificación por dos vías: (a) la familia elegida casa
con la productividad recomputada al nivel de redondeo de la hoja (~5e-7 p.p.); (b) la
otra familia yerra ~7 p.p. (≈1e7×), así que la elección es inequívoca. El número de
familia no está garantizado estable entre releases ni países.
> Nota de precisión: el umbral estricto **1e-9 aplica a cantidades recomputadas de
> extremo a extremo** (el cierre de identidad, INV-2), no al match contra la hoja
> redondeada. (Corrige una redacción ambigua previa que pedía 1e-9 contra `LP*_G`.)

**INV-2 · Identidad exacta.** Δln(W/Pc) = Δln(s_L) + Δln(VA_Q/H) + [Δln(P_VA) −
Δln(Pc)]. Residuo de cierre < 1e-9 p.p. siempre. El test de cierre **no** se usa
como prueba de corrección (cierra por construcción); es solo un guardarraíl.

**INV-3 · Cobertura de contribuciones.** Antes de calcular, se computa la cobertura
real (no la de horas) factor×rama×año. Las ramas sin desglose completo (en ES:
C20, C21, C26, C27, T, U; parcial C19 en PTF 2020-21) **no se tratan como cero en
silencio**. Se renormalizan los pesos del `within` sobre las ramas cubiertas y se
reporta como salida de primer nivel el % de horas no cubierto. Es un *gate* que
avisa, no un check a posteriori.

**INV-4 · `between` constructivo.** Ver §4. El residuo de reconciliación se reporta
aparte; nunca se le pone la etiqueta "reasignación sectorial".

**INV-5 · Reproducibilidad.** Datos versionados con procedencia (release, fecha de
extracción, MD5). Ninguna serie embebida como literal en el `.py`. Modo por defecto
congelado contra un CSV "golden" que un test compara byte a byte.

---

## 3. Arquitectura

### 3.1 Función pura + driver

```python
def decompose(
    data: CountryData,            # datos ya cargados (sin I/O dentro)
    *,
    deflator: str = "cne_p31",    # "cne_p31" | "ipc"   (ver §5)
    productivity: str = "per_hour",  # fija la identidad; selecciona familia LP
    period: tuple[int, int] = (1996, 2019),
) -> DecompositionResult
```

- **Pura:** sin descargas, sin escritura, sin `print`. Entra `CountryData`, sale
  un `DecompositionResult` (dataclass con la tabla anual, las etapas, la cobertura
  y los metadatos de qué familia/deflactor se usaron).
- **Driver** (`run.py`): carga datos, barre países, escribe CSV/PNG, imprime
  resúmenes. Toda la suciedad de I/O vive aquí, no en `decompose`.
- `productivity="per_hour"` es el único modo certificado en v1. El parámetro existe
  para que, si alguien quiere "por persona", cambie **toda** la identidad de forma
  coherente (numerador y denominador), nunca un híbrido.

### 3.2 Estructura de carpetas

```
descomposicion-salario-real/
├── DESIGN.md                 # este documento
├── README.md                 # qué es, cómo correrlo, qué NO afirma (§7)
├── pyproject.toml            # deps fijadas: pandas, numpy, matplotlib, openpyxl
├── SOURCES.md                # release, fecha, URL y MD5 de cada fichero
├── data/
│   ├── download_data.py      # baja LLEE (URLs verificadas) + verifica MD5
│   ├── euklems_2024/         # xlsx por país (no en git si pesan; sí en .gitignore + checksums)
│   └── deflactores/          # ipc_enlazado.csv, cne_p31.csv (con procedencia)
├── src/
│   ├── data_loading.py       # CountryData, carga + gate de cobertura (INV-3)
│   ├── decomposition.py      # decompose(): identidad + within(LP auto) + between(§4)
│   └── reallocation.py       # término de reasignación constructivo
├── tests/
│   ├── test_invariants.py    # INV-1..INV-4
│   └── test_golden.py        # INV-5: ES modo por defecto vs golden CSV
├── output/                   # CSV y PNG generados (gitignored)
└── writeup/                  # los textos; ver §7
```

### 3.3 Stack

Python + pandas. **Nada de DuckDB aquí.** 20 países × 33 ramas × 25 años es
trivial en memoria; meter DuckDB sería complejidad por reflejo. (Se reserva para
proyectos donde el volumen lo justifique.)

---

## 4. El `between` constructivo (la parte con riesgo técnico real)

**La trampa:** los `VA_Q` son volúmenes **encadenados** (índice a 2015=100 de cada
rama). Los niveles encadenados **no son aditivos ni comparables entre ramas**. Por
tanto **NO** se puede computar una covarianza Olley-Pakes ni un Melitz-Polanec
directo sobre los niveles de `VA_Q` sectoriales. Hacerlo es cambiar un sesgo
conocido por otro escondido.

**La solución de diseño (DOS términos — corregido tras el diagnóstico de §3):**

> ⓘ Corrección. La especificación original pedía UN solo término de reasignación
> (OP de horas) esperando residuo pequeño. El diagnóstico de §3 demostró que eso
> deja una reconciliación grande (2,48 de 3,12): la productividad agregada por hora,
> con within ponderado por horas, tiene **dos** canales de cambio estructural, no
> uno. El omitido es el término Domar. Con los dos, la reconciliación cae a −0,07.
> Esto corrige un defecto de la especificación, no una desviación de la implementación.

- **Within** = suma Törnqvist (pesos = media de cuotas de horas de t-1 y t) de los
  crecimientos *reales* de productividad por rama (familia LP coherente, INV-1),
  renormalizada sobre ramas cubiertas (INV-3).
- **Reasignación (horas)** = Olley-Pakes **estático sobre niveles NOMINALES**
  (euros/hora, comparables entre ramas), cuotas renormalizadas dentro de lo cubierto:

  reasignación_t = Σ_i Δs_it · ln( y_it / ȳ_t )

  s_it = cuota de horas, y_it = VAB **nominal** por hora. Capta **a DÓNDE van las
  horas** (hacia/desde ramas de mayor/menor productividad nominal). En ES: pequeño (0,64).
- **Composición del crecimiento sectorial (Domar)** = Σ_i (v_it − w_it)·Δln(VAQ_it),
  con v_i = cuota de VA nominal, w_i = cuota de horas, Δln(VAQ_i) = **crecimiento**
  real del output por rama. Capta **QUÉ ramas crecen en output** (las de alta
  intensidad-VA creciendo más empujan la productividad agregada por encima del within
  ponderado por horas). En ES: el grueso (2,55). ⚠ Usa **crecimientos** Δln(VAQ_i),
  nunca niveles de VA_Q entre ramas: respeta la trampa del encadenamiento.
- **Reconciliación** = c_prod − within − reasignación − Domar. Se **reporta visible**
  (no se absorbe ni se renombra). Debe ser pequeña (ES: −0,07 acum.); acotada por
  test (INV-4, |recon| < 0,2 p.p.). Si se dispara, alguien rompió un término.

> **Nomenclatura (crítica para el writeup):** "Reasignación (horas)" = a dónde van
> las horas; "Composición del crecimiento sectorial (Domar)" = qué ramas crecen en
> output. NO llamar al Domar "cambio estructural" a secas: ese término abarca ambos
> canales y el lector los fundiría, perdiendo justo la distinción que da valor.

Esto convierte el `between` de cajón residual en (dos términos con significado +
residuo honesto y diminuto). Espíritu Melitz-Polanec/Domar adaptado a datos
encadenados. **Limitación a declarar en el writeup:** la reasignación usa niveles
nominales y el within/Domar crecimientos reales; es la opción menos mala con datos
encadenados, no una descomposición perfecta. Decláralo, no lo escondas.

---

## 5. Deflactor — **[EDITORIAL]**, decidido pero revisable

Se deflacta la compensación nominal por hora. Dos candidatos, ambos deflactores de
consumo:

- `cne_p31`: deflactor implícito del gasto en consumo final de los hogares (CNE).
  Paasche encadenado. **Coherente** con el resto del marco (todo es contabilidad
  nacional).
- `ipc`: índice de precios al consumo (INE). Laspeyres. Es lo que la gente
  reconoce como "inflación", pero conceptualmente mide otra cosa (cesta fija).

**Decisión:** `deflator="cne_p31"` por defecto, por coherencia interna del marco.
**Pero** el modelo computa y reporta **siempre ambos** como banda de sensibilidad.
Medido esta sesión: la diferencia es material (~0,9 p.p. en salario real acumulado,
~19% de la cuña). Por eso no se elige un ganador en el texto: se presenta la banda.

> Si el destino es divulgación pura y prima la relatabilidad, el autor puede
> cambiar el default a `ipc`. Es la única decisión de este documento que es de
> criterio, no técnica. Por eso queda aislada en un parámetro.

El enlace IPC 2001→2002 **no se hardcodea**: se reconstruye con el dato YoY oficial
(verificado: 3,5278%, casi idéntico al 3,5% que usaba el repo viejo) y se documenta
en `SOURCES.md`. Las series del deflactor viven en `data/deflactores/*.csv`, no en
el código.

---

## 6. Periodo y COVID

- Default: **1996-2019** (diagnóstico estructural). Decir siempre "**23 años**", no
  "treinta" (error del repo viejo, arrastrado del titular de prensa).
- 1996-2021 disponible pero **etiquetado** "incl. COVID — no usar para tesis de
  fondo". El resumen de consola imprime ambos tramos con esa etiqueta para que
  quien redacte no copie por error la PTF contaminada (−19,41 vs −10,09 limpio).
- Etapas: expansión 1996-2007, crisis/devaluación interna 2008-2013, recuperación
  2014-2019, COVID 2020-2021 (esta última, solo descriptiva).

---

## 7. Capa de honestidad (requisito de documentación, no opcional)

El `README.md` y el writeup deben, **por diseño**:

- Presentar la descomposición como **anatomía contable**, no como explicación
  causal. Frase guía: *"señala dónde cavar, no qué hay enterrado"*.
- Incluir una sección **"Qué cabe dentro del residuo (PTF)"**: mala asignación de
  capital (hipótesis del ladrillo), márgenes empresariales crecientes (el marco
  asume competencia perfecta: cuotas = elasticidades; si suben los márgenes, parte
  de la "caída de PTF + caída de participación laboral" es trasvase al beneficio y
  el método no lo ve), infrautilización de capacidad, y mismeasurement de
  intangibles.
- **No** afirmar "no es un problema de márgenes": es justo lo que el método no puede
  ver. Separar dato ("la contabilidad sitúa el origen en el residuo") de opinión
  ("a mi juicio, y esto ya es interpretación...").
- No cerrar con recetas de política presentadas como si se derivaran de la
  identidad. La descomposición señala el cuello de botella contable; qué política
  lo resuelve es otra discusión.
- Sobre el benchmark (v2): aclarar que responde "¿es España outlier?", **no** "¿es
  real la PTF?". Todos los países heredan los mismos supuestos; un patrón común
  podría ser un artefacto global de medición, no una verdad sobre las economías.

---

## 8. Tests (la red que hace las invariantes reales)

- `test_invariants.py`:
  - INV-1: la familia LP autoseleccionada casa con Δln(VA_Q/H) **recomputado**
    (match al nivel de redondeo de la hoja, ~5e-7 p.p., + separación dominante ~7
    p.p.); falla si alguien fuerza la incoherente. El 1e-9 estricto es para INV-2.
  - INV-2: identidad cierra < 1e-9 en todos los modos (deflactor × periodo).
  - INV-3: cobertura reportada; el % de horas no cubierto coincide con el conocido
    para ES (~4,2% medio); las ramas sin desglose son las esperadas.
  - INV-4: within + reasignación(horas) + Domar + reconciliación = c_prod; y la
    reconciliación acumulada acotada (|recon| < 0,2 p.p.). El test falla si un cambio
    futuro la dispara (señal de que se rompió un término).
- `test_golden.py` (INV-5): ES, modo por defecto, contra `tests/golden_es.csv`
  congelado. Cualquier cambio de número que no sea intencionado rompe el test.

---

## 9. Orden de ejecución sugerido

1. `data_loading.py` + `download_data.py` + `SOURCES.md` (datos verificados ES).
2. `decomposition.py` con INV-1 e INV-2 (identidad + within coherente). Congelar
   `golden_es.csv`.
3. `reallocation.py` (INV-4, el `between` constructivo). **Aquí está el riesgo;**
   ir con calma y comparar contra el residuo viejo para entender la diferencia.
4. Driver, CSV, PNG, resúmenes etiquetados (§6).
5. `README.md` con la capa de honestidad (§7).
6. **Parar. Validar v1. Escribir la pieza de España.** Solo entonces, v2.

---

### Resumen de una línea

Identidad por hora con `within` coherente (LP auto), `between` construido (no
residuo), cobertura como gate, datos versionados, deflactor parametrizado, y un
README que distingue contabilidad de causa. Lo demás es ejecución.
