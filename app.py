"""
Application Streamlit : mesurer la liquidité en finance.
Accompagne l'article de M. Moreau et F. Planchet — version du 15/10/2026.
Lancement local :  streamlit run app.py
"""
import io, json, os, zipfile
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from i18n import LANGS, tr
import models as M

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CODE = os.path.join(HERE, "article_code")

st.set_page_config(page_title="Liquidité / Liquidity / Liquidität", page_icon="💧", layout="wide")

# palette catégorielle (ordre fixe par actif, identique aux figures de l'article)
COLOR = {"CAC": "#2a78d6", "SPX": "#eb6834", "OATFR": "#1baf7a", "UST": "#eda100", "TTE": "#e87ba4",
         "LVMH": "#008300", "RE": "#4a3aa7", "PE": "#e34948", "CASH": "#8a8984"}
LISTED = ["CAC", "SPX", "OATFR", "UST", "TTE", "LVMH"]
ALL = LISTED + ["RE", "PE"]


@st.cache_data
def load():
    R = json.load(open(os.path.join(DATA, "results.json"), encoding="utf8"))
    A = json.load(open(os.path.join(DATA, "alm.json"), encoding="utf8"))
    LP = json.load(open(os.path.join(DATA, "listed_params.json"), encoding="utf8"))
    W = pd.read_csv(os.path.join(DATA, "listed_weekly.csv"), index_col=0, parse_dates=True)
    deals = {k: pd.read_csv(os.path.join(DATA, f"{k.lower()}_deals.csv"), parse_dates=["date"]) for k in ("RE", "PE")}
    return R, A, LP, W, deals

R, A, LP, W, DEALS = load()

def layout(fig, h=380, ytitle=None, xtitle=None, logx=False, logy=False):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=50, b=10), template="plotly_white",
                      legend=dict(orientation="h", yanchor="top", y=-0.18, x=0), hovermode="x unified")
    if ytitle: fig.update_yaxes(title=ytitle)
    if xtitle: fig.update_xaxes(title=xtitle)
    if logx: fig.update_xaxes(type="log")
    if logy: fig.update_yaxes(type="log")
    return fig

def fmt(x, nd=2, lang="fr"):
    s = f"{x:,.{nd}f}"
    return s.replace(",", " ").replace(".", ",") if lang in ("fr", "de") else s

# --------------------------------------------------------------------------- barre latérale
with st.sidebar:
    lang_label = st.selectbox("🌐 Langue / Language / Sprache", list(LANGS), index=0)
    L = LANGS[lang_label]
    st.markdown(f"**{tr('app_title', L)}**")
    st.caption(tr("date", L))
    st.caption(tr("disclaimer", L))
    st.markdown("---")
    st.caption("Matthieu Moreau · Frédéric Planchet")

NAMES = tr("assets", L)
st.title(tr("app_title", L))
st.caption(tr("app_sub", L) + "  ·  " + tr("date", L))
tabs = st.tabs(tr("tabs", L))

# =========================================================================== 0. Accueil
with tabs[0]:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(tr("home_md", L))
        st.latex(r"\Delta\mathrm{PTV}_{\alpha}(Q,t) = \inf\{x : \mathbb{P}(\Delta P(Q,t)\le x)\ge \alpha\}")
        st.markdown(tr("home_md2", L))
    with c2:
        st.subheader(tr("home_results", L))
        S = R["synthetic"]
        df = pd.DataFrame([{tr("col_asset", L): NAMES[k], tr("col_L", L): round(S[k]["L"], 2), tr("col_note", L): S[k]["note_L"]}
                           for k in sorted(ALL, key=lambda k: -S[k]["L"])])
        st.dataframe(df, hide_index=True, use_container_width=True)
        fig = go.Figure(go.Bar(x=[S[k]["L"] for k in sorted(ALL, key=lambda k: S[k]["L"])],
                               y=[NAMES[k] for k in sorted(ALL, key=lambda k: S[k]["L"])], orientation="h",
                               marker_color=[COLOR[k] for k in sorted(ALL, key=lambda k: S[k]["L"])]))
        st.plotly_chart(layout(fig, 340, xtitle="L"), use_container_width=True)
        st.caption(f"x* = {fmt(R['meta']['x_star'], 2, L)}")

