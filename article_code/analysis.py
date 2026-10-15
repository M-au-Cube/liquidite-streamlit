"""
Analyse de la liquidité : indicateurs paramétriques et non paramétriques,
surfaces ΔPTV_α, liquidité juridique (temps minimal), indicateur synthétique.
Sorties : figs/*.png, results/results.json
"""
import json, os
import numpy as np
import pandas as pd
from scipy import stats, optimize
from style import plt, ASSETS, LABEL, SHORT, COLOR, INK, INK2, MUTED, GRID, shade_stress

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data"); FIG = os.path.join(HERE, "..", "figs"); RES = os.path.join(HERE, "..", "results")
os.makedirs(FIG, exist_ok=True); os.makedirs(RES, exist_ok=True)
rng = np.random.default_rng(7)
P = json.load(open(os.path.join(DATA, "params.json")))
d = pd.read_csv(os.path.join(DATA, "listed_daily.csv"), index_col=0, parse_dates=True)
mo = pd.read_csv(os.path.join(DATA, "metaorders.csv"), parse_dates=["date"])
bt = pd.read_csv(os.path.join(DATA, "bond_trades.csv"), parse_dates=["date"])
reQ = pd.read_csv(os.path.join(DATA, "re_quarterly.csv"), index_col=0, parse_dates=True)
peQ = pd.read_csv(os.path.join(DATA, "pe_quarterly.csv"), index_col=0, parse_dates=True)
deals = {"RE": pd.read_csv(os.path.join(DATA, "re_deals.csv"), parse_dates=["date"]),
         "PE": pd.read_csv(os.path.join(DATA, "pe_deals.csv"), parse_dates=["date"])}
LISTED = ["CAC", "SPX", "OATFR", "UST", "TTE", "LVMH"]
R = {"listed": {}, "unlisted": {}, "synthetic": {}, "meta": {}}
TD = 252 / 365          # jours de bourse par jour calendaire
QSTAR = 10e6            # taille de référence : 10 M€
ALPHA = 0.995
RHO_MAX = {"CAC": 0.25, "SPX": 0.25, "OATFR": 1.0, "UST": 1.0, "TTE": 1.0, "LVMH": 1.0}  # participation max. (carnet : 25 % ; OTC : bloc négocié)
FEES = P["fees_bp"]
T_LEG = {"CAC": 2, "SPX": 2, "OATFR": 2, "UST": 1, "TTE": 2, "LVMH": 2, "RE": 90, "PE": 120}  # jours
SETTLE_TXT = {"CAC": "T+2 (CSDR)", "SPX": "T+2 (CSDR)", "OATFR": "T+2 (Euroclear)", "UST": "T+1 (Fedwire)",
              "TTE": "T+2 (Euroclear)", "LVMH": "T+2 (Euroclear)", "RE": "≈ 3 mois (DPU, acte notarié)",
              "PE": "≈ 4 mois (agrément, préemption)"}

def savefig(fig, name):
    fig.savefig(os.path.join(FIG, name + ".png")); plt.close(fig)

# ===========================================================================
# 0. Figures descriptives des données générées
# ===========================================================================
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.4))
for ax, group, ttl in [(axs[0], ["CAC", "SPX"], "a) ETF actions (base 100)"),
                       (axs[1], ["OATFR", "UST", "TTE", "LVMH"], "b) Obligations 10 ans, maturité constante (base 100)")]:
    shade_stress(ax, d["stress"])
    for k in group:
        ax.plot(d.index, 100 * d[f"{k}_price"] / d[f"{k}_price"].iloc[0], color=COLOR[k], label=SHORT[k], lw=1.1)
    ax.set_title(ttl); ax.legend(loc="upper left", ncol=2)
savefig(fig, "f01_prix_cotes")

fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.2))
shade_stress(axs[0], d["stress"]); shade_stress(axs[1], d["stress"])
axs[0].plot(d.index, 100 * d["OATFR_yield"], color=COLOR["OATFR"], label="OAT 10 ans")
axs[0].plot(d.index, 100 * d["UST_yield"], color=COLOR["UST"], label="Treasury 10 ans")
axs[0].set_title("a) Taux souverains 10 ans (%)"); axs[0].legend(loc="upper left")
axs[1].plot(d.index, 1e4 * d["TTE_credit_spread"], color=COLOR["TTE"], label="TotalEnergies")
axs[1].plot(d.index, 1e4 * d["LVMH_credit_spread"], color=COLOR["LVMH"], label="LVMH")
axs[1].set_title("b) Spreads de crédit contre OAT (pb)"); axs[1].legend(loc="upper left")
savefig(fig, "f02_taux_spreads")

fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.2))
axs[0].plot(reQ.index, reQ["true_value"] / 1e6, color=COLOR["RE"], lw=1.0, ls="--", label="Valeur « vraie » (latente)")
axs[0].plot(reQ.index, reQ["appraisal"] / 1e6, color=COLOR["RE"], lw=1.8, label="Valeur d'expertise (lissée)")
axs[0].set_title("a) Immeuble de bureaux (M€)"); axs[0].legend(loc="lower left")
axs[1].plot(peQ.index, peQ["true_value"] / 1e6, color=COLOR["PE"], lw=1.0, ls="--", label="Valeur « vraie » (latente)")
axs[1].plot(peQ.index, peQ["nav"] / 1e6, color=COLOR["PE"], lw=1.8, label="NAV publiée (lissée)")
axs[1].set_title("b) Private Equity small caps (M€)"); axs[1].legend(loc="upper left")
savefig(fig, "f03_non_cotes")

fig, ax = plt.subplots(figsize=(9.6, 3.3))
shade_stress(ax, d["stress"])
for k in LISTED:
    ax.plot(d.index, 1e4 * d[f"{k}_spread"].rolling(10).median(), color=COLOR[k], lw=1.0, label=SHORT[k])
ax.set_yscale("log"); ax.set_ylabel("fourchette relative (pb, échelle log)")
ax.set_title("Fourchettes affichées (médiane mobile 10 jours)"); ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.1))
savefig(fig, "f04_fourchettes")

# ===========================================================================
# 1. Actifs cotés : indicateurs non paramétriques
# ===========================================================================
def roll_spread(px):
    dp = np.diff(np.log(px))
    c = np.cov(dp[1:], dp[:-1])[0, 1]
    return 2 * np.sqrt(-c) if c < 0 else np.nan

for k in LISTED:
    r = d[f"{k}_ret"].values; V = d[f"{k}_volume"].values; s = d[f"{k}_spread"].values
    out = {}
    out["spread_med_bp"] = float(np.median(s) * 1e4)
    out["spread_q995_bp"] = float(np.quantile(s, ALPHA) * 1e4)
    out["amihud_bp_per_Meur"] = float(np.mean(np.abs(r) / (V / 1e6)) * 1e4)
    r20 = pd.Series(r).rolling(20).sum().values[19::20]
    out["MEC"] = float(np.var(r20, ddof=1) / (20 * np.var(r, ddof=1)))
    X = d[f"{k}_oi"].values / 1e6
    ols = stats.linregress(X, r)
    out["kyle_lambda_bp_per_Meur"] = float(ols.slope * 1e4); out["kyle_t"] = float(ols.slope / ols.stderr)
    out["adv_eur"] = float(np.median(V)); out["sigma_d_med"] = float(np.median(d[f"{k}_vol"]))
    out["sigma_ann"] = float(np.std(r) * np.sqrt(252))
    if k in ("TTE", "LVMH"):
        tr = bt[bt.asset == k]
        out["roll_bp"] = float(roll_spread(tr["price"].values) * 1e4)
        out["trades_per_day"] = float(tr.groupby("date").size().reindex(d.index, fill_value=0).mean())
    R["listed"][k] = out

# ===========================================================================
# 2. Actifs cotés : calibration paramétrique de la loi d'impact en racine carrée
#    ln(ΔP - f - s/2) = ln Y + ln σ_d + δ ln(Q / (V_d t)) + ε
# ===========================================================================
fig, axs = plt.subplots(1, 3, figsize=(9.6, 3.0), sharey=True)
for j, k in enumerate(LISTED):
    m = mo[mo.asset == k].copy()
    net = m["cost"] - FEES[k] * 1e-4 - m["spread"] / 2
    ok = net > 0
    y = np.log(net[ok] / m["sigma_d"][ok]); x = np.log(m["Q"][ok] / (m["V_d"][ok] * m["t_days"][ok]))
    fit = stats.linregress(x, y)
    resid = y - (fit.intercept + fit.slope * x)
    R["listed"][k].update(Y_hat=float(np.exp(fit.intercept)), delta_hat=float(fit.slope),
                          delta_se=float(fit.stderr), r2=float(fit.rvalue ** 2), resid_sd=float(resid.std()),
                          n_meta=int(ok.sum()))
    R["listed"][k]["_resid"] = resid.values.tolist()
    if k in ("CAC", "OATFR", "TTE"):
        ax = axs[["CAC", "OATFR", "TTE"].index(k)]
        ax.scatter(x, y, s=4, color=COLOR[k], alpha=0.25, lw=0)
        xx = np.linspace(x.min(), x.max(), 50)
        ax.plot(xx, fit.intercept + fit.slope * xx, color=INK, lw=1.6)
        ax.set_title(f"{SHORT[k]} : δ̂ = {fit.slope:.2f}, Ŷ = {np.exp(fit.intercept):.2f}", fontsize=9)
        ax.set_xlabel("ln(Q / (V·t))")
