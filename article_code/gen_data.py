"""
Génération d'un historique fictif (2015-2025) de données financières et de
microstructure pour 8 actifs, calibré sur des ordres de grandeur publics.

Sorties (dossier data/) :
  listed_daily.csv     prix, volumes, fourchettes, déséquilibres d'ordres (6 actifs cotés)
  bond_trades.csv      transactions OTC simulées (obligations TotalEnergies / LVMH)
  metaorders.csv       journal fictif d'exécutions de l'assureur (Q, t, coût réalisé)
  re_quarterly.csv     valeur "vraie" et valeur d'expertise de l'immeuble de bureaux
  pe_quarterly.csv     valeur "vraie" et NAV publiée du PE small caps
  re_deals.csv         transactions de bureaux comparables (délai, décote, nb d'offres)
  pe_deals.csv         transactions secondaires PE small caps
  params.json          paramètres de calibration
"""
import json, os
import numpy as np
import pandas as pd

rng = np.random.default_rng(20261015)
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

dates = pd.bdate_range("2015-01-02", "2025-12-31")
N = len(dates)
DT = 1 / 252

# ---------------------------------------------------------------------------
# 1. Facteur de stress de marché commun (épisodes historiques stylisés)
# ---------------------------------------------------------------------------
episodes = [  # (début, fin, intensité du choc de volatilité, dérive journalière additionnelle)
    ("2015-08-17", "2015-09-30", 0.8, -0.0030),   # dévaluation du yuan
    ("2016-06-24", "2016-07-08", 0.7, -0.0040),   # Brexit
    ("2018-10-01", "2018-12-24", 0.6, -0.0018),   # resserrement Fed
    ("2020-02-24", "2020-03-23", 1.4, -0.0240),   # Covid-19 : krach
    ("2020-03-24", "2020-06-08", 1.0, +0.0045),   # Covid-19 : rebond
    ("2022-02-24", "2022-10-12", 0.5, -0.0004),   # Ukraine / inflation
    ("2023-03-10", "2023-03-24", 0.6, -0.0020),   # SVB / Credit Suisse
    ("2025-04-02", "2025-04-09", 1.2, -0.0150),   # choc tarifaire
    ("2025-04-10", "2025-05-30", 0.6, +0.0012),
]
stress = np.zeros(N)
drift_overlay = np.zeros(N)
for a, b, k, d in episodes:
    m = (dates >= a) & (dates <= b)
    stress[m] = np.maximum(stress[m], k)
    drift_overlay[m] += d
# lissage exponentiel pour une décroissance progressive du stress
stress_s = pd.Series(stress).ewm(halflife=8).mean().values
stress_s = np.maximum(stress, stress_s)


def garch_t_returns(sigma_ann, alpha, beta, nu, lev, target_log_ret, beta_mkt=None, z_common=None, rho=0.0):
    """GJR-GARCH(1,1) à innovations de Student-t, conditionné à une valeur terminale.
    Renvoie (rendements log, volatilité conditionnelle journalière)."""
    s2_bar = (sigma_ann ** 2) * DT
    omega = s2_bar * (1 - alpha - beta - lev / 2)
    z = rng.standard_t(nu, N) / np.sqrt(nu / (nu - 2))
    if z_common is not None:
        z = rho * z_common + np.sqrt(1 - rho ** 2) * z
    h = np.empty(N); r = np.empty(N); eb = np.empty(N)
    h[0] = s2_bar
    for i in range(N):
        if i > 0:
            neg = 1.0 if eb[i - 1] < 0 else 0.0
            h[i] = omega + (alpha + lev * neg) * eb[i - 1] ** 2 + beta * h[i - 1]
        eb[i] = np.sqrt(h[i]) * z[i]            # choc GARCH de base
        r[i] = eb[i] * (1 + stress_s[i]) + drift_overlay[i]   # amplification exogène en crise
    # pont par morceaux : correction de dérive constante sur chaque année civile pour
    # reproduire les niveaux de clôture annuels de référence (target_log_ret = liste)
    yrs = dates.year.values
    for j, y in enumerate(range(2015, 2026)):
        m = yrs == y
        r[m] += (target_log_ret[j] - r[m].sum()) / m.sum()
    vol = np.sqrt(h) * (1 + stress_s)
    return r, vol, z


