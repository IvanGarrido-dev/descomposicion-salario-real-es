#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py — Driver (§4). Toda la suciedad de I/O vive AQUÍ; decompose() es pura.

Carga ES, ejecuta la descomposición certificada (cne_p31, renorm, per_hour) y
escribe CSV + PNG + resúmenes etiquetados en output/. Reproduce lo base (anual,
etapas) y añade visualizaciones analíticas de los hallazgos del proyecto.

Estilo: paleta basada en AZUL (la máquina productiva en azules/teal; los lastres
—participación, PTF, cuña— en acentos cálidos para que resalten). Layout
determinista: banda inferior reservada para leyenda y fuente, sin solapes.
Etiquetado disciplinado (DESIGN §6/§7): 1996-2019 = 23 años; 2020-21 marcado COVID
(+ artefacto del deflactor); Domar ≠ "cambio estructural"; reconciliación visible.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data_loading import load_country
from decomposition import decompose, COMPONENT_LABELS, COMPONENT_KEYS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

PERIOD = (1996, 2019)
SOURCE = ("Fuente: EUKLEMS & INTANProd 2024 (LLEE), IPC/CNE (INE). Elaboración propia. Salario real = "
          "compensación laboral por hora deflactada por el deflactor del consumo de los hogares (CNE).")

# Etapas (DESIGN §6). La de COVID es solo descriptiva.
STAGES = [
    ("1996-2007", "Expansión\n(ladrillo)", range(1996, 2008), False),
    ("2008-2013", "Crisis y\ndevaluación interna", range(2008, 2014), False),
    ("2014-2019", "Recuperación", range(2014, 2020), False),
    ("2020-2021", "COVID\n(descriptivo)", range(2020, 2022), True),
]

# Paleta basada en AZUL: la máquina productiva (capital, composición, reasignación,
# Domar) en azules y teales; los lastres (participación del trabajo, PTF, cuña) en
# acentos cálidos/neutros para que resalten sobre el azul. Reconciliación en gris.
AZUL_PALIDO, AZUL_CLARO, AZUL, AZUL_MARINO = "#AED6F1", "#7FB3D5", "#2E86C1", "#1B4F72"
NAVY = "#154360"
COLORS = {
    "c_labshare":     "#5D6D7E",   # azul-pizarra (lastre)
    "comp_lab":       AZUL_PALIDO,
    "cap_tic":        AZUL_CLARO,
    "cap_notic":      AZUL,
    "cap_intang":     AZUL_MARINO,
    "ptf":            "#A93226",    # ladrillo: el protagonista negativo, resalta
    "reallocation":   "#5DADE2",    # azul (horas)
    "domar":          "#16A085",    # teal (Domar)
    "reconciliation": "#D5DBDB",    # gris claro (casi cero)
    "c_wedge":        "#E5A823",    # ámbar (lastre de precios)
}
TOTAL_C = NAVY

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#777777", "axes.titlesize": 13.5, "axes.titleweight": "bold",
    "axes.titlecolor": NAVY, "figure.dpi": 130,
})


def _finish(fig, name, *, legend_ax=None, ncol=5, footnote="", bottom=0.30,
            top=0.90, left=0.075, legend_y=0.115, foot_y=0.022, foot_size=7.6):
    """Layout determinista: reserva banda inferior, coloca leyenda y fuente sin
    solapes. NO usa bbox_inches='tight' (respeta los márgenes reservados)."""
    fig.subplots_adjust(left=left, right=0.965, top=top, bottom=bottom, wspace=0.22)
    if legend_ax is not None:
        h, l = legend_ax.get_legend_handles_labels()
        fig.legend(h, l, ncol=ncol, fontsize=8.6, loc="lower center",
                   bbox_to_anchor=(0.5, legend_y), frameon=False)
    txt = SOURCE + (("  " + footnote) if footnote else "")
    fig.text(0.075, foot_y, txt, fontsize=foot_size, color="#777777", wrap=True)
    fig.savefig(os.path.join(OUT, name), dpi=150)
    plt.close(fig)


