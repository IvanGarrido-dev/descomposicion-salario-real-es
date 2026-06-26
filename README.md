# Descomposición del salario real por hora — España

Anatomía **contable** del crecimiento del salario real por hora en España,
1996-2019 (23 años). Atribuye el crecimiento del salario a sus componentes
contables —participación del trabajo, productividad por hora (abierta en cinco
factores intrasectoriales + reasignación + composición del crecimiento), y la
cuña de precios— mediante una identidad **exacta**.

> **Qué es** Es una descomposición contable: dice *dónde*
> está, en la contabilidad, el origen del estancamiento salarial.

> **señala dónde cavar; qué hay enterrado es harina de otro costal**

Fuente de verdad del diseño: [`DESIGN.md`](DESIGN.md). Seguimiento operativo:
[`Seguimiento.md`](Seguimiento.md). Procedencia de datos: [`SOURCES.md`](SOURCES.md).

---

## La identidad

A nivel de toda la economía, por **hora trabajada**, y de forma exacta:

```
Δln(W/Pc) = Δln(s_L) + Δln(VA_Q/H) + [ Δln(P_VA) − Δln(Pc) ]
```

con `W = LAB/H` (compensación laboral por hora), `s_L = LAB/VA` (participación
del trabajo), `VA_Q/H` (productividad real por hora), `P_VA = VA/VA_Q` (deflactor
del VA), `Pc` (deflactor del consumo). La productividad por hora se abre, a su
vez, en cinco factores intrasectoriales (composición laboral, capital TIC,
capital no-TIC, capital intangible y **PTF**), más dos términos de cambio
estructural (reasignación de horas y composición del crecimiento sectorial) y un
residuo de reconciliación.

---

## Resultado de cabecera (1996-2019, deflactor CNE)

El salario real por hora creció **+5,7 p.p. en 23 años** (~0,24 %/año):
prácticamente plano. Esa cifra pequeña es la resta de fuerzas grandes
(contribución acumulada, puntos porcentuales):

| Componente | p.p. |
|---|---:|
| Participación del trabajo | **−6,5** |
| Composición laboral | +10,0 |
| Capital TIC | +0,6 |
| Capital no-TIC | +9,6 |
| Capital intangible | +1,8 |
| **PTF (intrasectorial)** | **−10,6** |
| Reasignación (horas) | +0,6 |
| Composición del crecimiento sectorial (Domar) | +2,6 |
| Reconciliación (no explicado) | −0,1 |
| Cuña de precios | −2,3 |
| **Salario real (total)** | **+5,7** |

Lectura contable: la inversión y la cualificación aportaron unos
**+22 p.p.** (composición laboral +10,0 y servicios de capital +12,0); un residuo de productividad hundido (**−10,6**) y una participación
del trabajo en caída (**−6,5**) se llevaron casi todo. La PTF es el mayor lastre
contable. Gráficos en [`output/`](output/) (anatomía, apertura del residuo,
termómetro, banda del deflactor, cobertura, trayectoria de la PTF).

---

## Capa de honestidad

Esta sección es parte del diseño (DESIGN §7), no un descargo. Sin ella, los
números engañan.

### 1. Es anatomía
La descomposición **localiza** el origen contable del estancamiento. "La contabilidad sitúa el grueso en el residuo de productividad" es
un **dato**. "Esto se debe a X" es una **interpretación**, y va marcada como tal.

### 2. Qué cabe dentro del residuo (la PTF)
La PTF es el **residuo de Solow**: lo que queda de la productividad tras restar
las contribuciones medidas del capital y el trabajo. Una
PTF de −10,6 es compatible con varias historias que el método **no distingue**:

- **Mala asignación del capital** (hipótesis del ladrillo): capital volcado a
  construcción/inmobiliario de baja productividad marginal durante la burbuja.