axs[0].set_ylabel("ln((ΔP − f − s/2) / σ_d)")
savefig(fig, "f05_calibration_impact")

Q_GRID = np.logspace(5, 8.7, 30)            # 100 k€ à 500 M€
T_GRID = np.logspace(np.log10(0.25), np.log10(90), 30)   # 6 h à 90 jours calendaires
M = 3000

def listed_cost_samples(k, Q, t_cal, mode="np", M=M, seed=None):
    """Échantillon de ΔP(Q,t) : mode 'np' (bootstrap historique) ou 'p' (log-normal multivarié).
    seed : nombres aléatoires communs (surfaces lisses en (Q,t))."""
    rng = np.random.default_rng(seed) if seed is not None else globals()["rng"]
    o = R["listed"][k]
    sig = d[f"{k}_vol"].values; V = d[f"{k}_volume"].values; s = d[f"{k}_spread"].values
    t = max(t_cal * TD, 1 / 8.5)
    if mode == "np":
        i = rng.integers(0, len(sig), M)
        sg, vv, ss = sig[i], V[i], s[i]
        e = rng.choice(np.array(o["_resid"]), M)
    else:
        Z = np.log(np.column_stack([sig, V, s]))
        mu, C = Z.mean(0), np.cov(Z.T)
        smp = np.exp(rng.multivariate_normal(mu, C, M))
        sg, vv, ss = smp[:, 0], smp[:, 1], smp[:, 2]
        e = rng.normal(0, o["resid_sd"], M)
    imp = o["Y_hat"] * sg * (Q / (vv * t)) ** o["delta_hat"] * np.exp(e)
    return FEES[k] * 1e-4 + ss / 2 + imp

for k in LISTED:
    surf = {}
    for mode in ("np", "p"):
        S50 = np.zeros((len(T_GRID), len(Q_GRID))); S995 = np.zeros_like(S50)
        for a, t in enumerate(T_GRID):
            for b, Q in enumerate(Q_GRID):
                x = listed_cost_samples(k, Q, t, mode, M=6000, seed=11)
                S50[a, b], S995[a, b] = np.quantile(x, 0.5), np.quantile(x, ALPHA)
        surf[mode] = (S50, S995)
    R["listed"][k]["_surf"] = surf
    # points de référence
    for mode in ("np", "p"):
        for t in (1, 20, 60):
            x = listed_cost_samples(k, QSTAR, t, mode, M=20000)
            R["listed"][k][f"dP_{mode}_t{t}_q50_bp"] = float(np.quantile(x, 0.5) * 1e4)
            R["listed"][k][f"dP_{mode}_t{t}_q995_bp"] = float(np.quantile(x, ALPHA) * 1e4)

# courbes ΔP(Q) à t = 1 jour et t = 20 jours (médiane, quantile 99,5 %)
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6), sharey=True)
for ax, ti, ttl in [(axs[0], 1, "a) Horizon t = 1 jour"), (axs[1], 20, "b) Horizon t = 20 jours")]:
    a = np.argmin(np.abs(T_GRID - ti))
    for k in LISTED:
        S50, S995 = R["listed"][k]["_surf"]["np"]
        ax.plot(Q_GRID / 1e6, 1e4 * S50[a], color=COLOR[k], lw=1.6, label=SHORT[k])
        ax.plot(Q_GRID / 1e6, 1e4 * S995[a], color=COLOR[k], lw=1.0, ls="--")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(ttl); ax.set_xlabel("Quantité vendue Q (M€)")
axs[0].set_ylabel("ΔP (pb) — trait plein : médiane ; tirets : q99,5 %")
axs[1].legend(loc="upper left", ncol=2)
savefig(fig, "f06_cout_quantite")