# ---------------------------------------------------------------------------
# 2. ETF actions (cotés sur Euronext Paris, en EUR)
# ---------------------------------------------------------------------------
z_mkt = rng.standard_t(6, N) / np.sqrt(6 / 4)
P0 = {"CAC": 42.0, "SPX": 25.0}
PT = {"CAC": 80.6, "SPX": 86.0}
# niveaux de clôture annuels de référence (fin 2014 ... fin 2025) : CAC 40 et S&P 500 converti en EUR
YE = {"CAC": [4273, 4637, 4862, 5313, 4731, 5978, 5551, 7153, 6474, 7543, 7381, 7967],
      "SPX": [1702, 1875, 2132, 2228, 2189, 2885, 3079, 4192, 3589, 4317, 5683, 5855]}
eq_par = {
    "CAC": dict(sigma_ann=0.150, alpha=0.06, beta=0.90, nu=6, lev=0.05, rho=0.92,
                adv=150e6, spread_bp=4.0, depth_alpha=2e6, depth_beta=150e3, fees_bp=1.0),
    "SPX": dict(sigma_ann=0.140, alpha=0.06, beta=0.90, nu=6, lev=0.05, rho=0.70,
                adv=110e6, spread_bp=6.0, depth_alpha=1.5e6, depth_beta=120e3, fees_bp=1.0),
}
listed = pd.DataFrame(index=dates)
listed.index.name = "date"

def microstructure(name, vol, ret, adv, spread_bp, kappa=0.8, phi=0.6, gamma=1.2,
                   sd_v=0.35, sd_s=0.20, lam_kyle=None):
    vbar = np.median(vol)
    lv = np.empty(N); lv[0] = 0
    e = rng.normal(0, sd_v, N)
    for i in range(1, N):
        lv[i] = phi * lv[i - 1] + e[i]
    volume = adv * np.exp(lv + gamma * np.log(vol / vbar) - 0.5 * sd_v ** 2 / (1 - phi ** 2))
    spread = spread_bp * 1e-4 * (vol / vbar) ** kappa * np.exp(rng.normal(0, sd_s, N) - sd_s ** 2 / 2)
    # déséquilibre d'ordres signé (en EUR) corrélé au rendement : r = lambda*OI + bruit
    oi = rng.normal(0, 0.15, N) * volume
    if lam_kyle is None:
        lam_kyle = 0.25 * np.median(vol) / (0.15 * adv)
    ret_info = lam_kyle * oi
    listed[f"{name}_volume"] = volume
    listed[f"{name}_spread"] = spread
    listed[f"{name}_oi"] = oi
    return ret_info

for k, p in eq_par.items():
    r, vol, _ = garch_t_returns(p["sigma_ann"], p["alpha"], p["beta"], p["nu"], p["lev"],
                                np.diff(np.log(YE[k])), z_common=z_mkt, rho=p["rho"])
    listed[f"{k}_vol"] = vol
    ri = microstructure(k, vol, r, p["adv"], p["spread_bp"])
    # composante informationnelle du flux d'ordres (Kyle) incorporée sans changer la valeur terminale
    r = r + ri - ri.mean()
    tgt = np.diff(np.log(YE[k]))
    for j, y in enumerate(range(2015, 2026)):      # ré-application du pont annuel
        m = dates.year.values == y
        r[m] += (tgt[j] - r[m].sum()) / m.sum()
    listed[f"{k}_ret"] = r
    listed[f"{k}_price"] = P0[k] * np.exp(np.cumsum(r))

# ---------------------------------------------------------------------------
# 3. Taux souverains 10 ans (ancrages annuels moyens) et spreads de crédit
# ---------------------------------------------------------------------------
years = np.arange(2015, 2026)
anchor_fr = [0.84, 0.47, 0.81, 0.78, 0.13, -0.15, 0.01, 1.70, 3.00, 2.95, 3.35]
anchor_us = [2.14, 1.84, 2.33, 2.91, 2.14, 0.89, 1.45, 2.95, 3.96, 4.21, 4.30]
mid_year = pd.to_datetime([f"{y}-07-01" for y in years])

def yield_path(anchor, sig_ann=0.0075, kappa=4.0, y_end=None):
    t_anchor = (mid_year - dates[0]).days.values
    t = (dates - dates[0]).days.values
    xs = list(t_anchor); ys = list(anchor)
    if y_end is not None:
        xs.append(t[-1]); ys.append(y_end)
    trend = np.interp(t, xs, ys) / 100
    x = np.zeros(N)
    e = rng.normal(0, sig_ann * np.sqrt(DT), N) * (1 + 0.6 * stress_s)
    for i in range(1, N):
        x[i] = x[i - 1] - kappa * x[i - 1] * DT + e[i]
    x -= x[-1] * t / t[-1]          # pont : x(0) = x(T) = 0
    return trend + x