- **Márgenes empresariales crecientes.** El marco asume **competencia perfecta**
  (las cuotas de factores = elasticidades). Si los márgenes suben, parte de lo
  que aquí aparece como "caída de PTF + caída de participación del trabajo" es en
  realidad **trasvase al beneficio**, y el método **no puede verlo**.
- **Infrautilización de capacidad** (el capital medido no se usa al 100 %).
- **Mismeasurement de intangibles** (I+D, software, organización mal capturados).

### 3. Sesgos conocidos
- **Imputación de ramas sin desglose.** El 4,2 % de las horas (química, farma,
  electrónica, material eléctrico, T, U) no tiene desglose de contribuciones; se
  renormalizan los pesos sobre las ramas con dato. Es un **supuesto** (esas ramas
  se comportan como la media). Como son ramas de PTF
  probablemente alta, el sesgo va **hacia lo más negativo**: −10,6 es la mejor
  cifra disponible, con sesgo conocido hacia exagerar lo negativo.
- **La cifra depende de hacer bien las unidades.** Con la familia de
  contribuciones incoherente con la identidad por hora, la PTF salía −12,3; con
  unidades coherentes, −10,1; con la renormalización de cobertura, −10,6. El
  derrumbe es real, pero versiones previas lo exageraban ~1,7 p.p.
- **El "between":** Lo que se solía contar como
  "reasignación sectorial" (+3,1) es, bien medido, +0,6 de reasignación de horas
  y **+2,6 de composición del crecimiento** (ramas ya productivas creciendo más
  en output), pero no trasvase de mano de obra.
- **Banda del deflactor.** El salario real acumulado es +5,7 con el deflactor del
  consumo de la CNE y +4,8 con el IPC. El estancamiento aguanta con cualquiera;
  la magnitud tiene una banda de ~0,9 p.p.
- **2020-2021** se reportan solo como **descriptivos** (COVID): horas con saltos
  enormes y un artefacto del año de referencia del deflactor (volumen 2020=100).

### 4. Sin recetas de política
La descomposición señala un **cuello de botella contable** (el residuo). Qué
política lo resuelve —si es competencia, inversión pública, regulación, formación—
es **otra discusión**. Cualquier propuesta
es opinión del autor, no un resultado del modelo.

### 5. Sobre el benchmark multi-país (futuro)
Cuando exista, responderá *"¿es España un outlier?"*, **no** *"¿es real la PTF?"*.
Todos los países heredarían los **mismos supuestos** (competencia perfecta,
medición de intangibles, encadenamiento); un patrón común podría ser un
**artefacto global de medición**.

---

## Cómo está construido (garantías por diseño)

El proyecto convierte en **imposibles por construcción** tres errores de diseño
de un trabajo previo (unidades híbridas, `between`-cajón, lenguaje causal sobre un
residuo). Invariantes testeadas (`tests/`, ver DESIGN §2/§8):

- **INV-1 · coherencia de unidades.** La identidad es por hora. La familia de
  contribuciones se **autoselecciona** comparándola con la productividad por hora
  recomputada desde VA_Q y H (no se hardcodea "LP1"; se certifica por coincidencia
  + separación dominante de ~7 p.p. entre familias).
- **INV-2 · identidad exacta.** Cierra a < 1e-9 p.p. en todos los modos.
- **INV-3 · cobertura real.** Se distingue cobertura **en horas** (100 %) de
  cobertura **de contribuciones** (~95,8 %); se reporta como salida de primer
  nivel, no como check a posteriori.
- **INV-4 · `between` constructivo.** El antiguo residuo-cajón se abre en
  reasignación (horas) + Domar + reconciliación; la reconciliación se reporta
  **visible** y acotada (|recon| < 0,2 p.p.). Nunca se le pone la etiqueta
  "reasignación sectorial".
- **INV-5 · reproducibilidad.** Datos versionados con procedencia y MD5; ninguna
  serie embebida como literal en el código; el modo por defecto está congelado
  contra un CSV "golden" que un test compara.