def _grid(ax):
    ax.grid(axis="y", color="#ECEFF1", lw=0.9, zorder=0)
    ax.set_axisbelow(True)


def _stage_table(annual):
    rows = []
    for code, name, yr, covid in STAGES:
        yrs = [y for y in yr]
        block = annual.loc[yrs]
        rec = {"etapa": code, "nombre": name.replace("\n", " "), "años": len(yrs), "covid": covid}
        for k in COMPONENT_KEYS:
            rec[k] = block[k].mean()
        rec["g_real"] = block["g_real"].mean()
        rec["g_real_acum"] = block["g_real"].sum()
        rows.append(rec)
    return pd.DataFrame(rows).set_index("etapa")


def _stacked(ax, df, xlabels, total, keys, title, ylab, xrot=0, bar_w=0.8, covid_mask=None):
    x = np.arange(len(df))
    pos = np.zeros(len(df)); neg = np.zeros(len(df))
    for k in keys:
        v = df[k].values
        base = np.where(v >= 0, pos, neg)
        ax.bar(x, v, bottom=base, width=bar_w, color=COLORS[k], edgecolor="white",
               linewidth=0.35, label=COMPONENT_LABELS[k], zorder=2)
        pos = pos + np.where(v >= 0, v, 0)
        neg = neg + np.where(v < 0, v, 0)
    if covid_mask is not None:
        for i, c in enumerate(covid_mask):
            if c:
                ax.axvspan(i - 0.5, i + 0.5, color="#EBF1F5", zorder=0)
    ax.plot(x, total, "o-", color=TOTAL_C, lw=1.9, ms=4.2, label="Salario real (total)",
            zorder=4, mfc="white", mec=TOTAL_C, mew=1.2)
    ax.axhline(0, color="#2C3E50", lw=1.0, zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(xlabels, rotation=xrot,
                                         ha="center" if xrot == 0 else "right")
    ax.set_title(title, loc="left", pad=12)
    ax.set_ylabel(ylab)
    _grid(ax)


# ---------------------------------------------------------------------------
def fig_anual(annual):
    fig, ax = plt.subplots(figsize=(13.5, 7.4))
    yrs = list(annual.index)
    covid = [y >= 2020 for y in yrs]
    _stacked(ax, annual, [str(y) for y in yrs], annual["g_real"].values, COMPONENT_KEYS,
             "Descomposición del crecimiento anual del salario real por hora. España, 1996-2021",
             "Contribución (puntos porcentuales)", xrot=90, bar_w=0.82, covid_mask=covid)
    ax.text(len(yrs) - 1.5, ax.get_ylim()[1] * 0.92, "COVID", fontsize=8.5,
            color="#943126", ha="center", va="top", style="italic")
    _finish(fig, "g1_descomposicion_anual.png", legend_ax=ax, ncol=5, bottom=0.30,
            legend_y=0.115, foot_y=0.02,
            footnote="Franja gris = 2020-21 (COVID), solo descriptivo.")


def fig_etapas(stages):
    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    xlabels = [f"{c}\n{stages.loc[c, 'nombre']}" for c in stages.index]
    covid = list(stages["covid"].values)
    _stacked(ax, stages, xlabels, stages["g_real"].values, COMPONENT_KEYS,
             "Contribuciones medias anuales por grandes etapas. España",
             "Contribución media (p.p. por año)", xrot=0, bar_w=0.66, covid_mask=covid)
    _finish(fig, "g2_descomposicion_etapas.png", legend_ax=ax, ncol=5, bottom=0.30,
            legend_y=0.115, foot_y=0.02,
            footnote="Media anualizada; punto = crecimiento medio anual del salario real.")


def fig_waterfall(acc):
    fig, ax = plt.subplots(figsize=(12.5, 7.4))
    keys = COMPONENT_KEYS
    base = 0.0
    for i, k in enumerate(keys):
        v = acc[k]
        ax.bar(i, v, bottom=base, width=0.72, color=COLORS[k], edgecolor="white", zorder=2)
        if i < len(keys) - 1:
            ax.plot([i + 0.36, i + 0.64], [base + v, base + v], color="#B0B6BA", lw=0.8, zorder=1)
        ax.annotate(f"{v:+.1f}", (i, base + v + (0.22 if v >= 0 else -0.22)),
                    ha="center", va="bottom" if v >= 0 else "top", fontsize=8.6, color="#2C3E50")
        base += v
    ax.bar(len(keys), base, width=0.72, color=NAVY, edgecolor="white", zorder=2)
    ax.annotate(f"{base:+.1f}", (len(keys), base + 0.22), ha="center", fontsize=9.5,
                fontweight="bold", color=NAVY)
    ax.axhline(0, color="#2C3E50", lw=1.0)
    labels = [COMPONENT_LABELS[k] for k in keys] + ["Salario real\n(total)"]
    ax.set_xticks(range(len(keys) + 1))
    ax.set_xticklabels(labels, rotation=38, ha="right", fontsize=8.6)
    ax.set_ylabel("Contribución acumulada (p.p.)")
    ax.set_title("Anatomía del salario real por hora. España, acumulado 1996-2019 (23 años)",
                 loc="left", pad=12)
    _grid(ax)
    _finish(fig, "g3_anatomia_acumulada.png", bottom=0.30, foot_y=0.02,
            footnote="La PTF (residuo de Solow) señala dónde cavar, no qué hay enterrado (ver README, capa de honestidad).")


def fig_between(acc):
    realloc, dom, recon = acc["reallocation"], acc["domar"], acc["reconciliation"]
    old_between = realloc + dom + recon
    fig, ax = plt.subplots(figsize=(9.5, 7.0))
    ax.set_ylim(top=old_between * 1.22)
    ax.bar(0, old_between, width=0.5, color="#AAB7B8", edgecolor="white", zorder=2)
    ax.annotate(f"'Reasignación sectorial'\n(cajón) = {old_between:+.2f}", (0, old_between / 2),
                ha="center", va="center", fontsize=9.5, color="white", fontweight="bold")
    base = 0.0
    for k, v in [("reallocation", realloc), ("domar", dom), ("reconciliation", recon)]:
        ax.bar(1, v, bottom=base, width=0.5, color=COLORS[k], edgecolor="white", zorder=2,
               label=COMPONENT_LABELS[k])
        ax.annotate(f"{v:+.2f}", (1, base + v / 2), ha="center", va="center", fontsize=9.5,
                    color="white" if k != "reconciliation" else "#566573", fontweight="bold")
        base += v
    ax.axhline(0, color="#2C3E50", lw=1.0)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Proyecto viejo\n(un residuo sin abrir)", "Este proyecto\n(dos canales + residuo)"])
    ax.set_ylabel("Contribución acumulada 1996-2019 (p.p.)")
    ax.set_title("Abrir el 'between': el grueso NO es reasignación de horas", loc="left", pad=12)
    ax.legend(fontsize=9, loc="upper right", frameon=False)
    _grid(ax)
    _finish(fig, "g4_apertura_between.png", bottom=0.18, foot_y=0.03,
            footnote="Reasignación (horas) = a dónde van las horas; Domar = qué ramas crecen en output. No son lo mismo.")


def fig_termometro(ptf_vals):
    labels = ["LP2 (por persona)\nproyecto viejo:\nunidades mezcladas",
              "LP1 (por hora)\nsin renorm", "LP1 + renorm INV-3\n(CERTIFICADO)"]
    colors = ["#AAB7B8", "#5DADE2", NAVY]            # gris (mal) -> azul -> navy (certificado)
    fig, ax = plt.subplots(figsize=(10, 7.0))
    ax.bar(range(3), ptf_vals, width=0.6, color=colors, edgecolor="white", zorder=2)
    for i, v in enumerate(ptf_vals):
        ax.annotate(f"{v:.2f}", (i, v + 0.45), ha="center", va="bottom", fontsize=12,
                    fontweight="bold", color="white")
    ax.axhline(0, color="#2C3E50", lw=1.0)
    ax.set_ylim(min(ptf_vals) * 1.12, 1.2)
    ax.set_xticks(range(3)); ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("PTF intrasectorial acumulada (p.p.)")
    ax.set_title("Termómetro de la PTF: la cifra depende de hacer bien las unidades", loc="left", pad=12)
    d1, d2 = ptf_vals[1] - ptf_vals[0], ptf_vals[2] - ptf_vals[1]
    ax.annotate(f"corrige unidades\n{d1:+.1f} p.p.", (0.5, -3.1), ha="center", fontsize=9,
                color="#2C3E50", fontweight="bold")
    ax.annotate(f"renorm cobertura\n{d2:+.1f} p.p.", (1.5, -3.1), ha="center", fontsize=9,
                color="#2C3E50", fontweight="bold")
    for x0, x1 in [(0.08, 0.92), (1.08, 1.92)]:
        ax.annotate("", xy=(x1, -4.1), xytext=(x0, -4.1),
                    arrowprops=dict(arrowstyle="->", color="#5D6D7E", lw=1.3))
    _grid(ax)
    _finish(fig, "g5_termometro_ptf.png", bottom=0.16, foot_y=0.03,
            footnote="El −12,3 del proyecto viejo mezclaba identidad por hora con contribuciones por persona; "
                     "la corrección de unidades es la grande, la renorm el ajuste fino.")


def fig_deflactor(res_cne, res_ipc):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.4))
    band = res_cne.accumulated["g_real"] - res_ipc.accumulated["g_real"]
    for ax, (title, key) in zip(axes, [("Salario real (total)", "g_real"), ("Cuña de precios", "c_wedge")]):
        cne, ipc = res_cne.accumulated[key], res_ipc.accumulated[key]
        ax.bar([0, 1], [cne, ipc], width=0.55, color=[NAVY, AZUL_CLARO], edgecolor="white", zorder=2)
        for i, v in enumerate([cne, ipc]):
            ax.annotate(f"{v:+.2f}", (i, v + (0.07 if v >= 0 else -0.07)),
                        ha="center", va="bottom" if v >= 0 else "top", fontsize=11, fontweight="bold")
        ax.axhline(0, color="#2C3E50", lw=1.0)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["CNE P.31\n(default)", "IPC"])
        ax.set_title(f"{title}  ·  acumulado 1996-2019 (p.p.)", loc="left", fontsize=12, pad=10)
        _grid(ax)
    fig.suptitle(f"Banda de sensibilidad al deflactor del consumo  (diferencia ≈ {band:+.2f} p.p.)",
                 x=0.075, ha="left", fontweight="bold", fontsize=13.5, color=NAVY, y=0.97)
    _finish(fig, "g6_banda_deflactor.png", bottom=0.17, top=0.85, foot_y=0.03,
            footnote="Default = deflactor CNE de los hogares (coherente con el marco). IPC, mostrado como banda, no como cifra única.")