# surface 3D ΔPTV pour l'ETF CAC 40 et l'obligation TotalEnergies
from mpl_toolkits.mplot3d import Axes3D  # noqa
fig = plt.figure(figsize=(9.6, 4.2))
for j, k in enumerate(["CAC", "TTE"]):
    ax = fig.add_subplot(1, 2, j + 1, projection="3d")
    S50, S995 = R["listed"][k]["_surf"]["np"]
    XX, YY = np.meshgrid(np.log10(Q_GRID), np.log10(T_GRID))
    ax.plot_surface(XX, YY, np.log10(1e4 * S50), color=COLOR[k], alpha=0.9, lw=0, shade=True)
    ax.plot_wireframe(XX, YY, np.log10(1e4 * S995), color=INK2, lw=0.5, rstride=2, cstride=2)
    ax.set_xlabel("log10 Q (€)"); ax.set_ylabel("log10 t (jours)"); ax.set_zlabel("log10 ΔP (pb)")
    ax.set_title(f"{'ab'[j]}) {SHORT[k]} : médiane (surface) et q99,5 % (grille)", fontsize=9)
    ax.view_init(22, -125)
savefig(fig, "f07_surface_dptv")

# ===========================================================================
# 3. Actifs non cotés : modèle d'enchère poissonnienne (paramétrique) et
#    estimateurs non paramétriques (Kaplan-Meier, quantiles à noyau)
# ===========================================================================
def is_stress(date, kind):
    y = date.year + (date.month - 1) / 12
    if kind == "RE":
        return (2020.2 <= y < 2020.6) or (y >= 2022.5 and y < 2025.0)
    return (2020.2 <= y < 2020.75) or (2022.3 <= y < 2024.0)

def fit_auction(df):
    """MLE : nu (Poisson) puis (mu_b, sig_b) à partir de la loi du maximum de n log-normales."""
    nu = df["n_bids"].sum() / df["marketing_days"].sum()
    sold = df[df.censored == 0]
    x = np.log(sold["price_to_value"].values); n = sold["n_bids"].values
    def nll(th):
        mu, ls = th; sg = np.exp(ls); z = (x - mu) / sg
        return -np.sum(np.log(n) + stats.norm.logpdf(z) + (n - 1) * stats.norm.logcdf(z) - np.log(sg))
    res = optimize.minimize(nll, [x.mean() - 0.1, np.log(0.1)], method="Nelder-Mead")
    Hm = np.zeros((2, 2))
    for i in range(2):
        Hm[i] = optimize.approx_fprime(res.x, lambda th: optimize.approx_fprime(th, nll, 1e-5)[i], 1e-5)
    se = np.sqrt(np.diag(np.linalg.inv(Hm)))
    nu_se = np.sqrt(df["n_bids"].sum()) / df["marketing_days"].sum()
    return dict(nu=nu, nu_se=nu_se, mu_b=res.x[0], mu_se=se[0], sig_b=np.exp(res.x[1]), sig_se=se[1] * np.exp(res.x[1]),
                n=len(df), n_sold=len(sold))

def auction_quantile(q, Lam, mu, sg):
    """Quantile q du rapport prix/valeur = max de N~Poisson(Lam) offres, conditionnel à N ≥ 1."""
    e = np.exp(-Lam)
    tgt = e + q * (1 - e)                         # P(max ≤ x) non conditionnel
    # exp(-Lam (1 - F(x))) = tgt  =>  F(x) = 1 + ln(tgt)/Lam
    Fx = 1 + np.log(tgt) / Lam
    Fx = np.clip(Fx, 1e-12, 1 - 1e-12)
    return np.exp(mu + sg * stats.norm.ppf(Fx))

def kaplan_meier(t, event):
    o = np.argsort(t); t, event = t[o], event[o]
    uniq = np.unique(t[event == 1]); S = 1.0; out_t, out_s = [0], [1.0]
    for u in uniq:
        n_risk = np.sum(t >= u); dth = np.sum((t == u) & (event == 1))
        S *= 1 - dth / n_risk; out_t.append(u); out_s.append(S)
    return np.array(out_t), np.array(out_s)

def kernel_quantile(xg, x, y, q, h):
    out = []
    for x0 in xg:
        w = np.exp(-0.5 * ((x - x0) / h) ** 2); o = np.argsort(y)
        cw = np.cumsum(w[o]) / w.sum()
        out.append(y[o][np.searchsorted(cw, q)] if cw[-1] > 0 else np.nan)
    return np.array(out)