El **término de reasignación** usa niveles **nominales** (VAB corriente por hora,
comparables en euros); el **Domar** usa **crecimientos** reales Δln(VA_Q). En
ningún punto se restan niveles de volumen encadenado entre ramas (eso no es
aditivo: sería cambiar un sesgo conocido por otro escondido).

---

## Cómo correrlo

```bash
python -m pip install -e .[dev]   # deps + pytest (sin [dev] no se instala pytest)
python src/run.py                 # genera output/: 3 CSV + 9 PNG
python -m pytest tests/ -q        # 14 invariantes (la red que las hace reales)
```

Los datos van incluidos en el repo, así que esto funciona sin descargar nada (ver
**Datos**). Para verificar la procedencia/MD5 o regenerar los deflactores:
`python data/download_data.py` (verifica) · `python data/build_deflactores.py` (regenera CSV desde INE).

---

## Datos

- **(a) Vienen incluidos en el repo.** Los inputs de España (4 xlsx EUKLEMS, 2 xlsx
  IPC, 2 CSV de deflactores; ~2,3 MB) están **versionados en git**. Clonar y correr
  funciona sin descargar nada: `pip install -e .[dev] && python src/run.py`.
- **(b) Regenerar / actualizar.** Para verificar la procedencia o pasar a una
  release nueva:
  - `python data/download_data.py` — verifica el MD5 de cada input contra
    `SOURCES.md` (aborta si algo no cuadra) y documenta de dónde sale (`--where`).
  - `python data/build_deflactores.py` — regenera los **CSV de deflactores**
    descargando de INE en vivo (verificado byte a byte).
  - Los **xlsx** (EUKLEMS, IPC) se actualizan a mano desde su fuente oficial: no hay
    URL directa que reproduzca byte a byte el export concreto, así que `download_data.py`
    documenta la página y marca descarga manual (sin inventar enlaces). Tras bajarlos,
    ese mismo script verifica el MD5.
- **(c) Procedencia (resumen).** EUKLEMS & INTANProd 2024 (LLEE), España, 1995-2021;
  IPC del INE (enlace real 2001→2002 = 3,5278 %, no el 3,5 % a mano); deflactor
  implícito del consumo de los hogares (CNE, P.31) por defecto. **Detalle completo,
  IDs de tabla INE y MD5 en [`SOURCES.md`](SOURCES.md).**

## Alcance

- **Periodo estructural: 1996-2019 (23 años).** 2020-2021, solo descriptivo.
- **v1 = España.** El multi-país (v2) no se arranca hasta que v1 cierre.
- **Límite duro:** la descomposición sectorial (PTF, within) llega hasta **2021**
  porque las contribuciones EUKLEMS terminan ahí. Extender la anatomía requiere una
  añada EUKLEMS más nueva, no empalmar otra fuente.

---

## Origen y reconocimiento

Este proyecto nace de auditar
[ProyectSubstrack/Substack](https://github.com/ProyectSubstrack/Substack), una
descomposición previa del salario real español de la que parto. Al revisarla
encontré tres problemas de diseño —una inconsistencia de unidades (contribuciones
por persona empleada dentro de una identidad por hora) que inflaba la PTF
~2,2 p.p., un término `between` puramente residual, y lenguaje causal sobre un
residuo— que aquí se corrigen por construcción. El mérito de plantear la pregunta
y el marco inicial es suyo; los errores corregidos y la reconstrucción son
responsabilidad mía.

---

## Licencia y citas

Código bajo licencia [MIT](LICENSE).

El uso de los datos **EUKLEMS & INTANProd** exige citar:
Bontadini F., Corrado C., Haskel J., Iommi M., Jona-Lasinio C. (2023),
*EUKLEMS & INTANProd: industry productivity accounts with intangibles*, LLEE.
Datos del **INE** (IPC; Contabilidad Nacional, deflactor del consumo P.31)
utilizados según sus condiciones de uso.