def fig_cobertura(cd):
    fig, ax = plt.subplots(figsize=(12, 6.2))
    yrs = cd.dyears
    ax.fill_between(yrs, cd.contrib_coverage.values * 100, 100, color="#FCF3CF", zorder=1,
                    label="Horas sin desglose (imputadas al within vía renorm)")
    ax.plot(yrs, cd.hours_coverage.values * 100, "o-", color=AZUL_MARINO, lw=1.8, ms=3.8,
            label="Cobertura EN HORAS (partición MECE = 100%)")
    ax.plot(yrs, cd.contrib_coverage.values * 100, "s-", color="#E5A823", lw=1.8, ms=3.8,
            label="Cobertura DE CONTRIBUCIONES (ramas con desglose)")
    ax.set_ylim(90, 100.6)
    ax.set_ylabel("% de horas totales")
    ax.set_title("Cobertura del desglose (INV-3): cubrir horas no es cubrir contribuciones",
                 loc="left", pad=12)
    ax.legend(fontsize=9, loc="lower center", frameon=False)
    _grid(ax)
    _finish(fig, "g7_cobertura_contribuciones.png", bottom=0.16, foot_y=0.03,
            footnote="Sin desglose: C20, C21, C26, C27, T, U (+ C19 parcial). ~4,2% de horas; "
                     "la renorm las imputa a la media (sesgo conocido hacia PTF más negativa).")