unl_t = np.linspace(0, 420, 300)
for kind in ("RE", "PE"):
    df = deals[kind].copy()
    df["stress"] = [is_stress(x, kind) for x in df["date"]]
    fn = fit_auction(df[~df.stress]); fs = fit_auction(df[df.stress])
    Tl = T_LEG[kind]
    o = dict(T_leg=Tl, normal=fn, stress=fs)
    # --- liquidité « physique » : délai minimal au seuil 99,5 % (1re offre reçue)
    o["t_first_med_normal"] = Tl + np.log(2) / fn["nu"]
    o["t_min995_normal"] = Tl + np.log(1 / (1 - ALPHA)) / fn["nu"]
    o["t_min995_stress"] = Tl + np.log(1 / (1 - ALPHA)) / fs["nu"]
    tKM, sKM = kaplan_meier(df["first_bid_days"].values, 1 - df["censored"].values)
    o["_km"] = (tKM.tolist(), sKM.tolist())
    o["km_median"] = float(Tl + tKM[np.argmax(sKM <= 0.5)]) if (sKM <= 0.5).any() else None
    o["km_q90"] = float(Tl + tKM[np.argmax(sKM <= 0.10)]) if (sKM <= 0.10).any() else None
    # --- liquidité financière : décote en fonction de t (paramétrique et non paramétrique)
    sold = df[df.censored == 0]
    for lab, f in (("normal", fn), ("stress", fs)):
        for t in (20, 60, 180, 365):
            m_ = max(t - Tl, 0.0) if t > Tl else 0.0
            Lam = f["nu"] * (t - Tl) if t > Tl else np.nan
            o[f"dP_{lab}_t{t}_q50"] = float(1 - auction_quantile(0.5, Lam, f["mu_b"], f["sig_b"])) if t > Tl else None
            o[f"dP_{lab}_t{t}_q995"] = float(1 - auction_quantile(1 - ALPHA, Lam, f["mu_b"], f["sig_b"])) if t > Tl else None
    o["dP_np_q50"] = float(sold["discount"].median()); o["dP_np_q995"] = float(sold["discount"].quantile(ALPHA))
    o["dP_np_q995_stress"] = float(sold[sold.stress]["discount"].quantile(ALPHA))
    o["dP_np_q50_stress"] = float(sold[sold.stress]["discount"].median())
    # bootstrap IC 90 % du quantile 99,5 % empirique
    bs = [np.quantile(rng.choice(sold["discount"].values, len(sold)), ALPHA) for _ in range(2000)]
    o["dP_np_q995_ci"] = [float(np.quantile(bs, 0.05)), float(np.quantile(bs, 0.95))]
    # --- volatilité de valeur : dé-lissage de Geltner (a = 1 - ρ1)
    ser = (reQ["appraisal"] if kind == "RE" else peQ["nav"])
    ro = np.log(ser).diff().dropna().values
    rho1 = np.corrcoef(ro[1:], ro[:-1])[0, 1]; a = 1 - rho1
    ru = (ro[1:] - rho1 * ro[:-1]) / a
    o.update(geltner_a_hat=float(a), sigma_obs_ann=float(ro.std() * 2), sigma_unsm_ann=float(ru.std() * 2))
    r4 = pd.Series(ro).rolling(4).sum().values[3::4]
    o["MEC"] = float(np.var(r4, ddof=1) / (4 * np.var(ro, ddof=1)))
    o["bids_per_week_normal"] = float(fn["nu"] * 7)
    R["unlisted"][kind] = o

# Figure : décote vs délai de commercialisation
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6), sharey=True)
for ax, kind in zip(axs, ("RE", "PE")):
    df = deals[kind]; sold = df[df.censored == 0]; o = R["unlisted"][kind]; Tl = o["T_leg"]
    st = np.array([is_stress(x, kind) for x in sold["date"]])
    ax.scatter(sold["t_total_days"][~st], 100 * sold["discount"][~st], s=7, color=COLOR[kind], alpha=0.35, lw=0, label="transactions (normal)")
    ax.scatter(sold["t_total_days"][st], 100 * sold["discount"][st], s=9, marker="^", color=INK2, alpha=0.45, lw=0, label="transactions (stress)")
    tt = np.linspace(Tl + 3, 420, 200)
    for lab, ls in (("normal", "-"), ("stress", "--")):
        f = o[lab]
        q50 = [1 - auction_quantile(0.5, f["nu"] * (t - Tl), f["mu_b"], f["sig_b"]) for t in tt]
        q995 = [1 - auction_quantile(1 - ALPHA, f["nu"] * (t - Tl), f["mu_b"], f["sig_b"]) for t in tt]
        ax.plot(tt, 100 * np.array(q50), color=INK, ls=ls, lw=1.6, label=f"médiane paramétrique ({lab})")
        ax.plot(tt, 100 * np.array(q995), color=COLOR[kind], ls=ls, lw=1.6, label=f"q99,5 % paramétrique ({lab})")
    lt = np.log(sold["t_total_days"].values)
    kq = kernel_quantile(np.log(tt), lt, sold["discount"].values, 0.5, 0.25)
    ax.plot(tt, 100 * kq, color=MUTED, lw=2.4, alpha=0.9, label="médiane à noyau (non param.)")
    ax.axvline(Tl, color=MUTED, lw=1, ls=":"); ax.text(Tl + 4, 2, "délai\njuridique", fontsize=7, color=INK2)
    ax.set_xlim(0, 420); ax.set_ylim(-15, 75); ax.set_xlabel("délai total de cession t (jours)")
    ax.set_title(f"{'ab'[['RE','PE'].index(kind)]}) {SHORT[kind]}")
