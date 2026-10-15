"""
Application ALM : assureur prévoyance fictif.
 - simulation stochastique des flux de passif (décès, incapacité, invalidité) en central et en stress
 - échelle de liquidité (matelas mobilisable par horizon, net des coûts ΔPTV_99,5 %)
 - stratégie de liquidation optimale (minimisation du coût de liquidité sous contrainte d'absence d'impasse)
 - allocation stratégique sous contraintes de volatilité et de liquidité
Sorties : figs/f14..f17, results/alm.json
"""
import json, os
import numpy as np
import pandas as pd
from scipy import optimize, stats
from style import plt, ASSETS, SHORT, COLOR, INK, INK2, MUTED

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data"); FIG = os.path.join(HERE, "..", "figs"); RES = os.path.join(HERE, "..", "results")
R = json.load(open(os.path.join(RES, "results.json"), encoding="utf8"))
d = pd.read_csv(os.path.join(DATA, "listed_daily.csv"), index_col=0, parse_dates=True)
reQ = pd.read_csv(os.path.join(DATA, "re_quarterly.csv"), index_col=0, parse_dates=True)
peQ = pd.read_csv(os.path.join(DATA, "pe_quarterly.csv"), index_col=0, parse_dates=True)
rng = np.random.default_rng(2027)
LISTED = ["CAC", "SPX", "OATFR", "UST", "TTE", "LVMH"]
TD = 252 / 365; ALPHA = 0.995

# ---------------------------------------------------------------------------
# 1. Bilan au 31/12/2025 (M€)
# ---------------------------------------------------------------------------
A_TOT = 620.0
W0 = {"CASH": 0.05, "OATFR": 0.38, "UST": 0.05, "TTE": 0.11, "LVMH": 0.11, "CAC": 0.07, "SPX": 0.06,
      "RE": 62.7 / A_TOT, "PE": 0.0}
W0["PE"] = 1 - sum(W0.values())
A0 = {k: A_TOT * w for k, w in W0.items()}
LIAB = {"PM invalidité (rentes en cours)": 215.0, "PM incapacité (arrêts de travail en cours)": 85.0,
        "PSAP décès et prestations à payer": 70.0, "PM rentes éducation / conjoint": 60.0,
        "Provision pour égalisation": 40.0, "Autres provisions techniques": 25.0}
FP = A_TOT - sum(LIAB.values())

# ---------------------------------------------------------------------------
# 2. Flux de passif mensuels (M€) : 10 000 scénarios x 12 mois
# ---------------------------------------------------------------------------
NS, NM = 10000, 12
base = dict(prem=14.0, ij=4.5, inval=3.0, rentes=0.8, frais=1.6, lam_dc=25, sev_dc=0.110, sev_cv=0.8)

def simulate(stress):
    m = np.arange(NM)
    lam = base["lam_dc"] * (np.where(m < 6, 1.5, 1.0) if stress else 1.0)
    ij_mult = (np.where(m < 3, 2.0, np.where(m < 9, 1.4, 1.1)) if stress else np.ones(NM))
    inv_mult = (np.where(m < 6, 1.0, 1.15) if stress else np.ones(NM))    # bascule incapacité -> invalidité
    prem_mult = (np.where(m < 1, 0.55, 0.80) if stress else np.ones(NM))  # report de cotisations + perte d'un grand compte
    one_off = np.zeros(NM)
    if stress:
        one_off[0] = 25.0                                                 # sortie exceptionnelle (transfert d'engagements)
    n_dc = rng.poisson(np.broadcast_to(lam, (NS, NM)))
    s2 = np.log(1 + base["sev_cv"] ** 2); mu = np.log(base["sev_dc"]) - s2 / 2
    dc = np.zeros((NS, NM))
    tot = n_dc.sum()
    sev = rng.lognormal(mu, np.sqrt(s2), tot)
    idx = np.repeat(np.arange(NS * NM), n_dc.ravel())
    np.add.at(dc.ravel(), idx, sev)
    ij = base["ij"] * ij_mult * rng.lognormal(-0.01 / 2, 0.10, (NS, NM))
    inv = base["inval"] * inv_mult * rng.lognormal(-0.0025 / 2, 0.05, (NS, NM))
    prem = base["prem"] * prem_mult * rng.lognormal(-0.0025 / 2, 0.05, (NS, NM))
    out = dc + ij + inv + base["rentes"] + base["frais"] + one_off
    net_out = out - prem                                                  # > 0 : besoin de trésorerie
    return net_out