def fig_ranking(acc):
    """Barras horizontales ordenadas: ranking de magnitudes (formato del proyecto
    viejo, pero con datos certificados y etiquetas honestas). Complementa al
    waterfall: éste muestra el RANKING; el waterfall, el camino acumulativo."""
    items = sorted(((k, acc[k]) for k in COMPONENT_KEYS), key=lambda kv: kv[1])
    keys = [k for k, _ in items]
    vals = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(12, 7.2))
    y = np.arange(len(keys))
    ax.barh(y, vals, color=[COLORS[k] for k in keys], edgecolor="white", height=0.7, zorder=2)
    # total como barra destacada, separada arriba
    yt = len(keys) + 0.6
    ax.barh(yt, acc["g_real"], color=NAVY, edgecolor="white", height=0.7, zorder=2)
    for yi, v in list(zip(y, vals)) + [(yt, acc["g_real"])]:
        ax.annotate(f"{v:+.1f}", (v + (0.15 if v >= 0 else -0.15), yi),
                    va="center", ha="left" if v >= 0 else "right",
                    fontsize=9, fontweight="bold", color="#2C3E50")
    ax.axvline(0, color="#2C3E50", lw=1.0, zorder=3)
    ax.set_yticks(list(y) + [yt])
    ax.set_yticklabels([COMPONENT_LABELS[k] for k in keys] + ["SALARIO REAL (total)"], fontsize=9.5)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.set_xlabel("Contribución acumulada 1996-2019 (p.p.)")
    ax.set_title("Salario real por hora: qué pesa más. España, acumulado 1996-2019 (23 años)",
                 loc="left", pad=12)
    ax.grid(axis="x", color="#ECEFF1", lw=0.9, zorder=0); ax.set_axisbelow(True)
    ax.margins(x=0.12)
    _finish(fig, "g9_ranking_acumulado.png", bottom=0.13, top=0.91, left=0.30, foot_y=0.02,
            footnote="PTF = residuo de Solow, NO 'eficiencia'. El antiguo 'reasignación sectorial' está "
                     "abierto en Reasignación (horas) + Domar + Reconciliación (ver g4).")