axs[0].set_ylabel("décote ΔP (% de la valeur publiée)")
h_, l_ = axs[1].get_legend_handles_labels()
fig.legend(h_, l_, loc="lower center", ncol=4, fontsize=7, bbox_to_anchor=(0.5, -0.08))
savefig(fig, "f08_decote_delai")

# Figure : Kaplan-Meier (temps jusqu'à la 1re offre)
fig, ax = plt.subplots(figsize=(6.4, 3.3))
for kind in ("RE", "PE"):
    o = R["unlisted"][kind]; tKM, sKM = map(np.array, o["_km"])
    ax.step(o["T_leg"] + tKM, sKM, where="post", color=COLOR[kind], lw=1.8, label=f"{SHORT[kind]} : Kaplan-Meier")
    tt = np.linspace(0, 400, 200)
    ax.plot(o["T_leg"] + tt, np.exp(-o["normal"]["nu"] * tt), color=COLOR[kind], ls="--", lw=1.1, label=f"{SHORT[kind]} : exponentielle (ν̂ normal)")
ax.axhline(0.005, color=MUTED, ls=":", lw=1); ax.text(10, 0.03, "seuil 0,5 %", fontsize=7, color=INK2)
ax.set_xlabel("délai depuis la décision de vendre (jours)"); ax.set_ylabel("P(aucune offre reçue)")
ax.set_title("Survie du délai d'obtention d'une première offre"); ax.legend(fontsize=7); ax.set_xlim(0, 520)
savefig(fig, "f09_kaplan_meier")

# ===========================================================================
# 4. Combien d'acheteurs pour P(prix ≥ 90 % de la valeur) ≥ 90 % ?
#    P(max_{j≤N} X_j ≥ x) = 1 - F(x)^N  ⇒  N* = ⌈ ln(1-p) / ln F(x) ⌉
# ===========================================================================
Nmax = 40; Ns = np.arange(1, Nmax + 1)
fig, ax = plt.subplots(figsize=(6.4, 3.3))
R["meta"]["N_star"] = {}
for kind in ("RE", "PE"):
    for lab, ls in (("normal", "-"), ("stress", "--")):
        f = R["unlisted"][kind][lab]
        F = stats.norm.cdf((np.log(0.9) - f["mu_b"]) / f["sig_b"])
        pr = 1 - F ** Ns
        ax.plot(Ns, pr, color=COLOR[kind], ls=ls, lw=1.6, label=f"{SHORT[kind]} ({lab})")
        Nst = int(np.ceil(np.log(0.1) / np.log(F))) if F < 1 else None
        R["meta"]["N_star"][f"{kind}_{lab}"] = dict(F=float(F), N=Nst,
              days=float(stats.gamma.ppf(0.9, Nst, scale=1 / f["nu"])) if Nst else None)
for kind in LISTED:  # actifs cotés : dispersion des offres ≈ demi-fourchette
    s = R["listed"][kind]["spread_q995_bp"] * 1e-4
    R["meta"]["N_star"][kind] = dict(F=0.0, N=1, days=0.0)
ax.axhline(0.9, color=MUTED, ls=":", lw=1); ax.set_xlabel("nombre d'acheteurs potentiels N")
ax.set_ylabel("P(prix ≥ 90 % de la valeur)"); ax.set_ylim(0, 1.02)
ax.set_title("Profondeur de la demande et probabilité de bon prix"); ax.legend(fontsize=7, loc="lower right")
savefig(fig, "f10_nombre_acheteurs")