# =========================================================================== 1. Actifs cotés
with tabs[1]:
    st.markdown(tr("lst_intro", L))
    st.latex(r"\Delta P(Q,t) = f + \frac{s}{2} + Y\,\sigma_d\left(\frac{Q}{V\,t}\right)^{\delta}")
    left, right = st.columns([1, 2.2])
    with left:
        st.markdown(f"**{tr('params', L)}**")
        k = st.selectbox(tr("preset", L), LISTED, format_func=lambda a: NAMES[a], key="lst_preset")
        p = LP[k]
        sig = st.slider(tr("sigma_ann", L), 1.0, 60.0, float(round(p["sigma_d"] * np.sqrt(252) * 100, 1)), 0.5, key=f"sig_{k}")
        adv = st.number_input(tr("adv", L), 0.1, 100000.0, float(round(p["adv"] / 1e6, 1)), key=f"adv_{k}")
        spr = st.slider(tr("spread", L), 0.5, 200.0, float(round(p["spread_bp"], 1)), 0.5, key=f"spr_{k}")
        fee = st.slider(tr("fees", L), 0.0, 20.0, float(p["fees_bp"]), 0.1, key=f"fee_{k}")
        Y = st.slider(tr("Y", L), 0.1, 2.0, float(round(p["Y"], 2)), 0.01, key=f"Y_{k}")
        dlt = st.slider(tr("delta", L), 0.2, 1.0, float(round(p["delta"], 2)), 0.01, key=f"d_{k}")
        Q = st.number_input(tr("Q", L), 0.01, 5000.0, 10.0, key="lst_Q")
        t = st.slider(tr("t", L), 0.125, 60.0, 1.0, 0.125, key="lst_t")
        unc = st.slider(tr("unc", L), 0.0, 2.0, 1.0, 0.1, key="lst_unc")
    sigma_d = sig / 100 / np.sqrt(252); V = adv * 1e6; s = spr * 1e-4
    args = dict(sigma_d=sigma_d, V=V, s=s, fees_bp=fee, Y=Y, delta=dlt, sd_sigma=p["sd_log_sigma"], sd_V=p["sd_log_V"],
                sd_s=p["sd_log_s"], resid_sd=p["resid_sd"], unc=unc)
    x = M.listed_cost_samples(Q * 1e6, t, M=8000, **args)
    q50, q995 = np.quantile(x, 0.5), np.quantile(x, 0.995)
    with right:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(tr("m_total", L), f"{fmt(q50 * 1e4, 1, L)} pb" if L == "fr" else f"{fmt(q50 * 1e4, 1, L)} bp" if L == "en" else f"{fmt(q50 * 1e4, 1, L)} Bp")
        m2.metric(tr("m_stress", L), f"{fmt(q995 * 1e4, 1, L)}" + (" pb" if L == "fr" else " bp" if L == "en" else " Bp"))
        m3.metric(tr("m_euro", L), f"{fmt(q50 * Q * 1e6, 0, L)} €")
        m4.metric(tr("m_part", L), f"{fmt(100 * Q * 1e6 / (V * t), 1, L)} %")
        f_, h_, i_ = M.listed_cost_central(Q * 1e6, t, sigma_d, V, s, fee, Y, dlt)
        fig = go.Figure()
        for lab, val, col in ((tr("c_fees", L), f_, "#8a8984"), (tr("c_half", L), h_, "#2a78d6"), (tr("c_imp", L), i_, "#e34948")):
            fig.add_trace(go.Bar(x=[val * 1e4], y=[""], orientation="h", name=lab, marker_color=col, hovertemplate="%{x:.2f}"))
        fig.update_layout(barmode="stack")
        st.plotly_chart(layout(fig, 150, xtitle=tr("decomp", L)), use_container_width=True)
        Qg = np.logspace(-1, np.log10(max(Q * 50, 500)), 40)
        fig = go.Figure()
        for tt, dash in ((t, "solid"), (min(t * 5, 60), "dot"), (min(t * 20, 60), "dash")):
            qs = np.array([np.quantile(M.listed_cost_samples(qq * 1e6, tt, M=1500, **args), [0.5, 0.995]) for qq in Qg])
            fig.add_trace(go.Scatter(x=Qg, y=qs[:, 0] * 1e4, name=f"{tr('median', L)}, t = {tt:g}", line=dict(color=COLOR[k], dash=dash, width=2)))
            fig.add_trace(go.Scatter(x=Qg, y=qs[:, 1] * 1e4, name=f"{tr('q995', L)}, t = {tt:g}", line=dict(color="#52514e", dash=dash, width=1)))
        fig.add_vline(x=Q, line_color="#8a8984", line_dash="dot")
        st.plotly_chart(layout(fig, 380, ytitle=tr("y_bp", L), xtitle=tr("x_Q", L), logx=True, logy=True).update_layout(title=tr("curve_Q", L)), use_container_width=True)
    Qs = np.logspace(-1, 2.7, 25); Ts = np.logspace(np.log10(0.125), np.log10(60), 25)
    Z = np.array([[np.log10(1e4 * sum(M.listed_cost_central(qq * 1e6, tt, sigma_d, V, s, fee, Y, dlt))) for qq in Qs] for tt in Ts])
    fig = go.Figure(go.Surface(x=np.log10(Qs), y=np.log10(Ts), z=Z, colorscale="Blues", showscale=False))
    fig.update_layout(scene=dict(xaxis_title="log₁₀ Q (M€)", yaxis_title="log₁₀ t", zaxis_title="log₁₀ ΔP (pb)"), title=tr("surface", L),
                      height=480, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.info(tr("lst_note", L))

# =========================================================================== 2. Actifs non cotés
with tabs[2]:
    st.markdown(tr("unl_intro", L))
    left, right = st.columns([1, 2.2])
    with left:
        st.markdown(f"**{tr('params', L)}**")
        kk = st.selectbox(tr("preset", L), ["RE", "PE"], format_func=lambda a: NAMES[a], key="unl_preset")
        reg = st.radio(" ", [tr("normal_lbl", L), tr("stress_lbl", L)], horizontal=True, key="unl_reg", label_visibility="collapsed")
        f = R["unlisted"][kk]["normal" if reg == tr("normal_lbl", L) else "stress"]
        nu = st.slider(tr("nu", L), 0.05, 5.0, float(round(f["nu"] * 30.4, 2)), 0.05, key=f"nu_{kk}_{reg}")
        mu = st.slider(tr("mu_b", L), -0.8, 0.1, float(round(f["mu_b"], 3)), 0.005, key=f"mu_{kk}_{reg}")
        sg = st.slider(tr("sig_b", L), 0.01, 0.5, float(round(f["sig_b"], 3)), 0.005, key=f"sg_{kk}_{reg}")
        Tl = st.slider(tr("Tleg", L), 0, 365, int(R["unlisted"][kk]["T_leg"]), 5, key=f"tl_{kk}")
        al = st.slider(tr("alpha", L), 50.0, 99.9, 99.5, 0.1, key="unl_alpha") / 100
        ts = st.slider(tr("t_sale", L), int(Tl) + 5, 1000, int(Tl) + 120, 5, key=f"ts_{kk}")
    nud = nu / 30.4
    med = float(M.auction_discount(0.5, ts, Tl, nud, mu, sg)); qa = float(M.auction_discount(al, ts, Tl, nud, mu, sg))
    pfail = float(np.exp(-nud * (ts - Tl))); tmin = M.t_min_unlisted(al, Tl, nud)
    with right:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(tr("m_med", L), f"{fmt(100 * med, 1, L)} %"); m2.metric(tr("m_q", L), f"{fmt(100 * qa, 1, L)} %")
        m3.metric(tr("m_fail", L), f"{fmt(100 * pfail, 1, L)} %"); m4.metric(tr("m_tmin", L), f"{fmt(tmin, 0, L)} {tr('days', L)}")
        tt = np.linspace(Tl + 1, max(1000, ts), 300)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tt, y=100 * M.auction_discount(0.5, tt, Tl, nud, mu, sg), name=tr("median", L), line=dict(color="#0b0b0b", width=2)))
        fig.add_trace(go.Scatter(x=tt, y=100 * M.auction_discount(al, tt, Tl, nud, mu, sg), name=f"{tr('qa', L)} ({fmt(100 * al, 1, L)} %)", line=dict(color=COLOR[kk], width=2)))
        dd = DEALS[kk].dropna(subset=["discount"])
        fig.add_trace(go.Scatter(x=dd["t_total_days"], y=100 * dd["discount"], mode="markers", name=tr("deals", L),
                                 marker=dict(size=4, color=COLOR[kk], opacity=0.25)))
        fig.add_vline(x=Tl, line_dash="dot", line_color="#8a8984"); fig.add_vline(x=ts, line_dash="dash", line_color="#52514e")
        st.plotly_chart(layout(fig, 380, ytitle=tr("y_disc", L), xtitle=tr("t_sale", L)).update_layout(title=tr("curve_t", L)), use_container_width=True)
        disc, _ = M.auction_simulate(ts, Tl, nud, mu, sg)
        fig = go.Figure(go.Histogram(x=100 * disc[~np.isnan(disc)], nbinsx=60, marker_color=COLOR[kk]))
        fig.add_vline(x=100 * qa, line_color="#0b0b0b", line_dash="dash")
        st.plotly_chart(layout(fig, 260, xtitle=tr("y_disc", L)).update_layout(title=tr("hist", L), hovermode="closest"), use_container_width=True)
    st.subheader(tr("nstar_title", L))
    st.markdown(tr("nstar_txt", L))
    st.latex(r"N^{*} = \left\lceil \frac{\ln(1-p)}{\ln F(x)} \right\rceil,\qquad F(x)=\Phi\left(\frac{\ln x-\mu_b}{\sigma_b}\right)")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        xf = st.slider(tr("x_frac", L), 50, 110, 90, 1, key="ns_x") / 100
        pp = st.slider(tr("p_conf", L), 50.0, 99.9, 90.0, 0.5, key="ns_p") / 100
    Nst, F = M.n_star(xf, pp, mu, sg)
    with c2:
        st.metric(tr("m_nstar", L), str(Nst) if Nst else tr("impossible", L))
        if Nst:
            from scipy import stats as _st
            st.metric(tr("m_ndays", L), f"{fmt(Tl + _st.gamma.ppf(0.5, Nst, scale=1 / nud), 0, L)} {tr('days', L)}")
    with c3:
        Ns = np.arange(1, 81)
        fig = go.Figure(go.Scatter(x=Ns, y=1 - F ** Ns, line=dict(color=COLOR[kk], width=2), name="P"))
        fig.add_hline(y=pp, line_dash="dot", line_color="#8a8984")
        st.plotly_chart(layout(fig, 260, xtitle=tr("x_N", L), ytitle="P"), use_container_width=True)