net_base = simulate(False); net_str = simulate(True)
cum_base = net_base.cumsum(1); cum_str = net_str.cumsum(1)
H_DAYS = [7, 30, 90, 180, 365]

def cum_at(cum, h):
    """Besoin cumulé à h jours (interpolation linéaire intra-mensuelle)."""
    mth = h / 30.4
    j = int(np.floor(mth)); frac = mth - j
    prev = cum[:, j - 1] if j >= 1 else 0
    nxt = cum[:, min(j, NM - 1)]
    return prev + frac * (nxt - prev) if j < NM else cum[:, -1]

need = {h: dict(base_q50=float(np.quantile(cum_at(cum_base, h), 0.5)),
                base_q995=float(np.quantile(cum_at(cum_base, h), ALPHA)),
                str_q50=float(np.quantile(cum_at(cum_str, h), 0.5)),
                str_q995=float(np.quantile(cum_at(cum_str, h), ALPHA))) for h in H_DAYS}

fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.4), sharey=True)
mm = np.arange(1, NM + 1)
for ax, cum, ttl, col in [(axs[0], cum_base, "a) Scénario central", COLOR["OATFR"]), (axs[1], cum_str, "b) Scénario de stress prévoyance", COLOR["PE"])]:
    for lo, hi, al in [(0.005, 0.995, 0.18), (0.05, 0.95, 0.3), (0.25, 0.75, 0.45)]:
        ax.fill_between(mm, np.quantile(cum, lo, 0), np.quantile(cum, hi, 0), color=col, alpha=al, lw=0)
    ax.plot(mm, np.median(cum, 0), color=INK, lw=1.6, label="médiane")
    ax.plot(mm, np.quantile(cum, ALPHA, 0), color=INK, lw=1, ls="--", label="quantile 99,5 %")
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_title(ttl); ax.set_xlabel("mois")
axs[0].set_ylabel("besoin de trésorerie cumulé (M€)\n(> 0 : sorties nettes)"); axs[0].legend(loc="upper left")
fig.text(0.5, -0.04, "Bandes : intervalles 50 %, 90 % et 99 % (10 000 simulations)", ha="center", fontsize=7.5, color=INK2)
plt.savefig(os.path.join(FIG, "f14_flux_passif.png")); plt.close(fig)

# ---------------------------------------------------------------------------
# 3. Échelle de liquidité : liquidité mobilisable à l'horizon h (nette des coûts au q99,5 %)
# ---------------------------------------------------------------------------
SHOCK = {"CASH": 0.0, "OATFR": -0.06, "UST": -0.05, "TTE": -0.08, "LVMH": -0.07, "CAC": -0.39, "SPX": -0.39, "RE": -0.25, "PE": -0.49}
RHO = {"CAC": 0.25, "SPX": 0.25, "OATFR": 1.0, "UST": 1.0, "TTE": 1.0, "LVMH": 1.0}
P = json.load(open(os.path.join(DATA, "params.json")))