def fig_ptf_trayectoria(annual):
    fig, ax = plt.subplots(figsize=(12, 6.4))
    yrs = list(annual.index)
    ax.bar(yrs, annual["ptf"].values, width=0.72, color="#A93226", edgecolor="white",
           zorder=2, label="PTF, contribución anual (p.p.)")
    ax2 = ax.twinx()
    ax2.plot(yrs, annual["ptf"].cumsum().values, "o-", color=NAVY, lw=1.9, ms=3.8,
             label="PTF acumulada (eje dcho.)", mfc="white", mec=NAVY, mew=1.2)
    ax2.axhline(0, color="#B0B6BA", lw=0.7)
    ax.axhline(0, color="#2C3E50", lw=1.0, zorder=3)
    for y in (2020, 2021):
        ax.axvspan(y - 0.5, y + 0.5, color="#EBF1F5", zorder=0)
    ax.set_ylabel("Contribución anual (p.p.)"); ax2.set_ylabel("Acumulada (p.p.)")
    ax.set_title("La PTF intrasectorial: el cuello de botella contable. España", loc="left", pad=12)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=9, loc="lower left", frameon=False)
    _grid(ax)
    _finish(fig, "g8_ptf_trayectoria.png", bottom=0.14, foot_y=0.03,
            footnote="PTF = residuo de Solow: NO es 'eficiencia'; cabe dentro mala asignación, márgenes, utilización, intangibles.")