y_fr = yield_path(anchor_fr, y_end=3.55)
y_us = yield_path(anchor_us, sig_ann=0.0090, y_end=4.15)

def cir_spread(theta, sig, kappa, s0, jump_scale):
    s = np.empty(N); s[0] = s0
    e = rng.normal(0, 1, N)
    for i in range(1, N):
        th = theta * (1 + jump_scale * stress_s[i])
        s[i] = abs(s[i - 1] + kappa * (th - s[i - 1]) * DT + sig * np.sqrt(max(s[i - 1], 1e-6) * DT) * e[i])
    return s

sp_tte = cir_spread(0.0050, 0.035, 6.0, 0.0055, 1.1)
sp_lvmh = cir_spread(0.0032, 0.028, 6.0, 0.0030, 1.0)

def cm_bond_returns(y):
    """Rendement journalier d'une obligation à maturité constante 10 ans (coupon = taux)."""
    c = np.maximum(y, 1e-4)
    T = 10
    D_mac = (1 + c) / c * (1 - 1 / (1 + c) ** T)       # duration de Macaulay au pair
    D_mod = D_mac / (1 + c)
    conv = (2 / c ** 2) * (1 - 1 / (1 + c) ** T) - (2 * T) / (c * (1 + c) ** (T + 1))
    conv = conv / (1 + c) ** 2 + 0  # approximation de la convexité au pair
    dy = np.diff(y, prepend=y[0])
    r = y * DT - D_mod * dy + 0.5 * np.abs(conv) * dy ** 2
    return r, D_mod

bond_par = {
    "OATFR": dict(y=y_fr, adv=1.5e9, spread_bp=3.0, depth=25e6, fees_bp=0.5, issue=40e9),
    "UST":   dict(y=y_us, adv=60e9, spread_bp=1.6, depth=100e6, fees_bp=0.3, issue=80e9),
    "TTE":   dict(y=y_fr + sp_tte, adv=7e6, spread_bp=25.0, depth=3e6, fees_bp=2.0, issue=1.0e9),
    "LVMH":  dict(y=y_fr + sp_lvmh, adv=6e6, spread_bp=20.0, depth=3e6, fees_bp=2.0, issue=1.5e9),
}
for k, p in bond_par.items():
    r, dmod = cm_bond_returns(p["y"])
    vol = pd.Series(r).rolling(21, min_periods=5).std().bfill().values
    ri = microstructure(k, vol, r, p["adv"], p["spread_bp"], kappa=1.0, sd_s=0.25)
    r = r + ri - ri.mean()
    listed[f"{k}_yield"] = p["y"]
    listed[f"{k}_dmod"] = dmod
    listed[f"{k}_ret"] = r
    listed[f"{k}_vol"] = pd.Series(r).rolling(21, min_periods=5).std().bfill().values
    listed[f"{k}_price"] = 100 * np.exp(np.cumsum(r))
listed["TTE_credit_spread"] = sp_tte
listed["LVMH_credit_spread"] = sp_lvmh
listed["stress"] = stress_s
listed.to_csv(os.path.join(OUT, "listed_daily.csv"))

# ---------------------------------------------------------------------------
# 4. Transactions OTC obligataires (pour les estimateurs de Roll / Amihud)
# ---------------------------------------------------------------------------
rows = []
for k, lam in [("TTE", 6.0), ("LVMH", 5.0)]:
    mid = listed[f"{k}_price"].values
    spr = listed[f"{k}_spread"].values
    vol = listed[f"{k}_volume"].values
    for i in range(N):
        n = rng.poisson(lam * (1 + 0.5 * stress_s[i]))
        if n == 0:
            continue
        tickets = rng.lognormal(np.log(vol[i] / max(n, 1)) - 0.5 * 0.6 ** 2, 0.6, n)
        side = rng.choice([-1, 1], n)
        intraday = rng.normal(0, listed[f"{k}_vol"].values[i] / np.sqrt(n + 1), n).cumsum()
        px = mid[i] * (1 + intraday) * (1 + side * spr[i] / 2 * rng.uniform(0.6, 1.4, n))
        for j in range(n):
            rows.append((dates[i], k, px[j], tickets[j], side[j]))
bt = pd.DataFrame(rows, columns=["date", "asset", "price", "notional", "side"])
bt.to_csv(os.path.join(OUT, "bond_trades.csv"), index=False)