def unit_cost_q(k, Q_eur, t_cal, q=ALPHA, n=4000, seed=5):
    """Coût unitaire ΔP_q(Q,t) d'un actif coté (modèle racine carrée, bootstrap)."""
    o = R["listed"][k]; g = np.random.default_rng(seed)
    i = g.integers(0, len(d), n)
    sg = d[f"{k}_vol"].values[i]; V = d[f"{k}_volume"].values[i]; s = d[f"{k}_spread"].values[i]
    t = max(t_cal * TD, 1 / 8.5)
    e = g.normal(0, o["resid_sd"], n)
    c = P["fees_bp"][k] * 1e-4 + s / 2 + o["Y_hat"] * sg * (Q_eur / (V * t)) ** o["delta_hat"] * np.exp(e)
    return float(np.quantile(c, q))

def mobilisable(k, A_meur, h, stressed=True):
    """(montant net mobilisable M€, coût moyen) à l'horizon h jours."""
    A = A_meur * (1 + SHOCK[k]) if stressed else A_meur
    if k == "CASH":
        return A, 0.0
    if k in LISTED:
        Tl = R["synthetic"][k]["T_leg"]
        if h <= Tl:
            return 0.0, 0.0
        Vq = np.quantile(d[f"{k}_volume"].values, 1 - ALPHA)
        cap = RHO[k] * Vq * (h - Tl) * TD / 1e6
        x = min(A, cap)
        if x <= 0:
            return 0.0, 0.0
        c = unit_cost_q(k, x * 1e6, h - Tl)
        return x * (1 - c), c
    s = R["synthetic"][k]
    o = R["unlisted"][k]; f = o["stress"]
    if h < s["t_min"]:
        return 0.0, 0.0
    return A * (1 - s["dP995"]), s["dP995"]

ladder = {h: {k: mobilisable(k, A0[k], h) for k in A0} for h in H_DAYS}
LR = {h: sum(v[0] for v in ladder[h].values()) / max(need[h]["str_q995"], 1e-9) for h in H_DAYS}

fig, ax = plt.subplots(figsize=(8.6, 3.8))
keys = ["CASH", "UST", "OATFR", "CAC", "SPX", "TTE", "LVMH", "RE", "PE"]
colors = {**COLOR, "CASH": "#8a8984"}
xpos = np.arange(len(H_DAYS)); bottom = np.zeros(len(H_DAYS))
for k in keys:
    vals = np.array([ladder[h][k][0] for h in H_DAYS])
    ax.bar(xpos, vals, bottom=bottom, color=colors[k], width=0.62, edgecolor="white", lw=1.0,
           label=("Trésorerie" if k == "CASH" else SHORT[k]))
    bottom += vals
ax.scatter(xpos, [need[h]["str_q995"] for h in H_DAYS], marker="D", s=46, color=INK, zorder=4, label="besoin stressé q99,5 %")
for j, h in enumerate(H_DAYS):
    ax.text(xpos[j], bottom[j] + 8, f"RL = {LR[h]:.1f}", ha="center", fontsize=7.5, color=INK2)
ax.set_xticks(xpos); ax.set_xticklabels([f"{h} j" for h in H_DAYS]); ax.set_ylim(0, bottom.max() * 1.14)
ax.set_ylabel("liquidité nette mobilisable (M€)")
ax.set_title("Échelle de liquidité en stress (valeurs choquées, coûts ΔPTV q99,5 %)")
ax.legend(ncol=5, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.1))
plt.savefig(os.path.join(FIG, "f15_echelle_liquidite.png")); plt.close(fig)

# ---------------------------------------------------------------------------
# 4. Stratégie de liquidation optimale sur 12 mois (besoin stressé q99,5 % mensuel)
#    min Σ_i Σ_m [ c_i(x_im) x_im + μ_i (12 - m)/12 x_im ]
#    s.c.  cash_0 + Σ_{m'≤m} Σ_i x_im' (1 - c_i(x_im')) ≥ Besoin_cum(m)  ∀m ;  Σ_m x_im ≤ A_i
# ---------------------------------------------------------------------------
MU = {"CASH": 0.020, "OATFR": 0.034, "UST": 0.024, "TTE": 0.039, "LVMH": 0.036, "CAC": 0.065, "SPX": 0.065, "RE": 0.055, "PE": 0.095}
need_m = np.quantile(cum_str, ALPHA, 0)                     # besoin cumulé q99,5 % (M€)
SELL = LISTED
Astr = {k: A0[k] * (1 + SHOCK[k]) for k in A0}

