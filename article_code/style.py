"""Style graphique commun (palette catégorielle validée, ordre fixe par actif)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ASSETS = ["CAC", "SPX", "OATFR", "UST", "TTE", "LVMH", "RE", "PE"]
LABEL = {"CAC": "ETF CAC 40", "SPX": "ETF S&P 500", "OATFR": "OAT 10 ans (France)",
         "UST": "Treasury 10 ans (États-Unis)", "TTE": "Obligation TotalEnergies 10 ans",
         "LVMH": "Obligation LVMH 10 ans", "RE": "Immeuble de bureaux", "PE": "Private Equity small caps"}
SHORT = {"CAC": "ETF CAC 40", "SPX": "ETF S&P 500", "OATFR": "OAT FR 10a", "UST": "UST 10a",
         "TTE": "TotalEnergies 10a", "LVMH": "LVMH 10a", "RE": "Bureaux", "PE": "PE small caps"}
COLOR = {"CAC": "#2a78d6", "SPX": "#eb6834", "OATFR": "#1baf7a", "UST": "#eda100",
         "TTE": "#e87ba4", "LVMH": "#008300", "RE": "#4a3aa7", "PE": "#e34948"}
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "legend.fontsize": 8,
    "lines.linewidth": 1.4, "figure.dpi": 110, "savefig.dpi": 220, "savefig.bbox": "tight",
    "axes.titleweight": "bold", "axes.titlelocation": "left", "text.color": INK,
})


def shade_stress(ax, stress_series, thr=0.35):
    """Grise les épisodes de stress (sans couleur de statut)."""
    m = stress_series > thr
    starts = m & ~m.shift(1, fill_value=False)
    ends = m & ~m.shift(-1, fill_value=False)
    for a, b in zip(stress_series.index[starts], stress_series.index[ends]):
        ax.axvspan(a, b, color="#d9d8d3", alpha=0.55, lw=0, zorder=0)