# ---------------------------------------------------------------------------
# 5. Journal d'exécutions (méta-ordres) : loi en racine carrée de l'impact
#    ΔP = fees + s/2 + Y σ_d sqrt(Q / (V_d t)) + bruit
# ---------------------------------------------------------------------------
Y_true = {"CAC": 0.75, "SPX": 0.80, "OATFR": 0.60, "UST": 0.55, "TTE": 0.90, "LVMH": 0.90}
fees = {"CAC": 1.0, "SPX": 1.0, "OATFR": 0.5, "UST": 0.3, "TTE": 2.0, "LVMH": 2.0}
mo = []
for k in Y_true:
    vol = listed[f"{k}_vol"].values; V = listed[f"{k}_volume"].values; s = listed[f"{k}_spread"].values
    adv = np.median(V)
    for _ in range(1500):
        i = rng.integers(25, N)
        Q = adv * 10 ** rng.uniform(-2.3, 0.7)              # de 0,5 % à 500 % de l'ADV
        t = 10 ** rng.uniform(np.log10(1 / 8.5), np.log10(20))  # de 1 heure à 20 jours de bourse
        imp = Y_true[k] * vol[i] * np.sqrt(Q / (V[i] * t))
        cost = fees[k] * 1e-4 + s[i] / 2 + imp * np.exp(rng.normal(0, 0.35) - 0.35 ** 2 / 2)
        cost += rng.normal(0, 0.15 * vol[i] * np.sqrt(min(t, 1.0)) / 3)  # bruit de prix résiduel
        mo.append((dates[i], k, Q, t, cost, s[i], vol[i], V[i]))
mo = pd.DataFrame(mo, columns=["date", "asset", "Q", "t_days", "cost", "spread", "sigma_d", "V_d"])
mo.to_csv(os.path.join(OUT, "metaorders.csv"), index=False)

# ---------------------------------------------------------------------------
# 6. Immobilier de bureau (Île-de-France) et Private Equity small caps (France)
#    Valeur vraie trimestrielle, valeur publiée lissée (modèle de Geltner)
# ---------------------------------------------------------------------------
qdates = pd.date_range("2015-03-31", "2025-12-31", freq="QE")
NQ = len(qdates)
re_anchor = [100, 106, 114, 122, 131, 132, 134, 126, 112, 106, 105]
pe_anchor = [100, 111, 124, 136, 151, 149, 178, 186, 191, 205, 222]

def quarterly_true(anchor, sig_q, beta_eq=0.0):
    t = (qdates - qdates[0]).days.values
    ta = (pd.to_datetime([f"{y}-12-31" for y in years]) - qdates[0]).days.values
    trend = np.log(np.interp(t, ta, anchor))
    eq_q = pd.Series(listed["CAC_ret"].values, index=dates).resample("QE").sum().reindex(qdates).fillna(0).values
    eq_q = eq_q - eq_q.mean()
    noise = rng.normal(0, sig_q, NQ).cumsum()
    noise -= np.linspace(0, noise[-1], NQ)
    lv = trend + beta_eq * (np.cumsum(eq_q) - np.linspace(0, np.cumsum(eq_q)[-1], NQ)) + noise
    return np.exp(lv - lv[0])

def geltner(v, a):
    out = np.empty_like(v); out[0] = v[0]
    for i in range(1, len(v)):
        out[i] = a * v[i] + (1 - a) * out[i - 1]
    return out

# chocs de crise trimestriels transitoires (absorbés ensuite par la tendance d'ancrage)
crisis_q = {"RE": {"2020-06-30": -0.04, "2023-06-30": -0.03, "2023-09-30": -0.03},
            "PE": {"2020-03-31": -0.14, "2022-06-30": -0.06, "2022-09-30": -0.05}}
def with_crisis(v, kind):
    lv = np.log(v)
    for dt, sh in crisis_q[kind].items():
        i = qdates.get_loc(pd.Timestamp(dt))
        lv[i] += sh; lv[i + 1] += sh / 2          # choc puis rattrapage partiel
    return np.exp(lv)
re_true = 60e6 * with_crisis(quarterly_true(re_anchor, 0.045), "RE")
pe_true = 30e6 * with_crisis(quarterly_true(pe_anchor, 0.075), "PE")
re_q = pd.DataFrame({"true_value": re_true, "appraisal": geltner(re_true, 0.45)}, index=qdates)
pe_q = pd.DataFrame({"true_value": pe_true, "nav": geltner(pe_true, 0.35)}, index=qdates)
re_q.index.name = pe_q.index.name = "date"
re_q.to_csv(os.path.join(OUT, "re_quarterly.csv"))
pe_q.to_csv(os.path.join(OUT, "pe_quarterly.csv"))