def cost_curve(k, x_meur):
    """Coût unitaire médian si x M€ vendus sur un mois (21 séances), au q99,5 % de marché."""
    o = R["listed"][k]
    sg = np.quantile(d[f"{k}_vol"], 0.9); V = np.quantile(d[f"{k}_volume"], 0.1); s = np.quantile(d[f"{k}_spread"], 0.9)
    return P["fees_bp"][k] * 1e-4 + s / 2 + o["Y_hat"] * sg * (np.maximum(x_meur, 0) * 1e6 / (V * 21)) ** o["delta_hat"]

nI, nM = len(SELL), NM
def unpack(z): return z.reshape(nI, nM)
def objective(z):
    X = unpack(z); tot = 0.0
    for i, k in enumerate(SELL):
        c = cost_curve(k, X[i]); tot += np.sum(X[i] * c + MU[k] * (NM - np.arange(nM)) / 12 * X[i])
    return tot
def cash_cum(z):
    X = unpack(z)
    proceeds = sum(X[i] * (1 - cost_curve(k, X[i])) for i, k in enumerate(SELL))
    return Astr["CASH"] + np.cumsum(proceeds)
cons = [{"type": "ineq", "fun": lambda z: cash_cum(z) - need_m},
        {"type": "ineq", "fun": lambda z: np.array([Astr[k] - unpack(z)[i].sum() for i, k in enumerate(SELL)])}]
z0 = np.full(nI * nM, max(need_m.max(), 1) / (nI * nM))
res = optimize.minimize(objective, z0, method="SLSQP", bounds=[(0, None)] * (nI * nM), constraints=cons,
                        options=dict(maxiter=500, ftol=1e-9))
Xopt = unpack(res.x)

# stratégie naïve : vente au prorata des encours cotés, au fil de l'eau
def prorata():
    w = np.array([Astr[k] for k in SELL]); w = w / w.sum()
    X = np.zeros((nI, nM)); cash = Astr["CASH"]
    for m in range(nM):
        gap = max(need_m[m] - cash, 0)
        if gap > 0:
            # ventes brutes nécessaires (itération point fixe sur le coût)
            g = gap
            for _ in range(20):
                c = np.array([cost_curve(k, g * w[i]) for i, k in enumerate(SELL)])
                g = gap / (1 - np.dot(w, c))
            X[:, m] = g * w; cash += gap
    return X
Xpr = prorata()
def liq_cost(X): return float(sum(np.sum(X[i] * cost_curve(k, X[i])) for i, k in enumerate(SELL)))
def carry_cost(X): return float(sum(np.sum(MU[k] * (NM - np.arange(nM)) / 12 * X[i]) for i, k in enumerate(SELL)))
liq_res = dict(success=bool(res.success), opt_liq=liq_cost(Xopt), opt_carry=carry_cost(Xopt), opt_sold=float(Xopt.sum()),
               pr_liq=liq_cost(Xpr), pr_carry=carry_cost(Xpr), pr_sold=float(Xpr.sum()),
               sold_by_asset_opt={k: float(Xopt[i].sum()) for i, k in enumerate(SELL)},
               sold_by_asset_pr={k: float(Xpr[i].sum()) for i, k in enumerate(SELL)},
               need_12m=float(need_m[-1]), cash0=Astr["CASH"])

fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.4), sharey=True)
for ax, X, ttl in [(axs[0], Xopt, "a) Stratégie optimale"), (axs[1], Xpr, "b) Vente au prorata")]:
    b = np.zeros(nM)
    for i, k in enumerate(SELL):
        ax.bar(mm, X[i], bottom=b, color=COLOR[k], edgecolor="white", lw=0.8, width=0.75, label=SHORT[k]); b += X[i]
    ax.set_title(f"{ttl} — coût total {liq_cost(X) + carry_cost(X):.2f} M€"); ax.set_xlabel("mois")
axs[0].set_ylabel("ventes brutes (M€)"); axs[1].legend(fontsize=7, ncol=2)
plt.savefig(os.path.join(FIG, "f16_liquidation_optimale.png")); plt.close(fig)

# ---------------------------------------------------------------------------
# 5. Allocation : max E[r] - coût de liquidité attendu, s.c. σ ≤ σ_max, RL(30 j) ≥ 1,2
# ---------------------------------------------------------------------------
KEYS = ["CASH", "OATFR", "UST", "TTE", "LVMH", "CAC", "SPX", "RE", "PE"]
qret = pd.DataFrame({k: d[f"{k}_ret"].resample("QE").sum() for k in LISTED})
ro = np.log(reQ["appraisal"]).diff(); po = np.log(peQ["nav"]).diff()
aR = R["unlisted"]["RE"]["geltner_a_hat"]; aP = R["unlisted"]["PE"]["geltner_a_hat"]
qret["RE"] = (ro - (1 - aR) * ro.shift(1)) / aR
qret["PE"] = (po - (1 - aP) * po.shift(1)) / aP
qret = qret.dropna()[KEYS[1:]]           # même ordre que KEYS (hors trésorerie)
C = qret.cov().values * 4
C = np.pad(C, ((1, 0), (1, 0)))                               # trésorerie : variance nulle
C[0, 0] = 0.005 ** 2
mu = np.array([MU[k] for k in KEYS])
# coût de liquidité attendu = P(vente forcée sur 1 an) x ΔP_99,5 de vente au plus tôt
PI_FORCE = 0.05
lc = np.array([0 if k == "CASH" else R["synthetic"][k]["dP995"] for k in KEYS]) * PI_FORCE
ell30 = np.array([1.0 if k == "CASH" else (ladder[30][k][0] / max(A0[k] * (1 + SHOCK[k]), 1e-9) * (1 + SHOCK[k])) for k in KEYS])
need30 = need[30]["str_q995"] / A_TOT
ub = {"CASH": 1, "OATFR": 0.6, "UST": 0.15, "TTE": 0.15, "LVMH": 0.15, "CAC": 0.15, "SPX": 0.15, "RE": 0.15, "PE": 0.10}

Lsc = np.array([1.0 if k == "CASH" else R["synthetic"][k]["L"] for k in KEYS])
L_MIN = 0.60

def solve(sig_max, liq_con=True, lr_min=1.2):
    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1},
            {"type": "ineq", "fun": lambda w: sig_max ** 2 - w @ C @ w}]
    if liq_con:
        cons.append({"type": "ineq", "fun": lambda w: w @ ell30 - lr_min * need30})
        cons.append({"type": "ineq", "fun": lambda w: w @ Lsc - L_MIN})          # score de liquidité du portefeuille
    r = optimize.minimize(lambda w: -(w @ mu - w @ lc), np.array([W0[k] for k in KEYS]), method="SLSQP",
                          bounds=[(0, ub[k]) for k in KEYS], constraints=cons, options=dict(maxiter=400))
    w = r.x
    return dict(ok=bool(r.success), w=w.tolist(), ret=float(w @ mu), net=float(w @ mu - w @ lc), vol=float(np.sqrt(w @ C @ w)),
                lr30=float(w @ ell30 / need30), Lp=float(w @ Lsc))