# ---------------------------------------------------------------------------
def main():
    print("== Driver: Espana, modo certificado (cne_p31, renorm, per_hour) ==\n")
    cd = load_country("ES", DATA)
    res = decompose(cd, deflator="cne_p31", renorm=True, period=PERIOD)
    res_ipc = decompose(cd, deflator="ipc", renorm=True, period=PERIOD)
    res_bug = decompose(cd, deflator="cne_p31", renorm=False, period=PERIOD)
    # LP2 SOLO para el termómetro: renorm=False = config exacta del proyecto viejo
    # (familia por persona + NaN→between), da su −12,30 histórico sin disparar INV-4.
    cd_lp2 = load_country("ES", DATA, force_family="LP2")
    res_lp2 = decompose(cd_lp2, deflator="cne_p31", renorm=False, period=PERIOD)

    annual = res.annual
    stages = _stage_table(annual)

    cols = COMPONENT_KEYS + ["g_real"]
    annual[cols].rename(columns=COMPONENT_LABELS).round(4).to_csv(
        os.path.join(OUT, "datos_anual.csv"), encoding="utf-8-sig")
    pd.DataFrame({"cne_p31 (default)": res.accumulated[cols], "ipc": res_ipc.accumulated[cols]}
                 ).rename(index=COMPONENT_LABELS).round(4).to_csv(
        os.path.join(OUT, "datos_acumulado_1996_2019.csv"), encoding="utf-8-sig")
    stages.rename(columns=COMPONENT_LABELS).round(4).to_csv(
        os.path.join(OUT, "datos_etapas.csv"), encoding="utf-8-sig")

    fig_anual(annual)
    fig_etapas(stages)
    fig_waterfall(res.accumulated)
    fig_between(res.accumulated)
    fig_termometro([res_lp2.accumulated["ptf"], res_bug.accumulated["ptf"], res.accumulated["ptf"]])
    fig_deflactor(res, res_ipc)
    fig_cobertura(cd)
    fig_ranking(res.accumulated)
    fig_ptf_trayectoria(annual)

    print(f"familia LP autoseleccionada (INV-1): {res.lp_family}")
    print(f"cierre identidad (INV-2): {res.closure_resid:.1e} p.p. | "
          f"reconciliacion (INV-4): {res.reconciliation_acc:+.3f} p.p.\n")
    print("Contribucion acumulada 1996-2019 (23 anios), p.p.  [default cne_p31]:")
    for k in cols:
        print(f"  {COMPONENT_LABELS.get(k, 'Salario real (total)'):46s} {res.accumulated[k]:8.3f}")
    print(f"\nApertura del viejo 'between' = {res.accumulated['reallocation']:.2f} (horas) "
          f"+ {res.accumulated['domar']:.2f} (Domar) + {res.accumulated['reconciliation']:.2f} (recon)")
    print(f"Termometro PTF: LP2={res_lp2.accumulated['ptf']:.2f} | "
          f"LP1 sin renorm={res_bug.accumulated['ptf']:.2f} | "
          f"LP1 renorm (cert)={res.accumulated['ptf']:.2f}")
    print(f"Banda deflactor salario real: cne_p31={res.accumulated['g_real']:.2f} | "
          f"ipc={res_ipc.accumulated['g_real']:.2f}")
    print("\nEscritos en output/: 3 CSV + 9 PNG.")


if __name__ == "__main__":
    main()