# ---------------------------------------------------------------------------
# 7. Transactions : modèle d'enchère à arrivée poissonnienne d'acheteurs
#    N ~ Poisson(nu * (t - T_leg)),  offres X_j = V exp(mu_b + sigma_b eps_j),
#    prix = max_j X_j ; décote = 1 - prix / V. Si N = 0 : vente infructueuse (censure).
# ---------------------------------------------------------------------------
def market_regime(d, kind):
    y = d.year + (d.month - 1) / 12
    if kind == "RE":
        nu = 0.75 if y < 2020.2 else (0.35 if y < 2020.6 else (0.65 if y < 2022.5 else (0.28 if y < 2025.0 else 0.45)))
        mu_shift = 0.0 if y < 2022.5 else (-0.05 if y < 2025.0 else -0.02)
    else:
        nu = 0.60 if y < 2020.2 else (0.25 if y < 2020.75 else (0.65 if y < 2022.3 else (0.35 if y < 2024.0 else 0.50)))
        mu_shift = 0.0 if y < 2020.2 else (-0.12 if y < 2020.75 else (0.0 if y < 2022.3 else (-0.06 if y < 2024.0 else -0.02)))
    return nu, mu_shift

deal_par = {
    "RE": dict(T_leg=90, mu_b=-0.12, sig_b=0.07, n=650, value=re_q["true_value"], pub=re_q["appraisal"]),
    "PE": dict(T_leg=120, mu_b=-0.27, sig_b=0.12, n=420, value=pe_q["true_value"], pub=pe_q["nav"]),
}
for kind, p in deal_par.items():
    rows = []
    for _ in range(p["n"]):
        d = pd.Timestamp("2015-01-01") + pd.Timedelta(days=int(rng.integers(0, 4017)))
        nu_m, mu_sh = market_regime(d, kind)
        nu_d = nu_m / 30.4
        # délai de commercialisation choisi par le vendeur : mélange vendeurs pressés / patients
        if rng.uniform() < 0.25:
            mkt = rng.uniform(5, 45)                 # vente pressée
        else:
            mkt = rng.lognormal(np.log(150 if kind == "RE" else 170), 0.55)
        t_total = p["T_leg"] + mkt
        n_bid = rng.poisson(nu_d * mkt)
        q = qdates.searchsorted(d)
        V = float(p["value"].iloc[min(q, NQ - 1)])
        Vpub = float(p["pub"].iloc[min(q, NQ - 1)])
        if n_bid == 0:
            rows.append((d, t_total, mkt, 0, np.nan, np.nan, Vpub, 1, mkt))
            continue
        first_bid = rng.uniform(0, mkt, n_bid).min()   # date d'arrivée de la 1re offre (processus de Poisson)
        bids = np.exp(p["mu_b"] + mu_sh + p["sig_b"] * rng.normal(size=n_bid))
        ratio = bids.max() * V / Vpub        # prix rapporté à la valeur publiée (expertise / NAV)
        rows.append((d, t_total, mkt, n_bid, ratio, 1 - ratio, Vpub, 0, first_bid))
    df = pd.DataFrame(rows, columns=["date", "t_total_days", "marketing_days", "n_bids",
                                     "price_to_value", "discount", "value", "censored", "first_bid_days"])
    df.sort_values("date").to_csv(os.path.join(OUT, f"{kind.lower()}_deals.csv"), index=False)

params = dict(
    seed=20261015, episodes=episodes, equity=eq_par, P0=P0, year_end_levels=YE,
    anchors=dict(oat_fr=anchor_fr, ust=anchor_us, re=re_anchor, pe=pe_anchor),
    bonds={k: {kk: vv for kk, vv in v.items() if kk != "y"} for k, v in bond_par.items()},
    Y_true=Y_true, fees_bp=fees,
    deals={k: {kk: vv for kk, vv in v.items() if kk not in ("value", "pub")} for k, v in deal_par.items()},
    geltner=dict(RE=0.45, PE=0.35),
)
json.dump(params, open(os.path.join(OUT, "params.json"), "w"), indent=1, default=str)
print("OK", N, "jours ;", len(bt), "transactions obligataires ;", len(mo), "méta-ordres")
print(listed[[c for c in listed.columns if c.endswith("_price")]].iloc[[0, -1]].round(2))
print("yields end", y_fr[-1], y_us[-1])