sig_grid = np.linspace(0.035, 0.11, 16)
front_nc = [solve(s, False) for s in sig_grid]; front_c = [solve(s, True) for s in sig_grid]
w0v = np.array([W0[k] for k in KEYS])
cur = dict(ret=float(w0v @ mu), net=float(w0v @ mu - w0v @ lc), vol=float(np.sqrt(w0v @ C @ w0v)), lr30=float(w0v @ ell30 / need30), Lp=float(w0v @ Lsc))
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6))
axs[0].plot([f["vol"] * 100 for f in front_nc], [f["net"] * 100 for f in front_nc], color=COLOR["PE"], marker="o", ms=3.5, label="sans contrainte de liquidité")
axs[0].plot([f["vol"] * 100 for f in front_c], [f["net"] * 100 for f in front_c], color=COLOR["CAC"], marker="o", ms=3.5, label="avec RL(30 j) ≥ 1,2 et L_p ≥ 0,60")
axs[0].scatter([cur["vol"] * 100], [cur["net"] * 100], color=INK, marker="*", s=90, zorder=4, label="allocation actuelle")
axs[0].set_xlabel("volatilité annuelle (%)"); axs[0].set_ylabel("rendement net du coût de liquidité (%)")
axs[0].set_title("a) Frontières efficientes"); axs[0].legend(fontsize=7, loc="lower right")
j = int(np.argmin(np.abs(sig_grid - 0.08)))
wv = np.array(front_c[j]["w"]); wn = np.array(front_nc[j]["w"])
xx = np.arange(len(KEYS)); bw = 0.27
axs[1].bar(xx - bw, w0v * 100, bw, color="#b9b8b2", label="actuelle")
axs[1].bar(xx, wn * 100, bw, color=COLOR["PE"], label="σ ≤ 8 %, sans contrainte")
axs[1].bar(xx + bw, wv * 100, bw, color=COLOR["CAC"], label="σ ≤ 8 %, avec contrainte")
axs[1].set_xticks(xx); axs[1].set_xticklabels(["Trés.", "OAT", "UST", "TTE", "LVMH", "CAC", "S&P", "Bur.", "PE"], fontsize=7.5)
axs[1].set_ylabel("poids (%)"); axs[1].set_title("b) Allocations comparées"); axs[1].legend(fontsize=7)
plt.savefig(os.path.join(FIG, "f17_allocation.png")); plt.close(fig)

# test de résistance inversé : sortie exceptionnelle X* rendant RL(30 j) = 1
mob30 = sum(v[0] for v in ladder[30].values())
X_star = mob30 - need[30]["str_q995"] + 25.0
surv = None
for hh in range(1, 366):
    mob = sum(mobilisable(k, A0[k], hh)[0] for k in A0)
    if mob < float(np.quantile(cum_at(cum_str, hh), ALPHA)) * 10:
        surv = hh; break
out = dict(X_star=float(X_star), mob30=float(mob30), L_MIN=L_MIN, Lsc=dict(zip(KEYS, Lsc.tolist())), A_TOT=A_TOT, W0=W0, A0=A0, LIAB=LIAB, FP=FP, base=base, need=need, LR=LR, SHOCK=SHOCK,
           ladder={h: {k: [float(v[0]), float(v[1])] for k, v in ladder[h].items()} for h in H_DAYS},
           liquidation=liq_res, MU=MU, PI_FORCE=PI_FORCE, alloc_current=cur,
           alloc_6_nc=front_nc[j], alloc_6_c=front_c[j], KEYS=KEYS, sig6=float(sig_grid[j]),
           frontier_nc=front_nc, frontier_c=front_c, corr=qret.corr().round(2).to_dict(),
           vol_ann={k: float(np.sqrt(C[i, i])) for i, k in enumerate(KEYS)})
json.dump(out, open(os.path.join(RES, "alm.json"), "w"), indent=1, default=float)
print("X*", X_star, "mob30", mob30, "surv10x", surv)
print(json.dumps({"need": need, "LR": LR, "liq": liq_res, "cur": cur, "c6": front_c[j], "nc6": front_nc[j]}, indent=1, default=float))