# =========================================================================== 3. Liquidité juridique
with tabs[3]:
    st.markdown(tr("leg_intro", L))
    S = R["synthetic"]
    df = pd.DataFrame([{tr("col_asset", L): NAMES[k], tr("settle", L): S[k]["settle"], "T_leg": S[k]["T_leg"],
                        "t_min,99,5 %": round(S[k]["t_min"], 1)} for k in ALL])
    st.subheader(tr("leg_table", L)); st.dataframe(df, hide_index=True, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(tr("leg_calc", L))
        kl = st.selectbox(tr("preset", L), LISTED, format_func=lambda a: NAMES[a], key="leg_preset")
        Qd = st.number_input(tr("Q", L), 0.1, 5000.0, 10.0, key="leg_Q")
        rho = st.slider(tr("rho", L), 1, 100, 25 if kl in ("CAC", "SPX") else 100, 1, key=f"rho_{kl}") / 100
        Vl = st.number_input(tr("Vlow", L), 0.01, 100000.0, float(round(LP[kl]["V_q005"] / 1e6, 2)), key=f"vl_{kl}")
        Tl2 = st.slider(tr("Tleg", L), 0, 10, int(S[kl]["T_leg"]), 1, key=f"tl2_{kl}")
        tau = Qd / (rho * Vl) / M.TD
        st.metric(tr("m_tmin", L), f"{fmt(Tl2 + tau, 1, L)} {tr('days', L)}")
        st.latex(rf"t_{{\min}} = {Tl2} + \frac{{{Qd:g}}}{{{rho:.2f}\times {Vl:.2f}}}\times\frac{{365}}{{252}} = {Tl2 + tau:.1f}")
    with c2:
        st.subheader(tr("rating_title", L)); st.caption(tr("rating_txt", L))
        ld = st.number_input(tr("legal_days", L), 0.0, 3000.0, 2.0, key="rt_days")
        ob = st.number_input(tr("obs", L), 0.0, 100000.0, 6.0, key="rt_obs")
        a, b = M.letter_time(ld), M.letter_obs(ob)
        r1, r2, r3 = st.columns(3)
        r1.metric(tr("n_leg", L), a); r2.metric(tr("n_obs", L), b); r3.metric(tr("n_fin", L), M.worst(a, b))
        st.table(pd.DataFrame({"": list("ABCDEF"),
                               tr("legal_days", L): ["< 1", "< 3", "< 7", "< 30", "< 365", "≥ 365"],
                               tr("obs", L): ["≥ 100", "≥ 30", "≥ 5", "≥ 1", "≥ 1/7", "< 1/7"]}).set_index(""))

# =========================================================================== 4. Indicateur synthétique
with tabs[4]:
    st.markdown(tr("syn_intro", L))
    st.latex(r"I_1 = 1 - \frac{\ln(1+t_{\min})}{\ln(1+T_{\max})},\quad I_2 = 1 - \frac{\ln(1+\Delta\mathrm{PTV}/\epsilon)}{\ln(1+1/\epsilon)},\quad L = x\,I_1 + (1-x)\,I_2")
    c1, c2 = st.columns([1, 2.2])
    with c1:
        Tmax = st.slider(tr("Tmax", L), 90, 3650, 1095, 5)
        H = st.slider(tr("H", L), 1, 365, 30, 1)
        re_ = st.slider(tr("re", L), 0.0, 20.0, 8.0, 0.5) / 100
        pi_ = st.slider(tr("pi", L), 0.0, 10.0, 2.0, 0.5) / 100
        st.caption(tr("edit", L))
    base = pd.DataFrame({"id": ALL, tr("col_asset", L): [NAMES[k] for k in ALL],
                         tr("c_tmin", L): [round(S[k]["t_min"], 1) for k in ALL], tr("c_dp", L): [round(100 * S[k]["dP995"], 3) for k in ALL]})
    with c2:
        ed = st.data_editor(base, hide_index=True, use_container_width=True, disabled=["id", tr("col_asset", L)], key="syn_ed")
    tmins = ed[tr("c_tmin", L)].astype(float).values; dps = ed[tr("c_dp", L)].astype(float).values / 100
    I1 = np.array([M.score_time(v, Tmax) for v in tmins]); I2 = np.array([M.score_cost(v) for v in dps])
    Sa = np.array([M.score_cost(M.alm_cost(tm, dp, H, re_, pi_)) for tm, dp in zip(tmins, dps)])
    xs = M.x_star(I1, I2, Sa)
    with c1:
        st.metric(tr("xstar_is", L), fmt(xs, 2, L))
        use = st.checkbox(tr("use_xstar", L), True)
        xw = xs if use else st.slider(tr("x", L), 0.0, 1.0, 0.5, 0.01)
    Lv = xw * I1 + (1 - xw) * I2
    out = pd.DataFrame({tr("col_asset", L): [NAMES[k] for k in ALL], "I₁": I1.round(3), "I₂": I2.round(3),
                        tr("col_L", L): Lv.round(3), tr("col_note", L): [M.letter_score(v) for v in Lv]}).sort_values(tr("col_L", L), ascending=False)
    with c2:
        st.dataframe(out, hide_index=True, use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        fig = go.Figure()
        g = np.linspace(0, 1, 60)
        fig.add_trace(go.Contour(x=g, y=g, z=xw * g[None, :] + (1 - xw) * g[:, None], colorscale="Greys", opacity=0.35, showscale=False,
                                 contours=dict(start=0.2, end=0.8, size=0.15, showlabels=True)))
        for i, k in enumerate(ALL):
            fig.add_trace(go.Scatter(x=[I1[i]], y=[I2[i]], mode="markers+text", text=[NAMES[k]], textposition="top center",
                                     marker=dict(size=13, color=COLOR[k], line=dict(color="white", width=2)), name=NAMES[k]))
        fig.update_layout(showlegend=False, title=tr("map", L))
        st.plotly_chart(layout(fig, 430, xtitle="I₁", ytitle="I₂").update_xaxes(range=[0, 1]).update_yaxes(range=[0, 1]).update_layout(hovermode="closest"), use_container_width=True)
    with c4:
        xx = np.linspace(0, 1, 51); fig = go.Figure()
        for i, k in enumerate(ALL):
            fig.add_trace(go.Scatter(x=xx, y=xx * I1[i] + (1 - xx) * I2[i], name=NAMES[k], line=dict(color=COLOR[k])))
        fig.add_vline(x=xw, line_dash="dot")
        st.plotly_chart(layout(fig, 430, xtitle="x", ytitle="L(x)").update_layout(title=tr("sens", L)), use_container_width=True)

# =========================================================================== 5. ALM prévoyance
with tabs[5]:
    st.markdown(tr("alm_intro", L))
    c1, c2 = st.columns([1, 2.2])
    with c1:
        st.markdown(f"**{tr('stress_par', L)}**")
        mort = st.slider(tr("mort", L), 1.0, 3.0, 1.5, 0.05)
        ijm = st.slider(tr("ij", L), 1.0, 4.0, 2.0, 0.1)
        prd = st.slider(tr("prem", L), 0, 60, 20, 1) / 100
        one = st.slider(tr("oneoff", L), 0, 400, 25, 5)
        st.markdown(f"**{tr('alloc', L)}**")
        keys = A["KEYS"]; w = {}
        for kk2 in keys:
            w[kk2] = st.slider(NAMES[kk2], 0.0, 60.0, float(round(100 * A["W0"][kk2], 1)), 0.5, key=f"w_{kk2}")
        st.caption(tr("norm_note", L))
    tot = sum(w.values()) or 1.0
    Wn = {k2: v / tot for k2, v in w.items()}
    Atot = A["A_TOT"]; SH = A["SHOCK"]
    cum = M.simulate_liabilities(mort, ijm, prd, one)
    H_ = [7, 30, 90, 180, 365]
    def mobil(k2, h):
        As = Atot * Wn[k2] * (1 + SH[k2])
        if k2 == "CASH": return As
        if k2 in LISTED:
            p2 = LP[k2]; Tl3 = S[k2]["T_leg"]
            if h <= Tl3 or As <= 0: return 0.0
            rho2 = 0.25 if k2 in ("CAC", "SPX") else 1.0
            x_ = min(As, rho2 * p2["V_q005"] * (h - Tl3) * M.TD / 1e6)
            s_st = p2["spread_bp"] * 1e-4 * np.exp(2.33 * p2["sd_log_s"])
            c_ = p2["fees_bp"] * 1e-4 + s_st / 2 + p2["Y"] * p2["sigma_d_q90"] * (x_ * 1e6 / (p2["V_q005"] * (h - Tl3) * M.TD)) ** p2["delta"]
            return x_ * (1 - min(c_, 1))
        return As * (1 - S[k2]["dP995"]) if h >= S[k2]["t_min"] else 0.0
    lad = {h: {k2: mobil(k2, h) for k2 in keys} for h in H_}
    needs = {h: M.need_at(cum, h) for h in H_}
    Lp = sum(Wn[k2] * (1.0 if k2 == "CASH" else S[k2]["L"]) for k2 in keys)
    with c2:
        mm = np.arange(1, 13); fig = go.Figure()
        for lo, hi, op in ((0.005, 0.995, 0.15), (0.05, 0.95, 0.25), (0.25, 0.75, 0.4)):
            fig.add_trace(go.Scatter(x=np.r_[mm, mm[::-1]], y=np.r_[np.quantile(cum, hi, 0), np.quantile(cum, lo, 0)[::-1]], fill="toself",
                                     fillcolor=f"rgba(227,73,72,{op})", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=mm, y=np.median(cum, 0), name=tr("median", L), line=dict(color="#0b0b0b", width=2)))
        fig.add_trace(go.Scatter(x=mm, y=np.quantile(cum, 0.995, 0), name=tr("q995", L), line=dict(color="#0b0b0b", dash="dash")))
        st.plotly_chart(layout(fig, 300, xtitle=tr("month", L), ytitle=tr("need", L)), use_container_width=True)
        fig = go.Figure()
        for k2 in ["CASH", "UST", "OATFR", "CAC", "SPX", "TTE", "LVMH", "RE", "PE"]:
            fig.add_trace(go.Bar(x=[f"{h} j" if L == "fr" else f"{h} d" if L == "en" else f"{h} T" for h in H_], y=[lad[h][k2] for h in H_],
                                 name=NAMES[k2], marker_color=COLOR[k2]))
        fig.add_trace(go.Scatter(x=[f"{h} j" if L == "fr" else f"{h} d" if L == "en" else f"{h} T" for h in H_], y=[needs[h] for h in H_],
                                 mode="markers", marker=dict(symbol="diamond", size=12, color="#0b0b0b"), name=tr("need_q", L)))
        fig.update_layout(barmode="stack", title=tr("ladder", L))
        st.plotly_chart(layout(fig, 400, ytitle="M€"), use_container_width=True)
        rl = {h: sum(lad[h].values()) / needs[h] if needs[h] > 0 else np.inf for h in H_}
        cols = st.columns(len(H_) + 1)
        for i, h in enumerate(H_):
            cols[i].metric(f"{tr('RL', L)} {h}", "∞" if not np.isfinite(rl[h]) else fmt(rl[h], 1, L))
        cols[-1].metric(tr("Lp", L), fmt(Lp, 2, L))
        if any(np.isfinite(v) and v < 1 for v in rl.values()):
            st.error(tr("alm_warn", L))
        else:
            st.success(tr("alm_ok", L))

# =========================================================================== 6. Données
with tabs[6]:
    st.caption(tr("data_intro", L))
    sel = st.multiselect(tr("choose", L), LISTED, default=LISTED, format_func=lambda a: NAMES[a])
    fig = go.Figure()
    stress = W["stress"] > 0.35
    for a_, b_ in zip(W.index[stress & ~stress.shift(1, fill_value=False)], W.index[stress & ~stress.shift(-1, fill_value=False)]):
        fig.add_vrect(x0=a_, x1=b_, fillcolor="#d9d8d3", opacity=0.5, line_width=0)
    for k3 in sel:
        sr = W[f"{k3}_price"]; fig.add_trace(go.Scatter(x=W.index, y=100 * sr / sr.iloc[0], name=NAMES[k3], line=dict(color=COLOR[k3], width=1.6)))
    st.plotly_chart(layout(fig, 400, ytitle=tr("base100", L)), use_container_width=True)
    c1, c2 = st.columns(2)
    for col, k3 in ((c1, "RE"), (c2, "PE")):
        dd = DEALS[k3].dropna(subset=["discount"])
        fig = go.Figure(go.Scatter(x=dd["date"], y=100 * dd["discount"], mode="markers", marker=dict(size=5, color=COLOR[k3], opacity=0.4), name=NAMES[k3]))
        col.plotly_chart(layout(fig, 300, ytitle=tr("y_disc", L)).update_layout(title=f"{tr('deals', L)} — {NAMES[k3]}", hovermode="closest"), use_container_width=True)
        col.download_button(f"{tr('download', L)} {k3.lower()}_deals.csv", DEALS[k3].to_csv(index=False).encode(), f"{k3.lower()}_deals.csv", "text/csv", key=f"dl_{k3}")

# =========================================================================== 7. Codes Python
with tabs[7]:
    st.markdown(tr("code_intro", L))
    order = ["gen_data.py", "analysis.py", "alm.py", "style.py", "content.py", "build_docx.py", "omml.py"]
    desc = tr("code_desc", L)
    st.dataframe(pd.DataFrame({tr("code_order", L): ["1", "2", "3", "—", "4", "5", "—"], tr("code_file", L): order, "": [desc[f] for f in order]}),
                 hide_index=True, use_container_width=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in order:
            z.write(os.path.join(CODE, fn), fn)
    st.download_button(tr("code_zip", L), buf.getvalue(), "codes_article_liquidite.zip", "application/zip")
    for fn in order:
        with st.expander(f"{fn} — {desc[fn]}"):
            src = open(os.path.join(CODE, fn), encoding="utf8").read()
            st.code(src, language="python", line_numbers=True)

st.markdown("---")
st.caption(f"© 2026 Matthieu Moreau, Frédéric Planchet — {tr('date', L)} — {tr('disclaimer', L)}")