# ===========================================================================
# 5. Coût de liquidité vs incertitude de valeur (σ √t)
# ===========================================================================
fig, ax = plt.subplots(figsize=(6.6, 3.6))
hz = np.array([1, 5, 20, 60, 180, 365])
R["meta"]["ratio_liq_val"] = {}
for k in ASSETS:
    if k in LISTED:
        sig = R["listed"][k]["sigma_ann"]
        liq = np.array([np.quantile(listed_cost_samples(k, QSTAR, t, "np", 4000), 0.5) for t in hz])
    else:
        o = R["unlisted"][k]; sig = o["sigma_unsm_ann"]; f = o["normal"]
        liq = np.array([1 - auction_quantile(0.5, f["nu"] * (t - o["T_leg"]), f["mu_b"], f["sig_b"]) if t > o["T_leg"] else np.nan for t in hz])
    val = sig * np.sqrt(hz / 365)
    ratio = liq / val
    R["meta"]["ratio_liq_val"][k] = dict(zip([int(h) for h in hz], [None if np.isnan(v) else float(v) for v in ratio]))
    ax.plot(hz, ratio, marker="o", ms=4, color=COLOR[k], label=SHORT[k])
ax.set_xscale("log"); ax.set_yscale("log"); ax.axhline(1, color=MUTED, lw=1, ls=":")
ax.set_xlabel("horizon t (jours)"); ax.set_ylabel("ΔP_50(Q*=10 M€, t) / (σ √t)")
ax.set_title("Coût de liquidité rapporté à l'incertitude de valeur"); ax.legend(ncol=2, fontsize=7)
savefig(fig, "f11_liquidite_vs_valeur")

# ===========================================================================
# 6. Indicateurs I1 (juridique / physique), I2 (financier) et indicateur synthétique
# ===========================================================================
EPS = 1e-4; TMAX = 1095.0
def score_time(t): return float(np.clip(1 - np.log1p(t) / np.log1p(TMAX), 0, 1))
def score_cost(c): return float(np.clip(1 - np.log1p(c / EPS) / np.log1p(1 / EPS), 0, 1))

H_ALM = 30.0; R_EMERG = 0.08; PI_IMP = 0.02
syn = {}
for k in ASSETS:
    if k in LISTED:
        Vq = np.quantile(d[f"{k}_volume"].values, 1 - ALPHA)
        t_exec = QSTAR / (RHO_MAX[k] * Vq) / TD                       # jours calendaires
        tmin = T_LEG[k] + t_exec
        cost_tmin = float(np.quantile(listed_cost_samples(k, QSTAR, max(t_exec, 0.25), "np", 20000), ALPHA))
        cost_H = float(np.quantile(listed_cost_samples(k, QSTAR, max(H_ALM - T_LEG[k], 0.25), "np", 20000), ALPHA))
        cost50 = float(np.quantile(listed_cost_samples(k, QSTAR, max(t_exec, 0.25), "np", 20000), 0.5))
        obs = (R["listed"][k].get("trades_per_day") or (R["listed"][k]["adv_eur"] / 50e3 if k in ("CAC", "SPX") else 500.0))
    else:
        o = R["unlisted"][k]; fs, fn = o["stress"], o["normal"]
        tmin = o["t_min995_stress"]
        cost_tmin = float(1 - auction_quantile(1 - ALPHA, fs["nu"] * (tmin - o["T_leg"]), fs["mu_b"], fs["sig_b"]))
        cost50 = float(1 - auction_quantile(0.5, fn["nu"] * (o["t_min995_normal"] - o["T_leg"]), fn["mu_b"], fn["sig_b"]))
        cost_H = cost_tmin
        obs = fn["nu"]
    I1, I2 = score_time(tmin), score_cost(cost_tmin)
    # coût ALM de mobilisation de Q* à l'horizon H : prix + portage d'urgence + pénalité d'impasse
    if tmin <= H_ALM:
        c_alm = cost_H
    else:
        c_alm = cost_tmin + R_EMERG * (tmin - H_ALM) / 365 + PI_IMP
    syn[k] = dict(t_min=float(tmin), dP995=cost_tmin, dP50=cost50, I1=I1, I2=I2, C_alm=float(c_alm),
                  S_alm=score_cost(c_alm), obs_per_day=float(obs), T_leg=T_LEG[k], settle=SETTLE_TXT[k])

I1v = np.array([syn[k]["I1"] for k in ASSETS]); I2v = np.array([syn[k]["I2"] for k in ASSETS]); Sv = np.array([syn[k]["S_alm"] for k in ASSETS])
x_star = float(np.clip(np.dot(Sv - I2v, I1v - I2v) / np.dot(I1v - I2v, I1v - I2v), 0, 1))
xs = np.linspace(0, 1, 101)
sse = [np.sum((x * I1v + (1 - x) * I2v - Sv) ** 2) for x in xs]
# rang : corrélation de Spearman entre L(x) et S_ALM
spear = [stats.spearmanr(x * I1v + (1 - x) * I2v, Sv).correlation for x in xs]
R["meta"].update(x_star=x_star, sse_curve=list(map(float, sse)), spearman_curve=list(map(float, spear)),
                 H_ALM=H_ALM, R_EMERG=R_EMERG, PI_IMP=PI_IMP, QSTAR=QSTAR, RHO_MAX=RHO_MAX, EPS=EPS, TMAX=TMAX)

