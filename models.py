"""Modèles de liquidité de l'article (fonctions pures, sans Streamlit)."""
import numpy as np
from scipy import stats

TD = 252 / 365   # jours de bourse par jour calendaire


# ---------------------------------------------------------------- actifs cotés
def listed_cost_samples(Q, t, sigma_d, V, s, fees_bp, Y, delta, sd_sigma, sd_V, sd_s, resid_sd, unc=1.0, M=4000, seed=1):
    """ΔP(Q,t) = f + s/2 + Y σ_d (Q/(V t))^δ e^ε, avec (σ_d, V, s) log-normaux autour des valeurs centrales.
    Q en euros, V en euros/jour, t en jours de bourse. Renvoie un échantillon de coûts relatifs."""
    g = np.random.default_rng(seed)
    z = g.standard_normal((M, 4))
    sg = sigma_d * np.exp(unc * sd_sigma * z[:, 0] - 0.5 * (unc * sd_sigma) ** 2)
    vv = V * np.exp(-unc * sd_V * (0.6 * z[:, 0] + 0.8 * z[:, 1]))     # volume bas quand la volatilité est haute
    ss = s * np.exp(unc * sd_s * (0.7 * z[:, 0] + 0.71 * z[:, 2]))
    e = resid_sd * unc * z[:, 3]
    imp = Y * sg * (Q / (vv * max(t, 1 / 8.5))) ** delta * np.exp(e - 0.5 * (resid_sd * unc) ** 2)
    return fees_bp * 1e-4 + ss / 2 + imp


def listed_cost_central(Q, t, sigma_d, V, s, fees_bp, Y, delta):
    imp = Y * sigma_d * (Q / (V * max(t, 1 / 8.5))) ** delta
    return fees_bp * 1e-4, s / 2, imp


# ---------------------------------------------------------------- actifs non cotés
def auction_quantile(q, Lam, mu, sg):
    """Quantile q du rapport prix/valeur = max de N~Poisson(Lam) offres log-normales, conditionnel à N ≥ 1."""
    Lam = np.maximum(np.asarray(Lam, float), 1e-9)
    e = np.exp(-Lam)
    Fx = 1 + np.log(e + q * (1 - e)) / Lam
    Fx = np.clip(Fx, 1e-12, 1 - 1e-12)
    return np.exp(mu + sg * stats.norm.ppf(Fx))


def auction_discount(alpha, t, Tleg, nu_day, mu, sg):
    """ΔPTV_α(t) = 1 - quantile (1-α) du rapport prix/valeur ; NaN si t ≤ T_leg."""
    t = np.asarray(t, float)
    Lam = nu_day * np.maximum(t - Tleg, 0)
    out = 1 - auction_quantile(1 - alpha, Lam, mu, sg)
    return np.where(t > Tleg, out, np.nan)


def auction_simulate(t, Tleg, nu_day, mu, sg, M=10000, seed=3):
    g = np.random.default_rng(seed)
    n = g.poisson(nu_day * max(t - Tleg, 0), M)
    disc = np.full(M, np.nan)
    for i in np.nonzero(n)[0]:
        disc[i] = 1 - np.exp(mu + sg * g.standard_normal(n[i])).max()
    return disc, float((n == 0).mean())


def n_star(x, p, mu, sg):
    F = stats.norm.cdf((np.log(x) - mu) / sg)
    if F <= 0:
        return 1, F
    if F >= 1:
        return None, F
    return int(np.ceil(np.log(1 - p) / np.log(F))), F


def t_min_unlisted(alpha, Tleg, nu_day):
    return Tleg + np.log(1 / (1 - alpha)) / nu_day


# ---------------------------------------------------------------- scores et notation
def score_time(t, Tmax=1095.0):
    return float(np.clip(1 - np.log1p(t) / np.log1p(Tmax), 0, 1))


def score_cost(c, eps=1e-4):
    return float(np.clip(1 - np.log1p(c / eps) / np.log1p(1 / eps), 0, 1))


def letter_time(t):
    return "A" if t < 1 else "B" if t < 3 else "C" if t < 7 else "D" if t < 30 else "E" if t < 365 else "F"


def letter_obs(n):
    return "A" if n >= 100 else "B" if n >= 30 else "C" if n >= 5 else "D" if n >= 1 else "E" if n >= 1 / 7 else "F"


def letter_score(L):
    return "A" if L >= 0.80 else "B" if L >= 0.65 else "C" if L >= 0.50 else "D" if L >= 0.35 else "E" if L >= 0.20 else "F"


def worst(*notes):
    return max(notes, key="ABCDEF".index)


def alm_cost(tmin, dp, H, r_e, pi):
    return dp if tmin <= H else dp + r_e * (tmin - H) / 365 + pi


def x_star(I1, I2, S):
    I1, I2, S = map(np.asarray, (I1, I2, S))
    d = I1 - I2
    den = float(d @ d)
    return float(np.clip((S - I2) @ d / den, 0, 1)) if den > 0 else 0.5


# ---------------------------------------------------------------- ALM prévoyance
def simulate_liabilities(mort=1.5, ij=2.0, prem_drop=0.20, one_off=25.0, NS=4000, NM=12, seed=2027,
                         prem=14.0, ij0=4.5, inval=3.0, rentes=0.8, frais=1.6, lam=25, sev=0.110, cv=0.8):
    """Besoin de trésorerie cumulé (M€) : NS scénarios × NM mois (> 0 : sorties nettes)."""
    g = np.random.default_rng(seed)
    m = np.arange(NM)
    lam_m = lam * np.where(m < 6, mort, 1.0)
    ij_m = np.where(m < 3, ij, np.where(m < 9, 1 + 0.4 * (ij - 1), 1 + 0.1 * (ij - 1)))
    inv_m = np.where(m < 6, 1.0, 1 + 0.15 * (ij - 1))
    prem_m = np.where(m < 1, 1 - min(1.0, 2.25 * prem_drop), 1 - prem_drop)
    n = g.poisson(np.broadcast_to(lam_m, (NS, NM)))
    s2 = np.log(1 + cv ** 2); mu = np.log(sev) - s2 / 2
    # somme de n log-normales ≈ n × moyenne + bruit gaussien (approximation suffisante pour l'illustration)
    dc = n * sev + np.sqrt(n) * sev * cv * g.standard_normal((NS, NM))
    flows = (dc + ij0 * ij_m * g.lognormal(-0.005, 0.10, (NS, NM)) + inval * inv_m * g.lognormal(-0.00125, 0.05, (NS, NM))
             + rentes + frais - prem * prem_m * g.lognormal(-0.00125, 0.05, (NS, NM)))
    flows[:, 0] += one_off
    return flows.cumsum(1)


def need_at(cum, h, q=0.995):
    mth = h / 30.4; j = int(np.floor(mth)); fr = mth - j
    NM = cum.shape[1]
    if j >= NM:
        x = cum[:, -1]
    else:
        prev = cum[:, j - 1] if j >= 1 else 0
        x = prev + fr * (cum[:, j] - prev)
    return float(np.quantile(x, q))