def letter_time(t):
    return "A" if t < 1 else "B" if t < 3 else "C" if t < 7 else "D" if t < 30 else "E" if t < 365 else "F"
def letter_obs(n):
    return "A" if n >= 100 else "B" if n >= 30 else "C" if n >= 5 else "D" if n >= 1 else "E" if n >= 1 / 7 else "F"
def letter_score(L):
    return "A" if L >= 0.80 else "B" if L >= 0.65 else "C" if L >= 0.50 else "D" if L >= 0.35 else "E" if L >= 0.20 else "F"
order = "ABCDEF"
for k in ASSETS:
    s = syn[k]; s["L"] = x_star * s["I1"] + (1 - x_star) * s["I2"]
    s["L50"] = 0.5 * s["I1"] + 0.5 * s["I2"]
    s["note_phys"] = letter_time(s["T_leg"]); s["note_eco"] = letter_obs(s["obs_per_day"])
    s["note_finale"] = max(s["note_phys"], s["note_eco"], key=order.index)
    s["note_L"] = letter_score(s["L"])
R["synthetic"] = syn

# figure : carte I1 / I2 avec iso-lignes de L(x*)
fig, ax = plt.subplots(figsize=(6.4, 4.4))
g = np.linspace(0, 1, 200); G1, G2 = np.meshgrid(g, g)
cs = ax.contour(G1, G2, x_star * G1 + (1 - x_star) * G2, levels=[0.25, 0.4, 0.55, 0.7, 0.85], colors=MUTED, linewidths=0.8)
ax.clabel(cs, fmt=lambda v: f"L={v:.2f}", fontsize=7)
for k in ASSETS:
    ax.scatter(syn[k]["I1"], syn[k]["I2"], s=70, color=COLOR[k], edgecolor="white", lw=1.5, zorder=3, label=SHORT[k])
    off = {"CAC": (6, 6), "SPX": (-62, 8), "TTE": (4, -12), "LVMH": (-52, 7), "OATFR": (6, 4), "UST": (-20, 9), "RE": (6, 4), "PE": (6, -10)}[k]
    ax.annotate(SHORT[k], (syn[k]["I1"], syn[k]["I2"]), xytext=off, textcoords="offset points", fontsize=7, color=INK2)
ax.set_xlim(0, 1.0); ax.set_ylim(0, 1.0)
ax.set_xlabel("I₁ : liquidité juridique / physique (délai minimal)"); ax.set_ylabel("I₂ : liquidité financière (décote q99,5 %)")
ax.set_title(f"Carte de liquidité et iso-lignes de L = x·I₁ + (1−x)·I₂  (x* = {x_star:.2f})")
savefig(fig, "f12_carte_liquidite")

fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.3))
for k in ASSETS:
    axs[0].plot(xs, xs * syn[k]["I1"] + (1 - xs) * syn[k]["I2"], color=COLOR[k], label=SHORT[k])
axs[0].axvline(x_star, color=INK, ls=":", lw=1); axs[0].set_xlabel("pondération x"); axs[0].set_ylabel("L(x)")
axs[0].set_title("a) Indicateur synthétique selon x"); axs[0].legend(fontsize=6.5, ncol=2)
axs[1].plot(xs, sse, color=INK, lw=1.6, label="SCE(x) vs score ALM")
axs[1].axvline(x_star, color=INK, ls=":", lw=1)
axs[1].set_xlabel("pondération x"); axs[1].set_title("b) Calibration de x* sur le coût ALM"); axs[1].set_ylabel("somme des carrés des écarts")
savefig(fig, "f13_sensibilite_x")

# nettoyage et export
for k in LISTED:
    R["listed"][k].pop("_resid", None)
    S = R["listed"][k].pop("_surf")
    np.save(os.path.join(RES, f"surf_{k}.npy"), np.array([S["np"][0], S["np"][1], S["p"][0], S["p"][1]]))
np.save(os.path.join(RES, "grid_Q.npy"), Q_GRID); np.save(os.path.join(RES, "grid_T.npy"), T_GRID)
for kind in ("RE", "PE"):
    R["unlisted"][kind].pop("_km", None)
json.dump(R, open(os.path.join(RES, "results.json"), "w"), indent=1, default=float)
print(json.dumps({k: {kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in syn[k].items()} for k in syn}, indent=0, ensure_ascii=False))
print("x* =", x_star)
