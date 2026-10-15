"""
Contenu de l'article (commun aux formats ArXiv et BMI).
Les valeurs numériques sont lues dans results/*.json : le texte reste cohérent avec les calculs.
Syntaxe : $...$ = mathématiques en ligne ; **gras** ; *italique* ; @cle@ = valeur de V.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
R = json.load(open(os.path.join(RES, "results.json"), encoding="utf8"))
A = json.load(open(os.path.join(RES, "alm.json"), encoding="utf8"))
P = json.load(open(os.path.join(HERE, "..", "data", "params.json"), encoding="utf8"))

LISTED = ["CAC", "SPX", "OATFR", "UST", "TTE", "LVMH"]
ALL = LISTED + ["RE", "PE"]
NAME = {"CAC": "ETF CAC 40", "SPX": "ETF S&P 500", "OATFR": "OAT 10 ans (France)", "UST": "Treasury 10 ans (États-Unis)",
        "TTE": "Obligation TotalEnergies 10 ans", "LVMH": "Obligation LVMH 10 ans",
        "RE": "Immeuble de bureaux (détention physique)", "PE": "Private Equity non coté (small caps françaises)"}
CLASS = {"CAC": "Actions", "SPX": "Actions", "OATFR": "Obligations souveraines", "UST": "Obligations souveraines",
         "TTE": "Obligations d'entreprise", "LVMH": "Obligations d'entreprise", "RE": "Immobilier", "PE": "Private Equity"}


def fr(x, nd=2):
    if x is None:
        return "–"
    s = f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")
    return s.replace("-", "−") if x < 0 else s

def pct(x, nd=1): return fr(100 * x, nd) + " %"

S = R["synthetic"]; L = R["listed"]; U = R["unlisted"]; M = R["meta"]
xs = M["x_star"]
V = dict(
    xstar=fr(xs, 2), one_m_xstar=fr(1 - xs, 2),
    N_days=fr(2869, 0), QSTAR="10 M€",
    re_nu=fr(U["RE"]["normal"]["nu"] * 30.4, 2), re_nu_s=fr(U["RE"]["stress"]["nu"] * 30.4, 2),
    pe_nu=fr(U["PE"]["normal"]["nu"] * 30.4, 2), pe_nu_s=fr(U["PE"]["stress"]["nu"] * 30.4, 2),
    re_tmin_n=fr(U["RE"]["t_min995_normal"], 0), re_tmin_s=fr(U["RE"]["t_min995_stress"], 0),
    pe_tmin_n=fr(U["PE"]["t_min995_normal"], 0), pe_tmin_s=fr(U["PE"]["t_min995_stress"], 0),
    re_km=fr(U["RE"]["km_median"], 0), pe_km=fr(U["PE"]["km_median"], 0),
    re_km90=fr(U["RE"]["km_q90"], 0), pe_km90=fr(U["PE"]["km_q90"], 0),
    re_tfirst=fr(U["RE"]["t_first_med_normal"], 0), pe_tfirst=fr(U["PE"]["t_first_med_normal"], 0),
    re_np50=pct(U["RE"]["dP_np_q50"]), re_np995=pct(U["RE"]["dP_np_q995"]),
    pe_np50=pct(U["PE"]["dP_np_q50"]), pe_np995=pct(U["PE"]["dP_np_q995"]),
    re_np50s=pct(U["RE"]["dP_np_q50_stress"]), pe_np50s=pct(U["PE"]["dP_np_q50_stress"]),
    re_ci=f"[{pct(U['RE']['dP_np_q995_ci'][0])} ; {pct(U['RE']['dP_np_q995_ci'][1])}]",
    pe_ci=f"[{pct(U['PE']['dP_np_q995_ci'][0])} ; {pct(U['PE']['dP_np_q995_ci'][1])}]",
    re_a=fr(U["RE"]["geltner_a_hat"], 2), pe_a=fr(U["PE"]["geltner_a_hat"], 2),
    re_sobs=pct(U["RE"]["sigma_obs_ann"]), re_sun=pct(U["RE"]["sigma_unsm_ann"]),
    pe_sobs=pct(U["PE"]["sigma_obs_ann"]), pe_sun=pct(U["PE"]["sigma_unsm_ann"]),
    re_mec=fr(U["RE"]["MEC"], 2), pe_mec=fr(U["PE"]["MEC"], 2),
    re_N=str(M["N_star"]["RE_normal"]["N"]), re_Ns=str(M["N_star"]["RE_stress"]["N"]),
    pe_N=str(M["N_star"]["PE_normal"]["N"]), pe_Ns=str(M["N_star"]["PE_stress"]["N"]),
    re_F=fr(M["N_star"]["RE_normal"]["F"], 3), pe_F=fr(M["N_star"]["PE_normal"]["F"], 3),
    re_Ndays=fr(M["N_star"]["RE_normal"]["days"], 0), pe_Ndays=fr(M["N_star"]["PE_normal"]["days"], 0),
    cac_Y=fr(L["CAC"]["Y_hat"], 2), cac_d=fr(L["CAC"]["delta_hat"], 3), cac_r2=fr(L["CAC"]["r2"], 2),
    d_min=fr(min(L[k]["delta_hat"] for k in LISTED), 2), d_max=fr(max(L[k]["delta_hat"] for k in LISTED), 2),
    tte_roll=fr(L["TTE"]["roll_bp"], 1), lvmh_roll=fr(L["LVMH"]["roll_bp"], 1),
    tte_sp=fr(L["TTE"]["spread_med_bp"], 1), lvmh_sp=fr(L["LVMH"]["spread_med_bp"], 1),
    cac_t1=fr(L["CAC"]["dP_np_t1_q50_bp"], 1), cac_t1s=fr(L["CAC"]["dP_np_t1_q995_bp"], 1),
    cac_t20=fr(L["CAC"]["dP_np_t20_q50_bp"], 1), tte_t1=fr(L["TTE"]["dP_np_t1_q50_bp"], 1),
    tte_t1s=fr(L["TTE"]["dP_np_t1_q995_bp"], 1), tte_t20=fr(L["TTE"]["dP_np_t20_q50_bp"], 1),
    ust_t1=fr(L["UST"]["dP_np_t1_q50_bp"], 1), oat_t1=fr(L["OATFR"]["dP_np_t1_q50_bp"], 1),
    ratio_tte1=fr(M["ratio_liq_val"]["TTE"]["1"], 2), ratio_cac1=fr(M["ratio_liq_val"]["CAC"]["1"], 2),
    ratio_cac20=fr(M["ratio_liq_val"]["CAC"]["20"], 3), ratio_re180=fr(M["ratio_liq_val"]["RE"]["180"], 2),
    ratio_pe180=fr(M["ratio_liq_val"]["PE"]["180"], 2), ratio_pe365=fr(M["ratio_liq_val"]["PE"]["365"], 2),
    ratio_re365=fr(M["ratio_liq_val"]["RE"]["365"], 2),
    L_ust=fr(S["UST"]["L"], 2), L_oat=fr(S["OATFR"]["L"], 2), L_cac=fr(S["CAC"]["L"], 2), L_spx=fr(S["SPX"]["L"], 2),
    L_tte=fr(S["TTE"]["L"], 2), L_lvmh=fr(S["LVMH"]["L"], 2), L_re=fr(S["RE"]["L"], 2), L_pe=fr(S["PE"]["L"], 2),
    A_TOT=fr(A["A_TOT"], 0), FP=fr(A["FP"], 0),
    need30=fr(A["need"]["30"]["str_q995"], 1), need365=fr(A["need"]["365"]["str_q995"], 1),
    need30b=fr(A["need"]["30"]["base_q995"], 1), need365b=fr(A["need"]["365"]["base_q50"], 1),
    LR7=fr(A["LR"]["7"], 1), LR30=fr(A["LR"]["30"], 1), LR365=fr(A["LR"]["365"], 1),
    Xstar=fr(A["X_star"], 0), Xstar_pct=pct(A["X_star"] / A["A_TOT"], 0), mob30=fr(A["mob30"], 0),
    liq_opt=fr(A["liquidation"]["opt_liq"] + A["liquidation"]["opt_carry"], 2),
    liq_pr=fr(A["liquidation"]["pr_liq"] + A["liquidation"]["pr_carry"], 2),
    liq_gain=pct(1 - (A["liquidation"]["opt_liq"] + A["liquidation"]["opt_carry"]) / (A["liquidation"]["pr_liq"] + A["liquidation"]["pr_carry"]), 0),
    liq_opt_l=fr(A["liquidation"]["opt_liq"] * 1000, 0), liq_pr_l=fr(A["liquidation"]["pr_liq"] * 1000, 0),
    sold=fr(A["liquidation"]["opt_sold"], 1),
    cur_net=pct(A["alloc_current"]["net"], 2), cur_vol=pct(A["alloc_current"]["vol"], 1), cur_Lp=fr(A["alloc_current"]["Lp"], 2),
    c8_net=pct(A["alloc_6_c"]["net"], 2), nc8_net=pct(A["alloc_6_nc"]["net"], 2),
    c8_Lp=fr(A["alloc_6_c"]["Lp"], 2), nc8_Lp=fr(A["alloc_6_nc"]["Lp"], 2),
    cost_con=fr((A["alloc_6_nc"]["net"] - A["alloc_6_c"]["net"]) * 1e4, 0),
    nc8_re=pct(A["alloc_6_nc"]["w"][7], 0), c8_re=pct(A["alloc_6_c"]["w"][7], 0),
    eff_gain=fr((A["frontier_c"][5]["net"] - A["alloc_current"]["net"]) * 1e4, 0),
)

def sub(s):
    for k, v in V.items():
        s = s.replace("@" + k + "@", v)
    assert "@" not in s.replace("@@", ""), s[:120]
    return s

B = []      # liste des blocs
def h1(t): B.append(("h1", t))
def h2(t): B.append(("h2", t))
def h3(t): B.append(("h3", t))
def p(t): B.append(("p", sub(t)))
def eq(t, lab=None): B.append(("eq", t, lab))
def bl(*items): B.append(("bullets", [sub(i) for i in items]))
def en(*items): B.append(("enum", [sub(i) for i in items]))
def fig(f, cap, w=16.0): B.append(("fig", f, sub(cap), w))
def tab(head, rows, cap, widths=None, note=None, font=None): B.append(("table", head, rows, sub(cap), widths, note and sub(note), font))

META = dict(
    title="Mesurer la liquidité des actifs financiers : liquidité juridique, liquidité financière et indicateur synthétique. Application à la gestion actif-passif d'un assureur prévoyance",
    title_short="Liquidité juridique, liquidité financière et indicateur synthétique",
    authors=[("Matthieu MOREAU", "Actuaire, consultant."),
             ("Frédéric PLANCHET", "Professeur à l'ISFA (Université Lyon 1, Laboratoire SAF) et actuaire associé chez Prim'Act.")],
    version="Version 1.0 du 15/10/2026",
    abstract_fr=sub(
        "Cet article propose un cadre unifié de mesure de la liquidité des actifs détenus par les institutions financières. "
        "Nous distinguons la **liquidité juridique** (ou physique), contrainte par le droit et l'organisation des marchés — délais de règlement-livraison, purge des droits de préemption, actes notariés, agréments —, "
        "et la **liquidité financière**, décrite par la surface probabiliste $\\Delta\\mathrm{PTV}_{\\alpha}(Q,t)$ de la décote subie à la vente d'une quantité $Q$ dans un délai $t$. "
        "Chaque dimension est estimée par des méthodes paramétriques (loi d'impact en racine carrée, modèle d'enchère à arrivée poissonnienne d'acheteurs estimé par maximum de vraisemblance, loi exponentielle des délais) "
        "et non paramétriques (fourchettes, estimateurs de Roll, d'Amihud, de Kyle, MEC, bootstrap historique, Kaplan-Meier, quantiles à noyau). "
        "L'étude porte sur un historique fictif calibré (2015-2025) de huit actifs : ETF CAC 40 et S&P 500, OAT et Treasury 10 ans, obligations TotalEnergies et LVMH 10 ans, un immeuble de bureaux et du Private Equity small caps. "
        "Nous construisons un indicateur synthétique $L = x\\,I_1 + (1-x)\\,I_2$ dont le poids $x^{*} = @xstar@$ est calibré sur le coût actif-passif d'une mobilisation de trésorerie, et une notation lettrée de A à F. "
        "L'application à un assureur prévoyance montre que le risque de liquidité y est d'abord un risque de délai sur les actifs non cotés, que la stratégie de liquidation optimale réduit de @liq_gain@ le coût d'une crise de trésorerie et que la contrainte de liquidité ne coûte que @cost_con@ points de base de rendement sur la frontière efficiente."),
    keywords_fr="Liquidité, risque de liquidité, coût de liquidité, surface ΔPTV, liquidité juridique, impact de marché, Private Equity, immobilier, gestion actif-passif, assurance prévoyance, Solvabilité II",
    abstract_en=sub(
        "This paper proposes a unified framework to measure the liquidity of assets held by financial institutions. "
        "We separate **legal (physical) liquidity**, constrained by law and market organisation (settlement cycles, pre-emption rights, notarial deeds, transfer approvals), "
        "from **financial liquidity**, described by the probabilistic surface $\\Delta\\mathrm{PTV}_{\\alpha}(Q,t)$ of the discount incurred when selling an amount $Q$ within a delay $t$. "
        "Both dimensions are estimated with parametric methods (square-root impact law, Poisson-arrival auction model fitted by maximum likelihood, exponential delays) "
        "and non-parametric ones (spreads, Roll, Amihud and Kyle estimators, market efficiency coefficient, historical bootstrap, Kaplan-Meier, kernel quantiles). "
        "We study a calibrated fictitious history (2015-2025) of eight assets: CAC 40 and S&P 500 ETFs, French and US 10-year government bonds, TotalEnergies and LVMH 10-year bonds, an office building and French small-cap private equity. "
        "We build a synthetic indicator $L = x\\,I_1 + (1-x)\\,I_2$ whose weight $x^{*} = @xstar@$ is calibrated on the asset-liability cost of raising cash, together with an A-to-F rating. "
        "Applied to a protection (prévoyance) insurer, the framework shows that liquidity risk is primarily a delay risk on unlisted assets, that the optimal liquidation strategy cuts the cost of a cash crisis by @liq_gain@ and that the liquidity constraint only costs @cost_con@ basis points of return on the efficient frontier."),
    keywords_en="Liquidity, liquidity risk, liquidity cost, ΔPTV surface, legal liquidity, market impact, private equity, real estate, asset-liability management, protection insurance, Solvency II",
    jel="G11, G12, G22, G23, C14, C15, C41",
)

# =============================================================================
h1("Introduction")
p("La liquidité d'un actif est classiquement définie comme sa capacité à être acheté ou vendu rapidement, si nécessaire en quantité importante, sans variation significative de son prix [Black, 1971 ; Demsetz, 1968]. "
  "Derrière cette définition familière se cachent trois dimensions distinctes — la quantité échangée $Q$, le délai disponible $t$ et la variation de prix $\\Delta P$ qui en résulte — et une difficulté pratique majeure : "
  "les indicateurs usuels — fourchette [Demsetz, 1968 ; Amihud et Mendelson, 1986], coefficient de sensibilité de Gresse [Gresse, 1997], $\\lambda$ de Kyle [Kyle, 1985], ratio d'Amihud [Amihud, 2002], *Market Efficiency Coefficient* [Hasbrouck et Schwartz, 1988] — n'en couvrent qu'une ou deux, et la plupart ne sont calculables que pour des titres cotés [Le Saout, 1999, 2000 ; Moreau, 2024]. "
  "Les approches de valeur en risque ajustée de la liquidité [Bangia et al., 1998 ; Le Saout, 2002] et de décomposition des spreads de crédit [Longstaff et al., 2005] intègrent la liquidité dans la mesure des risques de marché, mais restent attachées aux titres cotés.")
p("Pour un assureur, la question n'est pas académique. La directive Solvabilité II définit le risque de liquidité comme le risque de ne pas pouvoir réaliser ses placements et autres actifs pour honorer ses engagements financiers au moment où ils deviennent exigibles (directive 2009/138/CE, art. 13). "
  "La révision de la directive, préparée par l'avis de l'EIOPA [EIOPA, 2020] et adoptée fin 2024, renforce les exigences de plans de gestion du risque de liquidité [Directive (UE) 2025/2], alors même que les incitations réglementaires — loi Industrie Verte de 2023 en tête — poussent les organismes vers des actifs non cotés (Private Equity, infrastructures, immobilier) dont la liquidité est, par nature, difficile à quantifier.")
p("Dans des travaux antérieurs [Moreau, 2024 ; Moreau et Planchet, 2025], nous avons proposé l'indicateur $\\Delta\\mathrm{PTV}_{\\alpha}$, une surface probabiliste donnant le coût unitaire de liquidité en fonction de $(Q,t)$ au seuil $\\alpha$. "
  "Le présent article prolonge ce travail sur quatre points. "
  "**Premièrement**, nous séparons explicitement deux natures de liquidité : la *liquidité juridique* — ou physique — qui résulte des délais incompressibles imposés par le droit et l'organisation des marchés (règlement-livraison en T+2, délai de purge du droit de préemption urbain, acte authentique, agrément des cessions de parts), et sur laquelle l'investisseur n'a pas de prise ; "
  "et la *liquidité financière*, qui mesure la décote à la vente (ou la surcote à l'achat) imputable à l'insuffisance de contreparties, fonction de $Q$ et de $t$. "
  "**Deuxièmement**, nous estimons chaque dimension par deux familles de méthodes, paramétriques et non paramétriques, afin d'en éprouver la robustesse. "
  "**Troisièmement**, nous construisons un indicateur synthétique de la forme $L = x\\,I_1 + (1-x)\\,I_2$, dont le poids $x$ est calibré, et non fixé à dire d'expert, sur le coût actif-passif d'une mobilisation de trésorerie. "
  "**Quatrièmement**, nous appliquons le cadre à la gestion actif-passif (ALM) d'un assureur prévoyance, dont le passif — prestations d'incapacité, d'invalidité et de décès — présente un profil de liquidité très différent de celui de l'épargne.")
p("Faute d'accès à des données de transaction homogènes pour l'ensemble des classes d'actifs, l'étude repose sur un **historique fictif mais calibré** de 2015 à 2025 pour huit actifs : deux ETF actions (CAC 40, S&P 500), deux obligations souveraines 10 ans (OAT, Treasury), deux obligations d'entreprise 10 ans (TotalEnergies, LVMH), un immeuble de bureaux détenu en direct et une participation de Private Equity non coté (small caps françaises). "
  "Les sources ayant servi à la calibration et la méthode mathématique de génération sont détaillées en annexe A ; les démonstrations sont en annexe B.")
p("L'article est organisé comme suit. La section 2 formalise le problème. La section 3 décrit la génération des données. La section 4 présente l'analyse des deux liquidités et l'indicateur synthétique. La section 5 développe l'application ALM prévoyance. La section 6 conclut et la section 7 synthétise les résultats opérationnels.")

# =============================================================================
h1("Problématique et cadre formel")
h2("Coût de liquidité et surface ΔPTV")
p("Considérons un investisseur qui détient un actif de valeur de référence $V_0$ (milieu de fourchette pour un titre coté, valeur d'expertise ou valeur liquidative publiée pour un actif non coté) et qui doit en céder un montant $Q$ (en euros) dans un délai $t$ (en jours calendaires), en suivant la meilleure stratégie d'exécution disponible. "
  "Notons $\\Pi(Q,t)$ le produit net de cession. Le **coût unitaire de liquidité** est la variable aléatoire")
eq(r"\Delta P(Q,t) = 1 - \frac{\Pi(Q,t)}{Q}, \qquad Q>0,\; t>0,", "eq:dP")
p("et l'indicateur $\\Delta\\mathrm{PTV}_{\\alpha}$ est son quantile de niveau $\\alpha$ :")
eq(r"\Delta\mathrm{PTV}_{\alpha}(Q,t) = \inf\left\{ x \in \mathbb{R} \;:\; \mathbb{P}\left(\Delta P(Q,t) \le x\right) \ge \alpha \right\}.", "eq:ptv")
p("Nous retenons, comme dans [Moreau, 2024], la médiane ($\\alpha = 50\\,\\%$, scénario central) et le quantile $\\alpha = 99{,}5\\,\\%$ (scénario stressé), cohérent avec le seuil de Solvabilité II. "
  "La surface vérifie quatre propriétés structurelles qui servent de garde-fous aux estimations :")
eq(r"\lim_{Q\to 0}\Delta P(Q,t)=0, \qquad \lim_{t\to+\infty}\Delta P(Q,t)=0, \qquad \frac{\partial\,\Delta\mathrm{PTV}_{\alpha}}{\partial Q}\ge 0, \qquad \frac{\partial\,\Delta\mathrm{PTV}_{\alpha}}{\partial t}\le 0.", "eq:axiomes")
p("Pour les titres cotés, le coût se décompose en frais $f$, demi-fourchette $s/2$ et impact de marché $\\mathcal{I}(Q,t)$ ; pour les actifs non cotés, il s'interprète comme l'écart entre le prix de transaction et la valeur publiée.")
eq(r"\Delta P(Q,t) = f + \frac{s}{2} + \mathcal{I}(Q,t) + \eta, \qquad \mathbb{E}[\eta]=0.", "eq:decomp")

h2("Liquidité juridique et liquidité financière")
p("Le coût de liquidité n'est défini que si la cession est *possible* dans le délai $t$. Or, pour de nombreux actifs, un délai minimal est imposé par le droit : règlement-livraison en T+2 pour les titres européens (règlement (UE) n° 909/2014, art. 5), en T+1 pour les Treasuries et, depuis mai 2024, pour les actions américaines ; "
  "délai de deux mois laissé à la commune pour exercer son droit de préemption urbain après déclaration d'intention d'aliéner (code de l'urbanisme, art. L213-2), auquel s'ajoutent la levée des conditions suspensives et la signature de l'acte authentique pour un immeuble ; "
  "agrément du gérant, droits de préemption statutaires et documentation de transfert pour une participation de Private Equity. "
  "Nous appelons ce délai incompressible $T_{\\mathrm{leg}}$ et définissons le **délai minimal de cession** au seuil $\\alpha$ :")
eq(r"t_{\min,\alpha}(Q) = T_{\mathrm{leg}} + \tau_{\alpha}(Q),", "eq:tmin")
p("où $\\tau_{\\alpha}(Q)$ est le quantile $\\alpha$ du délai nécessaire pour trouver les contreparties (exécution pour un titre coté, commercialisation pour un actif non coté). "
  "La **liquidité juridique** est mesurée par $t_{\\min,\\alpha}$, la **liquidité financière** par $\\Delta\\mathrm{PTV}_{\\alpha}$ évalué au plus tôt, c'est-à-dire en $t = t_{\\min,\\alpha}(Q)$. "
  "Cette séparation formalise l'intuition selon laquelle la liquidité totale additionne une composante sur laquelle l'investisseur ne peut agir (le droit) et une composante économique sur laquelle il peut agir en communiquant sur l'actif et en facilitant le passage de la valeur au prix.")

h2("Observabilité, profondeur de la demande et nombre d'acheteurs")
p("Un actif est économiquement peu liquide lorsque sa valeur est peu observable (peu de participants, peu de transactions) et lorsque la dispersion des prix les plus probables — les meilleures offres effectivement reçues — est élevée. "
  "Si $N$ acheteurs potentiels formulent des offres indépendantes $X_j = V_0\\,e^{\\mu_b + \\sigma_b \\varepsilon_j}$, $\\varepsilon_j \\sim \\mathcal{N}(0,1)$, le prix obtenu est le maximum $M_N = \\max_{j \\le N} X_j$ et")
eq(r"\mathbb{P}\left(M_N \ge x\,V_0\right) = 1 - F(x)^{N}, \qquad F(x) = \Phi\left(\frac{\ln x - \mu_b}{\sigma_b}\right).", "eq:maxN")
p("La question « combien d'acheteurs faut-il pour obtenir, avec une probabilité d'au moins $p$, un prix au moins égal à une fraction $x$ de la valeur ? » admet donc la réponse explicite")
eq(r"N^{*}(x,p) = \left\lceil \frac{\ln(1-p)}{\ln F(x)} \right\rceil,", "eq:Nstar")
p("que nous évaluons en section 4.3 pour $x = p = 90\\,\\%$. Elle relie directement l'observabilité (nombre de participants par unité de temps) à la liquidité financière.")

h2("Liquidité et incertitude de valeur")
p("Une objection naturelle est que la variation de prix liée à la liquidité est souvent négligeable devant la variation de la valeur elle-même pendant le délai de vente. Nous testons cette hypothèse par le rapport")
eq(r"\rho(t) = \frac{\Delta\mathrm{PTV}_{50\%}(Q^{*},t)}{\sigma\sqrt{t/365}},", "eq:ratio")
p("où $\\sigma$ est la volatilité annuelle de la valeur (dé-lissée pour les actifs non cotés). Un rapport inférieur à 1 signifie que le coût de liquidité est dominé par le risque de valeur.")

h2("Questions de recherche")
en("Comment mesurer séparément la liquidité juridique et la liquidité financière d'actifs aussi différents que des ETF, des obligations, un immeuble et du Private Equity ?",
   "Les méthodes paramétriques et non paramétriques conduisent-elles aux mêmes ordres de grandeur ?",
   "Comment agréger ces deux mesures dans un indicateur unique $L = x\\,I_1 + (1-x)\\,I_2$, avec un poids $x$ justifié ?",
   "Quelles conséquences pour le pilotage actif-passif d'un assureur prévoyance : matelas de liquidité, stratégie de liquidation et allocation stratégique ?")

# =============================================================================
h1("Génération des données")
h2("Principe et périmètre")
p("Les historiques sont générés au pas quotidien (jours ouvrés, @N_days@ dates du 2 janvier 2015 au 31 décembre 2025) pour les six actifs cotés et au pas trimestriel pour les deux actifs non cotés, complétés par trois jeux de microdonnées : "
  "un fichier de transactions obligataires de gré à gré, un journal fictif de 9 000 ordres exécutés par l'assureur (*méta-ordres*) et deux bases de transactions sur actifs non cotés (650 cessions de bureaux et 420 cessions secondaires de Private Equity). "
  "La génération est conçue pour reproduire des faits stylisés documentés — niveaux annuels des indices et des taux, épisodes de stress (yuan 2015, Brexit 2016, Covid-19 2020, Ukraine et inflation 2022, SVB 2023, choc tarifaire 2025), fourchettes et volumes typiques, lissage des valorisations d'expertise, décotes du marché secondaire — sans prétendre restituer les séries réelles. "
  "Tous les chiffres de cet article sont donc **illustratifs** ; la méthode, en revanche, s'applique telle quelle à des données réelles.")
rows = [
    ["ETF CAC 40", "ETF UCITS coté Euronext Paris (EUR)", "Quotidien", "GJR-GARCH(1,1)-t, pont annuel, carnet"],
    ["ETF S&P 500", "ETF UCITS coté Euronext Paris (EUR)", "Quotidien", "GJR-GARCH(1,1)-t, pont annuel, carnet"],
    ["OAT 10 ans", "Obligation à maturité constante 10 ans", "Quotidien", "Ornstein-Uhlenbeck autour d'ancrages"],
    ["Treasury 10 ans", "Obligation à maturité constante 10 ans (USD)", "Quotidien", "Ornstein-Uhlenbeck autour d'ancrages"],
    ["TotalEnergies 10 ans", "OAT + spread de crédit (CIR), gré à gré", "Quotidien + transactions", "CIR, Poisson des transactions"],
    ["LVMH 10 ans", "OAT + spread de crédit (CIR), gré à gré", "Quotidien + transactions", "CIR, Poisson des transactions"],
    ["Immeuble de bureaux", "Île-de-France, valeur ≈ 60 M€", "Trimestriel + transactions", "Valeur latente, lissage de Geltner, enchères"],
    ["Private Equity", "Participation small caps (France), ≈ 30 M€ en 2015", "Trimestriel + transactions", "Valeur latente, NAV lissée, enchères"],
]
tab(["Actif", "Description", "Fréquence", "Modèle générateur"], rows,
    "Périmètre des données fictives générées (détails et sources en annexe A).", [3.3, 5.4, 3.2, 4.6])

h2("Actifs cotés")
p("Les rendements des ETF suivent un modèle GJR-GARCH(1,1) à innovations de Student [Bollerslev, 1986 ; Glosten et al., 1993], amplifié par un facteur de stress exogène pendant les épisodes de crise et conditionné, année par année, à reproduire les niveaux de clôture annuels de référence (pont de dérive). "
  "Les taux souverains 10 ans sont modélisés par un processus d'Ornstein-Uhlenbeck autour d'une tendance interpolant les moyennes annuelles observées (de −0,15 % à 3,35 % pour l'OAT, de 0,89 % à 4,30 % pour le Treasury). "
  "Les spreads de crédit de TotalEnergies et LVMH suivent un processus de Cox-Ingersoll-Ross dont la moyenne de long terme augmente en période de stress. "
  "Le rendement quotidien d'une obligation à maturité constante est approché au second ordre à partir de la duration modifiée et de la convexité. "
  "Pour chaque actif coté, on génère également le volume quotidien, la fourchette relative et le déséquilibre d'ordres signé, ce qui permet de calculer l'ensemble des indicateurs de microstructure (figures 1 à 4).")
fig("f01_prix_cotes", "Figure 1 – Historiques fictifs des actifs cotés (base 100 au 2 janvier 2015). Les zones grisées signalent les épisodes de stress.")
fig("f02_taux_spreads", "Figure 2 – Taux souverains 10 ans et spreads de crédit des obligations d'entreprise.")
fig("f04_fourchettes", "Figure 3 – Fourchettes affichées (échelle logarithmique) : la liquidité financière se dégrade dans chaque épisode de stress.")
rows = []
for k in LISTED:
    o = L[k]
    rows.append([NAME[k], pct(o["sigma_ann"]), fr(o["spread_med_bp"], 1), fr(o["spread_q995_bp"], 1),
                 (fr(o["adv_eur"] / 1e6, 0) if o["adv_eur"] < 1e10 else fr(o["adv_eur"] / 1e9, 0) + " Md")])
tab(["Actif", "Volatilité annuelle", "Fourchette médiane (pb)", "Fourchette q99,5 % (pb)", "Volume quotidien médian (M€)"], rows,
    "Statistiques descriptives des actifs cotés générés.", [5.4, 2.6, 2.8, 2.8, 2.9],
    note="Le volume des ETF inclut les échanges sur carnet et par demande de prix (RFQ) ; celui des obligations, les échanges de gré à gré entre intermédiaires et clients.")

h2("Actifs non cotés")
p("Pour l'immeuble et le Private Equity, on génère d'abord une valeur « vraie » latente (trimestrielle), puis la valeur publiée selon le modèle de lissage de Geltner [Geltner, 1991] :")
eq(r"V^{\mathrm{pub}}_{q} = a\,V_{q} + (1-a)\,V^{\mathrm{pub}}_{q-1}, \qquad 0<a\le 1,", "eq:geltner")
p("avec $a = 0{,}45$ pour l'expertise immobilière et $a = 0{,}35$ pour la valeur liquidative du Private Equity (figure 4). "
  "Les transactions sont ensuite simulées par un **modèle d'enchère à arrivée poissonnienne d'acheteurs** : un vendeur qui commercialise son actif pendant une durée $m$ (au-delà du délai juridique) reçoit $N \\sim \\mathcal{P}(\\nu m)$ offres indépendantes log-normales et cède au mieux-disant ; si aucune offre n'est reçue, la vente échoue (observation censurée). "
  "L'intensité $\\nu$ et la moyenne des offres $\\mu_b$ dépendent du régime de marché (normal ou stressé). Ce modèle a l'avantage de produire endogènement la relation décroissante entre délai et décote observée empiriquement sur l'immobilier [Lin et Vandell, 2007] et sur le marché secondaire du Private Equity [Mende et al., 2016].")
fig("f03_non_cotes", "Figure 4 – Valeur latente et valeur publiée (lissée) de l'immeuble de bureaux et de la participation de Private Equity.")

# =============================================================================
h1("Analyse de la liquidité")
h2("Liquidité juridique : délais incompressibles et délais de cession")
h3("Délais juridiques")
rows = [[NAME[k], S[k]["settle"], fr(S[k]["T_leg"], 0)] for k in ALL]
tab(["Actif", "Contrainte juridique dominante", "T_leg (jours)"], rows,
    "Délais juridiques minimaux de transfert de propriété et de mise à disposition des fonds.", [6.2, 7.0, 2.6],
    note="Le passage au règlement T+1 dans l'Union européenne est prévu pour le 11 octobre 2027 [ESMA, 2024]. Pour l'immeuble : déclaration d'intention d'aliéner et délai de deux mois de préemption, conditions suspensives, acte authentique. Pour le Private Equity : agrément du gérant, droits de préemption et documentation de cession.")
h3("Méthode paramétrique")
p("Pour un titre coté, le délai d'exécution d'un montant $Q$ sous une contrainte de participation maximale $\\rho$ au volume quotidien $V_d$ est $\\tau(Q) = Q/(\\rho\\,V_d)$. "
  "Au seuil $\\alpha$, on retient le volume quotidien de quantile $1-\\alpha$ (marché déprimé) : $\\tau_{\\alpha}(Q) = Q / (\\rho\\, V_d^{(1-\\alpha)})$, avec $\\rho = 25\\,\\%$ pour les ETF négociés sur carnet et $\\rho = 100\\,\\%$ pour les obligations négociées en bloc avec un intermédiaire. "
  "Pour un actif non coté, le délai jusqu'à la première offre suit, dans le modèle poissonnien, une loi exponentielle :")
eq(r"\mathbb{P}\left(\tau_1 > u\right) = e^{-\nu u} \quad\Longrightarrow\quad t_{\min,\alpha} = T_{\mathrm{leg}} + \frac{\ln\left(1/(1-\alpha)\right)}{\nu}.", "eq:expo")
p("L'intensité est estimée par maximum de vraisemblance, $\\hat{\\nu} = \\sum_i n_i / \\sum_i m_i$ (nombre total d'offres rapporté à la durée totale de commercialisation). "
  "On obtient @re_nu@ offre par mois pour les bureaux en régime normal (@re_nu_s@ en stress) et @pe_nu@ pour le Private Equity (@pe_nu_s@ en stress). "
  "Le délai minimal au seuil de 99,5 % atteint ainsi @re_tmin_n@ jours (@re_tmin_s@ en stress) pour l'immeuble et @pe_tmin_n@ jours (@pe_tmin_s@ en stress) pour le Private Equity : "
  "la garantie quasi certaine de trouver un acheteur exige plus d'un an et demi en marché stressé.")
h3("Méthode non paramétrique")
p("L'estimateur de Kaplan-Meier [Kaplan et Meier, 1958] du délai jusqu'à la première offre tient compte des ventes infructueuses (censure à droite) :")
eq(r"\hat{S}(u) = \prod_{u_j \le u}\left(1 - \frac{d_j}{n_j}\right),", "eq:km")
p("où $d_j$ est le nombre de premières offres reçues en $u_j$ et $n_j$ le nombre de mandats encore actifs. "
  "Le délai médian total est de @re_km@ jours pour l'immeuble et de @pe_km@ jours pour le Private Equity (quantiles à 90 % : @re_km90@ et @pe_km90@ jours), proches des médianes paramétriques (@re_tfirst@ et @pe_tfirst@ jours, figure 5). "
  "L'estimateur non paramétrique ne permet toutefois pas d'atteindre le quantile 99,5 % faute d'observations dans la queue : l'extrapolation paramétrique est ici indispensable.")
fig("f09_kaplan_meier", "Figure 5 – Probabilité de n'avoir reçu aucune offre en fonction du délai : estimateur de Kaplan-Meier et loi exponentielle ajustée.", 12.5)

h2("Liquidité financière des actifs cotés")
h3("Indicateurs non paramétriques")
p("Nous calculons les indicateurs classiques de microstructure : la fourchette relative $s_t = (P^{\\mathrm{ask}}_t - P^{\\mathrm{bid}}_t)/M_t$, l'estimateur de fourchette implicite de Roll [Roll, 1984] à partir des transactions obligataires, le ratio d'illiquidité d'Amihud [Amihud, 2002], le $\\lambda$ de Kyle [Kyle, 1985] estimé par régression des rendements sur le déséquilibre d'ordres, et le *Market Efficiency Coefficient* [Hasbrouck et Schwartz, 1988] :")
eq(r"\hat{s}_{\mathrm{Roll}} = 2\sqrt{-\operatorname{Cov}\left(\Delta p_{k},\Delta p_{k-1}\right)}, \qquad \mathrm{ILLIQ} = \frac{1}{T}\sum_{t=1}^{T}\frac{|r_t|}{\mathrm{DVol}_t},", "eq:roll")
eq(r"r_t = c + \lambda\,\mathrm{OI}_t + \varepsilon_t, \qquad \mathrm{MEC} = \frac{\operatorname{Var}\left(R^{(n)}\right)}{n\,\operatorname{Var}(r)}.", "eq:kyle")
p("Un MEC proche de 1 caractérise un marché efficient ; un MEC inférieur à 1 traduit un excès de volatilité de court terme (rebond sur la fourchette), un MEC supérieur à 1 une autocorrélation positive, typique des valorisations lissées.")
rows = []
for k in LISTED:
    o = L[k]
    rows.append([NAME[k], fr(o["spread_med_bp"], 1), (fr(o["roll_bp"], 1) if "roll_bp" in o else "–"),
                 fr(o["amihud_bp_per_Meur"], 3), fr(o["kyle_lambda_bp_per_Meur"], 3), fr(o["MEC"], 2)])
tab(["Actif", "Fourchette (pb)", "Roll (pb)", "Amihud (pb / M€)", "λ de Kyle (pb / M€)", "MEC (n = 20)"], rows,
    "Indicateurs non paramétriques de liquidité financière des actifs cotés.", [5.4, 2.2, 1.9, 2.4, 2.6, 2.0])
p("Les indicateurs sont cohérents entre eux : le Treasury et l'OAT dominent, les ETF suivent, les obligations d'entreprise ferment la marche avec un $\\lambda$ de Kyle et un ratio d'Amihud supérieurs de deux ordres de grandeur à ceux des souverains. "
  "L'estimateur de Roll (@tte_roll@ pb pour TotalEnergies, @lvmh_roll@ pb pour LVMH) est cohérent avec les fourchettes affichées médianes (@tte_sp@ et @lvmh_sp@ pb) : il les dépasse légèrement car les prix de transaction s'écartent aléatoirement des bornes de la fourchette. "
  "Aucun de ces indicateurs ne donne cependant le coût de cession d'un montant donné dans un délai donné.")
h3("Méthode paramétrique : loi d'impact en racine carrée")
p("La littérature empirique sur l'exécution des méta-ordres établit que l'impact croît comme la racine carrée de la taille rapportée au volume [Almgren et Chriss, 2001 ; Tóth et al., 2011 ; Bouchaud et al., 2018]. Nous retenons la spécification")
eq(r"\mathcal{I}(Q,t) = Y\,\sigma_d\left(\frac{Q}{V_d\,t}\right)^{\delta},", "eq:sqrt")
p("où $\\sigma_d$ est la volatilité quotidienne, $V_d$ le volume quotidien et $t$ la durée d'exécution en jours de bourse. Les paramètres $(Y,\\delta)$ sont estimés par moindres carrés ordinaires sur le journal des méta-ordres :")
eq(r"\ln\left(\frac{\Delta P_i - f - s_i/2}{\sigma_{d,i}}\right) = \ln Y + \delta\,\ln\left(\frac{Q_i}{V_{d,i}\,t_i}\right) + e_i.", "eq:ols")
rows = [[NAME[k], fr(L[k]["Y_hat"], 3), fr(L[k]["delta_hat"], 3), fr(L[k]["delta_se"], 3), fr(L[k]["r2"], 2), fr(L[k]["n_meta"], 0)] for k in LISTED]
tab(["Actif", "Ŷ", "δ̂", "écart-type de δ̂", "R²", "Méta-ordres"], rows,
    "Calibration de la loi d'impact (équation [[eq:sqrt]]) sur le journal d'exécutions.", [5.6, 2.0, 2.0, 2.6, 1.8, 2.3])
p("L'exposant estimé est compris entre @d_min@ et @d_max@, conforme à la valeur théorique $\\delta = 1/2$ (figure 6). "
  "La surface paramétrique est obtenue par simulation de Monte-Carlo : le triplet $(\\ln\\sigma_d, \\ln V_d, \\ln s)$ est tiré dans une loi normale multivariée ajustée sur l'historique, et le résidu $e$ dans une loi normale. "
  "La surface **non paramétrique** est obtenue par bootstrap historique : on tire conjointement des journées passées $(\\sigma_d, V_d, s)$ et des résidus empiriques, ce qui préserve les dépendances non linéaires et les queues épaisses observées en crise.")
fig("f05_calibration_impact", "Figure 6 – Calibration de la loi d'impact en racine carrée (échelle log-log) pour trois actifs représentatifs.")
fig("f06_cout_quantite", "Figure 7 – Coût de liquidité ΔP en fonction de la quantité vendue (bootstrap historique). Trait plein : médiane ; tirets : quantile 99,5 %.")
fig("f07_surface_dptv", "Figure 8 – Surfaces ΔPTV de l'ETF CAC 40 et de l'obligation TotalEnergies (échelles logarithmiques) : médiane (surface pleine) et quantile 99,5 % (grille).")
rows = []
for k in LISTED:
    o = L[k]
    rows.append([NAME[k], fr(o["dP_p_t1_q50_bp"], 1), fr(o["dP_np_t1_q50_bp"], 1), fr(o["dP_p_t1_q995_bp"], 1), fr(o["dP_np_t1_q995_bp"], 1),
                 fr(o["dP_p_t20_q995_bp"], 1), fr(o["dP_np_t20_q995_bp"], 1)])
tab(["Actif", "q50 % t=1 j (P)", "q50 % t=1 j (NP)", "q99,5 % t=1 j (P)", "q99,5 % t=1 j (NP)", "q99,5 % t=20 j (P)", "q99,5 % t=20 j (NP)"], rows,
    "ΔPTV des actifs cotés pour Q* = 10 M€ (en points de base) : méthode paramétrique (P) et non paramétrique (NP).", [4.6, 1.9, 1.9, 2.0, 2.0, 2.0, 2.0], font=8)
p("Les deux méthodes concordent sur la médiane (écarts inférieurs à 10 %) ; la méthode paramétrique produit des quantiles 99,5 % un peu plus élevés, l'hypothèse log-normale surpondérant les combinaisons extrêmes de volatilité forte et de volume faible. "
  "Pour 10 M€ vendus en une journée, le coût médian est de @ust_t1@ pb pour le Treasury, @oat_t1@ pb pour l'OAT, @cac_t1@ pb pour l'ETF CAC 40 et @tte_t1@ pb pour l'obligation TotalEnergies ; il est divisé par trois environ lorsque la vente est étalée sur vingt jours, conformément à la décroissance en $t^{-1/2}$ de l'équation [[eq:sqrt]].")

h2("Liquidité financière des actifs non cotés")
h3("Méthode paramétrique : modèle d'enchère poissonnien")
p("Pour l'immeuble et le Private Equity, la notion de quantité perd son sens (l'actif est cédé en bloc) et c'est le délai qui gouverne la décote. Avec $\\Lambda(t) = \\nu\\,(t - T_{\\mathrm{leg}})^{+}$ le nombre moyen d'offres reçues, la loi du rapport prix/valeur $M$ conditionnellement à la réalisation de la vente est")
eq(r"\mathbb{P}\left(M \le x \mid N\ge 1\right) = \frac{\exp\left(-\Lambda\left[1-\Phi\left(\frac{\ln x - \mu_b}{\sigma_b}\right)\right]\right) - e^{-\Lambda}}{1 - e^{-\Lambda}},", "eq:cdfM")
p("d'où le quantile explicite (démonstration en annexe B)")
eq(r"\Delta\mathrm{PTV}_{\alpha}(t) = 1 - \exp\left(\mu_b + \sigma_b\,\Phi^{-1}\left(1 + \frac{\ln\left(e^{-\Lambda} + (1-\alpha)(1-e^{-\Lambda})\right)}{\Lambda}\right)\right).", "eq:qM")
p("Les paramètres $(\\mu_b,\\sigma_b)$ sont estimés par maximum de vraisemblance à partir des rapports prix/valeur $m_i$ et des nombres d'offres $n_i$ des ventes réalisées, la densité du maximum de $n$ log-normales donnant la log-vraisemblance")
eq(r"\ell(\mu_b,\sigma_b) = \sum_{i}\left[\ln n_i + \ln\varphi(z_i) + (n_i-1)\ln\Phi(z_i) - \ln\sigma_b\right], \qquad z_i = \frac{\ln m_i - \mu_b}{\sigma_b}.", "eq:mle")
rows = []
for k in ("RE", "PE"):
    for lab, labfr in (("normal", "normal"), ("stress", "stressé")):
        f = U[k][lab]
        rows.append([NAME[k].split(" (")[0], labfr, f"{fr(f['nu'] * 30.4, 3)} ({fr(f['nu_se'] * 30.4, 3)})",
                     f"{fr(f['mu_b'], 3)} ({fr(f['mu_se'], 3)})", f"{fr(f['sig_b'], 3)} ({fr(f['sig_se'], 3)})", f"{f['n_sold']} / {f['n']}"])
tab(["Actif", "Régime", "ν̂ (offres / mois)", "μ̂_b", "σ̂_b", "Ventes / mandats"], rows,
    "Estimation par maximum de vraisemblance du modèle d'enchère (écarts-types asymptotiques entre parenthèses).", [3.6, 1.8, 3.0, 2.7, 2.7, 2.4])
h3("Méthode non paramétrique")
p("En parallèle, nous estimons les quantiles empiriques des décotes observées, ainsi qu'une médiane conditionnelle au délai par un estimateur à noyau gaussien sur $\\ln t$ [Nadaraya, 1964 ; Watson, 1964] :")
eq(r"\hat{q}_{p}(t) = \inf\left\{ y : \frac{\sum_i K_h(\ln t_i - \ln t)\,\mathbf{1}_{\{y_i\le y\}}}{\sum_i K_h(\ln t_i - \ln t)} \ge p \right\}.", "eq:kq")
p("La décote médiane empirique est de @re_np50@ pour les bureaux (@re_np50s@ en période de stress) et de @pe_np50@ pour le Private Equity (@pe_np50s@ en stress) ; le quantile empirique 99,5 % atteint @re_np995@ (intervalle bootstrap à 90 % : @re_ci@) et @pe_np995@ (@pe_ci@). "
  "Ces niveaux sont cohérents avec les ordres de grandeur de [Moreau, 2024] : jusqu'à 30 % pour l'immobilier en stress, de 15 % à 55 % pour le Private Equity.")
fig("f08_decote_delai", "Figure 9 – Décote en fonction du délai total de cession : transactions simulées, quantiles paramétriques (modèle d'enchère, régimes normal et stressé) et médiane à noyau.")
rows = []
for k in ("RE", "PE"):
    o = U[k]
    rows.append([NAME[k].split(" (")[0], pct(o["dP_normal_t180_q50"]), pct(o["dP_normal_t365_q50"]), pct(o["dP_stress_t180_q995"]), pct(o["dP_stress_t365_q995"]),
                 pct(o["dP_np_q50"]), pct(o["dP_np_q995"])])
tab(["Actif", "q50 % t=180 j (P)", "q50 % t=365 j (P)", "q99,5 % stress t=180 j (P)", "q99,5 % stress t=365 j (P)", "q50 % (NP)", "q99,5 % (NP)"], rows,
    "ΔPTV des actifs non cotés : modèle d'enchère (P) et quantiles empiriques toutes transactions confondues (NP).", [3.2, 2.2, 2.2, 2.6, 2.6, 1.8, 1.8], font=8)
h3("Combien d'acheteurs pour vendre au juste prix ?")
p("L'équation [[eq:Nstar]] appliquée aux paramètres estimés répond à la question posée en section 2.3. Pour obtenir avec 90 % de probabilité un prix au moins égal à 90 % de la valeur publiée, il faut $N^{*} = @re_N@$ acheteurs pour l'immeuble en régime normal ($F(0{,}9) = @re_F@$) et @re_Ns@ en stress ; "
  "il en faut @pe_N@ pour le Private Equity en régime normal et @pe_Ns@ en stress, ce qui revient, au rythme d'arrivée estimé, à des délais de commercialisation de plusieurs années (figure 10). "
  "Pour les actifs cotés, la dispersion des offres se réduit à la demi-fourchette et un seul intervenant suffit. "
  "Ce résultat éclaire la nature de l'illiquidité du Private Equity : ce n'est pas tant la rareté des acheteurs que la décote systématique qu'ils exigent ($\\hat{\\mu}_b$ très négatif) qui rend le juste prix presque inaccessible.")
fig("f10_nombre_acheteurs", "Figure 10 – Probabilité d'obtenir au moins 90 % de la valeur publiée en fonction du nombre d'acheteurs potentiels.", 12.5)
h3("Lissage des valorisations")
p("Le dé-lissage de Geltner, avec $\\hat{a} = 1 - \\hat{\\rho}_1$, porte la volatilité annuelle de @re_sobs@ à @re_sun@ pour l'immeuble ($\\hat{a} = @re_a@$) et de @pe_sobs@ à @pe_sun@ pour le Private Equity ($\\hat{a} = @pe_a@$). "
  "Les vraies valeurs ($0{,}45$ et $0{,}35$) ne sont qu'approximativement retrouvées sur 43 trimestres, ce qui illustre la fragilité de cette correction sur des historiques courts [Getmansky et al., 2004]. "
  "Le MEC trimestriel des séries publiées (@re_mec@ et @pe_mec@) est nettement supérieur à 1, signature du lissage.")

h2("Liquidité contre incertitude de valeur")
p("La figure 11 représente le rapport $\\rho(t)$ de l'équation [[eq:ratio]]. Pour les actifs cotés, le coût de liquidité devient rapidement négligeable devant l'incertitude de valeur : dès cinq jours, $\\rho < 0{,}5$ pour tous les titres et, à vingt jours, $\\rho = @ratio_cac20@$ pour l'ETF CAC 40. "
  "Seules les obligations d'entreprise présentent un rapport supérieur à 1 pour une vente en une journée ($\\rho = @ratio_tte1@$ pour TotalEnergies). "
  "Pour les actifs non cotés, en revanche, la décote de liquidité reste du même ordre que la variation de valeur, voire supérieure : $\\rho = @ratio_re180@$ à six mois pour l'immeuble et $\\rho = @ratio_pe180@$ pour le Private Equity, encore @ratio_pe365@ à un an. "
  "L'intuition selon laquelle la variation de prix liée à la liquidité est négligeable n'est donc valide que pour les actifs cotés et pour des horizons de quelques jours ; elle est fausse pour les actifs réels et non cotés, pour lesquels la liquidité doit être modélisée explicitement.")
fig("f11_liquidite_vs_valeur", "Figure 11 – Rapport entre le coût médian de liquidité et l'incertitude de valeur σ√t, pour Q* = 10 M€.", 12.5)

h2("Indicateur synthétique de liquidité")
h3("Normalisation des deux composantes")
p("Les deux mesures n'ont ni la même unité ni la même échelle. Nous les ramenons à des scores dans $[0,1]$ (1 = parfaitement liquide) par une transformation logarithmique, qui reflète le fait qu'un doublement du délai ou du coût a une signification comparable à tous les niveaux :")
eq(r"I_1 = 1 - \frac{\ln\left(1 + t_{\min,\alpha}\right)}{\ln\left(1 + T_{\max}\right)}, \qquad I_2 = 1 - \frac{\ln\left(1 + \Delta\mathrm{PTV}_{\alpha}(Q^{*},t_{\min,\alpha})/\epsilon\right)}{\ln\left(1 + 1/\epsilon\right)},", "eq:scores")
p("avec $t$ en jours, $T_{\\max} = 3$ ans, $\\epsilon = 1$ point de base, $\\alpha = 99{,}5\\,\\%$ et $Q^{*} = 10$ M€ (actifs non cotés : actif entier). "
  "$I_1$ mesure la liquidité juridique (délai minimal de cession au seuil $\\alpha$), $I_2$ la liquidité financière (décote au seuil $\\alpha$ pour une vente au plus tôt). L'indicateur synthétique est la combinaison convexe")
eq(r"L(x) = x\,I_1 + (1-x)\,I_2, \qquad x\in[0,1].", "eq:L")
h3("Calibration du poids x sur le coût actif-passif")
p("Plutôt que de fixer $x$ à dire d'expert, nous le calibrons sur le coût que supporterait l'assureur pour mobiliser $Q^{*}$ à un horizon de passif $H$. Si l'actif ne peut être cédé avant $H$, le besoin de trésorerie doit être financé en urgence au taux $r_e$ jusqu'à la cession, et l'impasse de trésorerie entraîne une pénalité $\\pi$ (coût réglementaire et de réputation) :")
eq(r"C^{\mathrm{ALM}} = \begin{cases} \Delta\mathrm{PTV}_{\alpha}(Q^{*},H) & \text{si } t_{\min,\alpha}\le H, \\ \Delta\mathrm{PTV}_{\alpha}(Q^{*},t_{\min,\alpha}) + r_e\,\frac{t_{\min,\alpha}-H}{365} + \pi & \text{sinon,} \end{cases}", "eq:calm")
p("avec $H = 30$ jours (délai usuel de règlement des prestations), $r_e = 8\\,\\%$ et $\\pi = 2\\,\\%$. Le score $S^{\\mathrm{ALM}}$ est obtenu par la même transformation que $I_2$. Le poids optimal minimise l'écart quadratique entre $L(x)$ et $S^{\\mathrm{ALM}}$ sur les huit actifs ; il admet une forme fermée (annexe B) :")
eq(r"x^{*} = \operatorname{argmin}_{x\in[0,1]} \sum_{i}\left(L_i(x) - S^{\mathrm{ALM}}_i\right)^2 = \min\left(1,\max\left(0,\frac{\langle S^{\mathrm{ALM}} - I_2,\; I_1 - I_2\rangle}{\lVert I_1 - I_2\rVert^{2}}\right)\right).", "eq:xstar")
p("On obtient $x^{*} = @xstar@$ : la liquidité juridique et la liquidité financière contribuent à parts presque égales au coût actif-passif, avec un léger avantage pour la première. "
  "La figure 13 montre que le classement des actifs est stable pour tout $x$ compris entre 0,2 et 0,8 : l'indicateur est robuste au choix de la pondération.")
fig("f12_carte_liquidite", "Figure 12 – Carte de liquidité : liquidité juridique I₁ en abscisse, liquidité financière I₂ en ordonnée, iso-lignes de l'indicateur synthétique L(x*).", 13.5)
fig("f13_sensibilite_x", "Figure 13 – a) Sensibilité de l'indicateur synthétique au poids x ; b) critère de calibration de x* sur le score actif-passif.")
h3("Notation lettrée")
p("Pour la communication, nous associons à chaque actif deux notations de A à F : une note de liquidité juridique fondée sur le délai légal (A : moins d'un jour ; B : moins de 3 jours ; C : moins d'une semaine ; D : moins d'un mois ; E : moins d'un an ; F : au-delà) "
  "et une note d'observabilité fondée sur le nombre de participants ou de transactions par jour (A : plus de 100 ; B : plus de 30 ; C : plus de 5 ; D : plus de 1 ; E : plus de 1 par semaine ; F : moins). La note finale retient la plus mauvaise des deux. "
  "Une note équivalente est déduite de $L(x^{*})$ par seuils (A ≥ 0,80 ; B ≥ 0,65 ; C ≥ 0,50 ; D ≥ 0,35 ; E ≥ 0,20 ; F < 0,20).")
h3("Résultats")
rows = [[NAME[k], f"L = {fr(S[k]['L'], 2)}   (note {S[k]['note_L']})"] for k in sorted(ALL, key=lambda k: -S[k]["L"])]
tab(["TYPE D'ACTIF", "INDICATEUR DE LIQUIDITÉ"], rows,
    "Indicateur synthétique de liquidité L = x*·I₁ + (1 − x*)·I₂ avec x* = @xstar@ (1 = parfaitement liquide).", [8.6, 7.4])
rows = []
for k in sorted(ALL, key=lambda k: -S[k]["L"]):
    s = S[k]
    dp = f"{fr(s['dP995'] * 1e4, 0)} pb" if s["dP995"] < 0.02 else pct(s["dP995"])
    rows.append([NAME[k], fr(s["t_min"], 1), fr(s["I1"], 2), dp, fr(s["I2"], 2), fr(s["L"], 2),
                 f"{s['note_phys']} / {s['note_eco']} → {s['note_finale']}"])
tab(["Actif", "t_min,99,5 % (j)", "I₁", "ΔPTV₉₉,₅ % au plus tôt", "I₂", "L(x*)", "Notes jur. / obs. → finale"], rows,
    "Détail des composantes de l'indicateur synthétique (Q* = 10 M€, α = 99,5 %).", [4.6, 2.0, 1.4, 2.6, 1.4, 1.5, 3.0], font=8)
p("Le Treasury (@L_ust@) et l'OAT (@L_oat@) sont les actifs les plus liquides ; viennent ensuite les ETF actions (@L_cac@ et @L_spx@), puis les obligations d'entreprise (@L_tte@ et @L_lvmh@), pénalisées par un volume quotidien faible qui allonge le délai de cession d'un bloc de 10 M€ en marché déprimé. "
  "L'immeuble (@L_re@) et le Private Equity (@L_pe@) sont très loin derrière, et ce sur les deux dimensions. "
  "La notation lettrée est cohérente avec l'indicateur continu, mais elle est plus grossière : elle ne distingue pas l'OAT des ETF (note juridique B dans les deux cas), alors que $L$ les sépare nettement.")

# =============================================================================
h1("Application à la gestion actif-passif d'un assureur prévoyance")
h2("Spécificités du passif prévoyance")
p("Un assureur prévoyance couvre les risques de décès, d'incapacité de travail (indemnités journalières), d'invalidité (rentes jusqu'à la retraite) et, le cas échéant, de dépendance et de rentes d'éducation ou de conjoint. "
  "À la différence de l'épargne, le passif ne comporte pas d'option de rachat massif : le risque de liquidité provient d'une **hausse brutale des prestations** (pandémie, crise économique augmentant les arrêts de travail), d'une **baisse des cotisations** (résiliation d'un contrat collectif, reports de cotisations des entreprises) "
  "et, plus rarement, d'une **sortie exceptionnelle** (transfert d'engagements à un autre assureur lors d'un changement d'organisme). En prévoyance collective, la loi Évin impose de maintenir les prestations en cours à la date de résiliation (loi n° 89-1009, art. 7), si bien que la perte d'un grand compte réduit les cotisations sans réduire immédiatement les prestations.")
rows = [["Trésorerie", fr(A["A0"]["CASH"], 1)], ["OAT 10 ans", fr(A["A0"]["OATFR"], 1)], ["Treasury 10 ans (couvert en change)", fr(A["A0"]["UST"], 1)],
        ["Obligation TotalEnergies", fr(A["A0"]["TTE"], 1)], ["Obligation LVMH", fr(A["A0"]["LVMH"], 1)], ["ETF CAC 40", fr(A["A0"]["CAC"], 1)],
        ["ETF S&P 500", fr(A["A0"]["SPX"], 1)], ["Immeuble de bureaux", fr(A["A0"]["RE"], 1)], ["Private Equity small caps", fr(A["A0"]["PE"], 1)],
        ["**Total actif**", "**" + fr(A["A_TOT"], 1) + "**"]]
rows2 = [[k, fr(v, 1)] for k, v in A["LIAB"].items()] + [["Fonds propres", fr(A["FP"], 1)], ["**Total passif**", "**" + fr(A["A_TOT"], 1) + "**"]]
n = max(len(rows), len(rows2))
rows = [(rows[i] if i < len(rows) else ["", ""]) + (rows2[i] if i < len(rows2) else ["", ""]) for i in range(n)]
tab(["Actif", "M€", "Passif", "M€"], rows, "Bilan économique simplifié de l'assureur prévoyance fictif au 31/12/2025.", [5.0, 1.8, 7.0, 1.8])
h2("Flux de passif en scénario central et en stress")
p("Les flux mensuels sont simulés sur douze mois (10 000 trajectoires). Les décès suivent une loi de Poisson composée (25 sinistres par mois en moyenne, capitaux log-normaux de moyenne 110 k€ et de coefficient de variation 0,8) ; "
  "les indemnités journalières (4,5 M€ par mois), les rentes d'invalidité (3,0 M€), les rentes d'éducation et de conjoint (0,8 M€) et les frais (1,6 M€) sont affectés de bruits log-normaux ; les cotisations s'élèvent à 14 M€ par mois. "
  "Le **scénario de stress** combine une pandémie (mortalité × 1,5 pendant six mois, indemnités journalières × 2 pendant trois mois puis × 1,4, bascule progressive vers l'invalidité), une chute des cotisations (−45 % le premier mois, −20 % ensuite) et une sortie exceptionnelle de 25 M€ le premier mois. "
  "Les actifs subissent simultanément les chocs de la formule standard (actions −39 %, Private Equity −49 %, immobilier −25 %, chocs de taux et de spread).")
fig("f14_flux_passif", "Figure 14 – Besoin de trésorerie cumulé (sorties nettes) : scénario central et scénario de stress prévoyance.")
p("En scénario central, l'assureur est structurellement prêteur de trésorerie : les cotisations excèdent les prestations et le besoin cumulé médian à un an est négatif (@need365b@ M€). "
  "En stress, le besoin cumulé au quantile 99,5 % atteint @need30@ M€ à un mois et @need365@ M€ à un an, soit environ 15 % de l'actif.")
h2("Échelle de liquidité")
p("Pour chaque horizon $h$, la liquidité nette mobilisable est la somme, sur les actifs, des montants cessibles avant $h$ (compte tenu du délai juridique et du volume de marché déprimé), valorisés après choc et nets du coût $\\Delta\\mathrm{PTV}_{99{,}5\\,\\%}$ :")
eq(r"\mathrm{RL}(h) = \frac{\sum_{i} \min\left(A_i^{s},\; \rho_i V_{d,i}^{(1-\alpha)}\,(h - T_{\mathrm{leg},i})^{+}\right)\left(1-\Delta\mathrm{PTV}_{\alpha,i}\right)}{B_{\alpha}(h)},", "eq:RL")
p("où $A_i^{s}$ est la valeur choquée de l'actif $i$ et $B_{\\alpha}(h)$ le besoin cumulé au quantile $\\alpha$ ; ce ratio transpose à l'assurance la logique du LCR bâlois [Comité de Bâle, 2013]. Les actifs non cotés ne contribuent qu'au-delà de leur délai minimal de cession $t_{\\min,99{,}5\\,\\%}$.")
fig("f15_echelle_liquidite", "Figure 15 – Échelle de liquidité en stress : liquidité nette mobilisable par horizon et besoin stressé au quantile 99,5 %.", 15.0)
rows = [[f"{h} jours", fr(A["need"][str(h)]["str_q50"], 1), fr(A["need"][str(h)]["str_q995"], 1),
         fr(sum(v[0] for v in A["ladder"][str(h)].values()), 1), fr(A["LR"][str(h)], 1)] for h in (7, 30, 90, 180, 365)]
tab(["Horizon", "Besoin médian (M€)", "Besoin q99,5 % (M€)", "Liquidité mobilisable (M€)", "RL(h)"], rows,
    "Ratio de liquidité par horizon en scénario de stress.", [2.6, 3.0, 3.0, 3.6, 2.0])
p("Le ratio de liquidité reste très supérieur à 1 à tous les horizons (@LR30@ à un mois, @LR365@ à un an) : le portefeuille obligataire souverain suffit à couvrir le stress. "
  "Un **test de résistance inversé** montre qu'il faudrait une sortie exceptionnelle de l'ordre de @Xstar@ M€ (@Xstar_pct@ de l'actif) pour ramener le ratio à 1 à un mois. "
  "L'immeuble et le Private Equity ne contribuent à aucun horizon inférieur à un an : leur illiquidité ne menace pas la solvabilité de trésorerie de cet assureur, mais elle rend ces actifs inutilisables comme réserve de liquidité, ce que les indicateurs usuels de valeur ne révèlent pas.")
h2("Stratégie de liquidation optimale")
p("Soit $x_{i,m}$ le montant de l'actif coté $i$ vendu au cours du mois $m$ et $B_m$ le besoin cumulé stressé au quantile 99,5 %. La stratégie de liquidation minimise la somme du coût de liquidité et du rendement abandonné (portage), sous contrainte d'absence d'impasse de trésorerie :")
eq(r"\min_{x\ge 0}\; \sum_{i}\sum_{m=1}^{12}\left[c_i(x_{i,m})\,x_{i,m} + \mu_i\,\frac{12-m+1}{12}\,x_{i,m}\right]", "eq:liqobj")
eq(r"\text{s.c.}\quad C_0 + \sum_{m'\le m}\sum_{i} x_{i,m'}\left(1 - c_i(x_{i,m'})\right) \ge B_m\;\;\forall m, \qquad \sum_{m} x_{i,m} \le A^{s}_i\;\;\forall i,", "eq:liqcon")
p("où $c_i(x) = f_i + s_i/2 + Y_i\\,\\sigma_{d,i}\\,(x/(21\\,V_{d,i}))^{\\delta_i}$ est le coût unitaire d'une vente étalée sur un mois en conditions de marché dégradées et $\\mu_i$ le rendement espéré. Le problème, convexe, est résolu par programmation quadratique séquentielle (SLSQP).")
fig("f16_liquidation_optimale", "Figure 16 – Ventes mensuelles : stratégie optimale et vente au prorata des encours cotés.")
lq = A["liquidation"]
rows = [["Stratégie optimale", fr(lq["opt_sold"], 1), fr(lq["opt_liq"] * 1000, 0), fr(lq["opt_carry"] * 1000, 0), fr((lq["opt_liq"] + lq["opt_carry"]) * 1000, 0)],
        ["Vente au prorata", fr(lq["pr_sold"], 1), fr(lq["pr_liq"] * 1000, 0), fr(lq["pr_carry"] * 1000, 0), fr((lq["pr_liq"] + lq["pr_carry"]) * 1000, 0)]]
tab(["Stratégie", "Ventes brutes (M€)", "Coût de liquidité (k€)", "Portage abandonné (k€)", "Coût total (k€)"], rows,
    "Coût d'une crise de trésorerie de douze mois selon la stratégie de liquidation.", [3.6, 2.8, 3.0, 3.2, 2.6])
p("La stratégie optimale concentre les ventes sur l'OAT et le Treasury, dont le coût de liquidité et le rendement espéré sont les plus faibles, et réduit le coût total de @liq_gain@ par rapport à une vente au prorata. "
  "Le coût de liquidité proprement dit reste faible (@liq_opt_l@ k€ contre @liq_pr_l@ k€) : pour un assureur prévoyance, l'enjeu principal d'une crise de trésorerie n'est pas la décote de marché mais le choix des actifs à céder et le rendement abandonné.")
h2("Allocation stratégique sous contrainte de liquidité")
p("Enfin, dans l'esprit de [Markowitz, 1952], nous déterminons l'allocation qui maximise le rendement espéré net du coût de liquidité attendu, sous une contrainte de volatilité et deux contraintes de liquidité : le ratio de liquidité à un mois et le score de liquidité du portefeuille $L_p = \\sum_i w_i L_i$, que nous imposons au moins égal à son niveau actuel (0,60) :")
eq(r"\max_{w}\; w^{\top}\mu - \pi_f\, w^{\top}\Delta\mathrm{PTV}_{99{,}5\%} \quad \text{s.c.}\quad w^{\top}\Sigma w \le \sigma_{\max}^{2},\;\; \mathrm{RL}_w(30) \ge 1{,}2,\;\; \sum_i w_i L_i \ge 0{,}60,\;\; \mathbf{1}^{\top}w = 1,\;\; 0\le w_i\le \bar{w}_i,", "eq:alloc")
p("où $\\pi_f = 5\\,\\%$ est la probabilité annuelle d'une vente forcée et $\\Sigma$ la matrice de covariance estimée sur les rendements trimestriels (dé-lissés pour l'immobilier et le Private Equity). Les rendements espérés sont des hypothèses prospectives (annexe C).")
fig("f17_allocation", "Figure 17 – a) Frontières efficientes avec et sans contraintes de liquidité ; b) allocations actuelle et optimales pour σ ≤ 8 %.")
p("L'allocation actuelle (rendement net @cur_net@ pour une volatilité de @cur_vol@, $L_p = @cur_Lp@$) est sous-optimale : à volatilité égale, la frontière offre environ @eff_gain@ points de base de plus. "
  "La contrainte de liquidité n'est active qu'au-delà de 6,5 % de volatilité ; à 8 %, elle conduit à remplacer l'essentiel de l'immobilier (@nc8_re@ → @c8_re@) par de l'OAT et coûte @cost_con@ points de base de rendement net ($L_p$ passant de @nc8_Lp@ à @c8_Lp@). "
  "Le ratio de liquidité à un mois, en revanche, n'est jamais contraignant : pour un assureur prévoyance, la contrainte pertinente porte sur la qualité de liquidité globale du portefeuille plutôt que sur la couverture des besoins de court terme.")

# =============================================================================
h1("Conclusion")
p("Nous avons proposé un cadre de mesure de la liquidité qui distingue la liquidité juridique, imposée par le droit et l'organisation des marchés, de la liquidité financière, décrite par la surface probabiliste $\\Delta\\mathrm{PTV}_{\\alpha}(Q,t)$. "
  "Chaque dimension a été estimée par des méthodes paramétriques et non paramétriques qui convergent sur les ordres de grandeur : les secondes sont préférables là où les données abondent (actifs cotés, cœur de distribution), les premières sont indispensables pour extrapoler les quantiles extrêmes, en particulier pour les actifs non cotés où les observations sont rares et censurées.")
p("Trois enseignements se dégagent. "
  "Premièrement, pour les actifs cotés, le coût de liquidité est faible et devient rapidement négligeable devant l'incertitude de valeur ; il est en revanche du même ordre, voire supérieur, pour l'immobilier et le Private Equity. "
  "Deuxièmement, l'illiquidité des actifs non cotés est d'abord une illiquidité de délai : même en marché normal, garantir à 99,5 % l'obtention d'une offre demande plus de dix mois. "
  "Troisièmement, l'indicateur synthétique $L = x\\,I_1 + (1-x)\\,I_2$, dont le poids $x^{*} = @xstar@$ est calibré sur le coût actif-passif, classe les actifs de façon robuste et s'intègre directement dans l'optimisation de l'allocation sous la forme d'une contrainte linéaire.")
p("Plusieurs limites appellent des travaux complémentaires : la calibration sur données réelles de transaction (TRACE, MiFID II, bases notariales, rapports du marché secondaire), l'introduction d'une dynamique de la liquidité (quatrième dimension temporelle évoquée dans [Moreau, 2024]), la modélisation de la dépendance entre chocs de passif et chocs de liquidité, et l'extension à d'autres classes d'actifs (dette privée, infrastructures, fonds ouverts soumis à des mécanismes de plafonnement des rachats). "
  "Enfin, le cadre ouvre la voie à une exigence de capital explicite pour le risque de liquidité, absente de la formule standard de Solvabilité II, qui pourrait s'appuyer sur la surface $\\Delta\\mathrm{PTV}_{99{,}5\\,\\%}$ et sur le coût actif-passif de l'équation [[eq:calm]].")

# =============================================================================
h1("Synthèse")
p("Le tableau ci-dessous résume, pour un décideur, les principaux résultats de l'étude.")
bl("**Deux liquidités.** La liquidité juridique (délai incompressible : de 1 jour pour le Treasury à 4 mois pour le Private Equity) et la liquidité financière (décote $\\Delta\\mathrm{PTV}$ fonction de $Q$ et $t$) se mesurent séparément puis s'agrègent.",
   "**Mesures.** Actifs cotés : loi d'impact en racine carrée ($\\hat{\\delta} \\approx 0{,}5$) et bootstrap historique. Actifs non cotés : modèle d'enchère poissonnien estimé par maximum de vraisemblance, Kaplan-Meier et quantiles à noyau.",
   "**Ordres de grandeur (10 M€, 99,5 %).** Quelques points de base pour les souverains, quelques dizaines pour les ETF et les obligations d'entreprise ; @re_np995@ pour l'immeuble et @pe_np995@ pour le Private Equity.",
   "**Indicateur synthétique.** $L = @xstar@\\,I_1 + @one_m_xstar@\\,I_2$ : Treasury @L_ust@, OAT @L_oat@, ETF CAC 40 @L_cac@, ETF S&P 500 @L_spx@, TotalEnergies @L_tte@, LVMH @L_lvmh@, bureaux @L_re@, Private Equity @L_pe@.",
   "**Combien d'acheteurs ?** Pour obtenir avec 90 % de chances au moins 90 % de la valeur : 1 intervenant pour un titre coté, @re_N@ pour l'immeuble, @pe_N@ pour le Private Equity (marché normal).",
   "**ALM prévoyance.** Besoin stressé à un an : @need365@ M€ ; ratio de liquidité à un mois : @LR30@ ; la liquidation optimale réduit de @liq_gain@ le coût d'une crise ; la contrainte de liquidité coûte @cost_con@ pb de rendement à 8 % de volatilité.",
   "**Recommandations.** Piloter la liquidité par horizon (échelle de liquidité), ne pas compter les actifs non cotés dans la réserve de liquidité à moins d'un an, intégrer le score $L_p$ dans les contraintes d'allocation stratégique et définir à l'avance l'ordre de cession des actifs.")
rows = [[CLASS[k], NAME[k], fr(S[k]["L"], 2), S[k]["note_L"]] for k in sorted(ALL, key=lambda k: -S[k]["L"])]
tab(["Classe", "Type d'actif", "Indicateur L", "Note"], rows, "Synthèse : indicateur de liquidité par type d'actif.", [3.8, 7.6, 2.4, 1.6])

# =============================================================================
REFS = [
    "Almgren R., Chriss N. [2001] « Optimal execution of portfolio transactions », Journal of Risk, vol. 3, n° 2, p. 5-39.",
    "Amihud Y. [2002] « Illiquidity and stock returns: cross-section and time-series effects », Journal of Financial Markets, vol. 5, n° 1, p. 31-56.",
    "Amihud Y., Mendelson H. [1986] « Asset pricing and the bid-ask spread », Journal of Financial Economics, vol. 17, n° 2, p. 223-249.",
    "Bangia A., Diebold F.X., Schuermann T., Stroughair J.D. [1998] « Modeling liquidity risk, with implications for traditional market risk measurement and management », Working Paper, Wharton Financial Institutions Center.",
    "Comité de Bâle sur le contrôle bancaire [2013] Bâle III : ratio de liquidité à court terme et outils de suivi du risque de liquidité, Banque des règlements internationaux.",
    "Black F. [1971] « Toward a fully automated stock exchange, part I », Financial Analysts Journal, vol. 27, n° 4, p. 28-35.",
    "Bollerslev T. [1986] « Generalized autoregressive conditional heteroskedasticity », Journal of Econometrics, vol. 31, n° 3, p. 307-327.",
    "Bouchaud J.-P., Bonart J., Donier J., Gould M. [2018] Trades, Quotes and Prices: Financial Markets Under the Microscope, Cambridge University Press.",
    "Cox J.C., Ingersoll J.E., Ross S.A. [1985] « A theory of the term structure of interest rates », Econometrica, vol. 53, n° 2, p. 385-407.",
    "Demsetz H. [1968] « The cost of transacting », Quarterly Journal of Economics, vol. 82, n° 1, p. 33-53.",
    "Directive 2009/138/CE du Parlement européen et du Conseil du 25 novembre 2009 sur l'accès aux activités de l'assurance et de la réassurance et leur exercice (Solvabilité II).",
    "Directive (UE) 2025/2 du Parlement européen et du Conseil du 27 novembre 2024 modifiant la directive 2009/138/CE.",
    "EIOPA [2020] Opinion on the 2020 review of Solvency II, EIOPA-BoS-20/749.",
    "ESMA [2024] Final report: Assessment of the shortening of the settlement cycle in the European Union, ESMA74-2119945925-2059.",
    "Geltner D. [1991] « Smoothing in appraisal-based returns », Journal of Real Estate Finance and Economics, vol. 4, n° 3, p. 327-345.",
    "Getmansky M., Lo A.W., Makarov I. [2004] « An econometric model of serial correlation and illiquidity in hedge fund returns », Journal of Financial Economics, vol. 74, n° 3, p. 529-609.",
    "Glosten L.R., Jagannathan R., Runkle D.E. [1993] « On the relation between the expected value and the volatility of the nominal excess return on stocks », Journal of Finance, vol. 48, n° 5, p. 1779-1801.",
    "Gresse C. [1997] La fragmentation des marchés financiers. Réflexions théoriques et preuves empiriques sur les actions françaises, thèse de doctorat, Université Paris IX-Dauphine.",
    "Hasbrouck J., Schwartz R.A. [1988] « Liquidity and execution costs in equity markets », Journal of Portfolio Management, vol. 14, n° 3, p. 10-16.",
    "Kaplan E.L., Meier P. [1958] « Nonparametric estimation from incomplete observations », Journal of the American Statistical Association, vol. 53, n° 282, p. 457-481.",
    "Kyle A.S. [1985] « Continuous auctions and insider trading », Econometrica, vol. 53, n° 6, p. 1315-1335.",
    "Le Saout E. [1999] « Un indice de liquidité multidimensionnel », Banque & Marchés, n° 41.",
    "Le Saout E. [2000] De la microstructure à la gestion du risque de liquidité, thèse de doctorat, Université de Rennes I.",
    "Le Saout E. [2002] « Intégration du risque de liquidité dans les modèles de valeur en risque », Banque & Marchés, n° 61.",
    "Lin Z., Vandell K.D. [2007] « Illiquidity and pricing biases in the real estate market », Real Estate Economics, vol. 35, n° 3, p. 291-330.",
    "Loi n° 89-1009 du 31 décembre 1989 renforçant les garanties offertes aux personnes assurées contre certains risques (loi Évin).",
    "Loi n° 2023-973 du 23 octobre 2023 relative à l'industrie verte.",
    "Longstaff F.A., Mithal S., Neis E. [2005] « Corporate yield spreads: default risk or liquidity? New evidence from the credit default swap market », Journal of Finance, vol. 60, n° 5, p. 2213-2253.",
    "Markowitz H. [1952] « Portfolio selection », Journal of Finance, vol. 7, n° 1, p. 77-91.",
    "Mende J., Marks J., Perembetov K. [2016] Introductory guide to investing in private equity secondaries, Schroder Adveq.",
    "Moreau M. [2024] Revue générale du risque de liquidité et calibration d'une pénalité de rachat pour les contrats UC comportant du Private Equity, mémoire d'actuariat, EURIA / Institut des Actuaires.",
    "Moreau M., Planchet F. [2025] « Un nouvel indicateur de liquidité tridimensionnel », document de travail, version 0.1.",
    "Nadaraya E.A. [1964] « On estimating regression », Theory of Probability and its Applications, vol. 9, n° 1, p. 141-142.",
    "Règlement (UE) n° 909/2014 du Parlement européen et du Conseil du 23 juillet 2014 concernant l'amélioration du règlement de titres dans l'Union européenne et les dépositaires centraux de titres (CSDR).",
    "Roll R. [1984] « A simple implicit measure of the effective bid-ask spread in an efficient market », Journal of Finance, vol. 39, n° 4, p. 1127-1139.",
    "Tóth B., Lempérière Y., Deremble C., de Lataillade J., Kockelkoren J., Bouchaud J.-P. [2011] « Anomalous price impact and the critical nature of liquidity in financial markets », Physical Review X, vol. 1, 021006.",
    "Vasicek O. [1977] « An equilibrium characterization of the term structure », Journal of Financial Economics, vol. 5, n° 2, p. 177-188.",
    "Watson G.S. [1964] « Smooth regression analysis », Sankhyā, Series A, vol. 26, n° 4, p. 359-372.",
]

# =============================================================================
APP = []
def ah1(t): APP.append(("h1", t))
def ah2(t): APP.append(("h2", t))
def ap(t): APP.append(("p", sub(t)))
def aeq(t, lab=None): APP.append(("eq", t, lab))
def atab(head, rows, cap, widths=None, note=None, font=None): APP.append(("table", head, rows, sub(cap), widths, note and sub(note), font))
def abl(*items): APP.append(("bullets", [sub(i) for i in items]))

ah1("Annexe A – Sources des historiques et méthode de calibration")
ah2("A.1 Sources ayant servi à la calibration")
ap("Les données de l'article sont fictives. Leurs paramètres ont été fixés de façon à reproduire les ordres de grandeur publiés par les sources ci-dessous (niveaux, volatilités, fourchettes, volumes, décotes, délais). Les séries réelles peuvent être téléchargées auprès de ces sources pour appliquer la méthode à des données observées.")
rows = [
    ["ETF CAC 40", "Euronext (cours de clôture, statistiques mensuelles de négociation des ETF) ; niveaux de clôture annuels de l'indice CAC 40 ; émetteurs d'ETF (fourchettes indicatives)"],
    ["ETF S&P 500", "S&P Dow Jones Indices (niveaux annuels du S&P 500) ; BCE (taux de change de référence EUR/USD) ; Euronext (volumes ETF)"],
    ["OAT 10 ans", "Banque de France, Webstat : taux de l'échéance constante 10 ans (TEC 10) ; Agence France Trésor (bulletins mensuels, encours et volumes) ; MTS (fourchettes)"],
    ["Treasury 10 ans", "Board of Governors of the Federal Reserve System, série DGS10 (FRED) ; SIFMA (volumes quotidiens) ; FINRA TRACE Treasury aggregates"],
    ["TotalEnergies 10 ans", "Prospectus d'émission (taille de souche) ; indices ICE BofA Euro Corporate (spreads OAS par notation) ; MarketAxess / Trax (fourchettes et volumes de gré à gré)"],
    ["LVMH 10 ans", "Mêmes sources que TotalEnergies ; notation AA−/Aa3 (spreads plus serrés)"],
    ["Immeuble de bureaux", "MSCI Real Estate (indices de valeurs en capital, bureaux Île-de-France) ; Immostat et courtiers (volumes d'investissement) ; Notaires de France ; code de l'urbanisme, art. L213-2"],
    ["Private Equity", "France Invest / EY (performance du non coté français) ; Jefferies, Global Secondary Market Review (prix du secondaire en % de la NAV) ; Mende et al. [2016]"],
    ["Passif prévoyance", "Hypothèses illustratives cohérentes avec les rapports annuels d'organismes de prévoyance et les statistiques de la DREES et de l'ACPR"],
]
atab(["Actif", "Sources"], rows, "Sources des ordres de grandeur utilisés pour la calibration.", [3.4, 12.6], font=8)
ah2("A.2 Actions : GJR-GARCH(1,1)-t avec pont annuel")
ap("Le rendement logarithmique quotidien est $r_t = (1 + k_t)\\,\\varepsilon_t + d_t$, où $k_t \\ge 0$ est l'amplification exogène de stress, $d_t$ une dérive de crise et $\\varepsilon_t = \\sqrt{h_t}\\,z_t$ un choc GJR-GARCH à innovations de Student standardisées ($\\nu = 6$) :")
aeq(r"h_t = \omega + \left(a + \gamma\,\mathbf{1}_{\{\varepsilon_{t-1}<0\}}\right)\varepsilon_{t-1}^{2} + b\,h_{t-1}, \qquad \omega = \bar{\sigma}^{2}\Delta t\,(1 - a - b - \gamma/2),", "eq:garch")
ap("avec $a = 0{,}06$, $b = 0{,}90$, $\\gamma = 0{,}05$ et $\\bar{\\sigma} = 15\\,\\%$ (CAC 40) ou $14\\,\\%$ (S&P 500). Les innovations des deux ETF sont corrélées à un facteur commun ($\\rho = 0{,}92$ et $0{,}70$). "
   "Pour chaque année civile $y$, une correction de dérive constante est ajoutée afin que $\\sum_{t\\in y} r_t = \\ln(I_y / I_{y-1})$, où $I_y$ est le niveau de clôture de référence (pont de dérive) : les trajectoires conservent la dynamique GARCH intra-annuelle tout en respectant les niveaux annuels.")
ah2("A.3 Taux souverains, spreads de crédit et obligations à maturité constante")
ap("Le taux 10 ans est $y_t = \\bar{y}(t) + x_t$, où $\\bar{y}$ interpole linéairement les moyennes annuelles (centrées au 1er juillet) et $x_t$ suit un processus d'Ornstein-Uhlenbeck [Vasicek, 1977] discrétisé, ramené à zéro aux deux extrémités (pont) :")
aeq(r"x_{t+\Delta t} = x_t - \kappa\,x_t\,\Delta t + \sigma_y\left(1 + 0{,}6\,k_t\right)\sqrt{\Delta t}\,\xi_t, \qquad \kappa = 4,\;\; \sigma_y = 0{,}75\,\%\;(\text{OAT}),\; 0{,}90\,\%\;(\text{UST}).", "eq:ou")
ap("Le spread de crédit suit un processus CIR [Cox et al., 1985] dont la moyenne de long terme augmente avec le stress :")
aeq(r"s_{t+\Delta t} = \left| s_t + \kappa_s\left(\theta(1 + j\,k_t) - s_t\right)\Delta t + \sigma_s\sqrt{s_t\,\Delta t}\;\xi'_t \right|,", "eq:cir")
ap("avec $\\theta = 50$ pb (TotalEnergies) et $32$ pb (LVMH), $\\kappa_s = 6$, $\\sigma_s = 0{,}035$ et $0{,}028$. Le rendement quotidien d'une obligation à maturité constante de 10 ans, de coupon égal au taux, est approché au second ordre :")
aeq(r"r_t \approx y_{t-1}\,\Delta t - D^{\mathrm{mod}}_{t}\,\Delta y_t + \tfrac{1}{2}\,C_t\,(\Delta y_t)^{2}, \qquad D^{\mathrm{mod}} = \frac{1}{c}\left(1 - (1+c)^{-10}\right).", "eq:bond")
ah2("A.4 Microstructure : volumes, fourchettes et flux d'ordres")
ap("Pour chaque actif coté, le logarithme du volume suit un AR(1) lié à la volatilité, la fourchette une loi de puissance de la volatilité et le déséquilibre d'ordres signé une loi normale proportionnelle au volume ; une composante informationnelle de type Kyle est ajoutée aux rendements :")
aeq(r"\ln\frac{V_t}{\bar{V}} = \phi\ln\frac{V_{t-1}}{\bar{V}} + g\ln\frac{\sigma_t}{\bar{\sigma}} + u_t,\qquad s_t = \bar{s}\left(\frac{\sigma_t}{\bar{\sigma}}\right)^{\kappa} e^{v_t},\qquad r_t \leftarrow r_t + \lambda\,\mathrm{OI}_t,", "eq:micro")
ap("avec $\\phi = 0{,}6$, $g = 1{,}2$, $\\kappa = 0{,}8$ (ETF) ou $1$ (obligations), $\\mathrm{OI}_t \\sim \\mathcal{N}(0, (0{,}15\\,V_t)^{2})$. Les fourchettes de référence $\\bar{s}$ sont de 4 et 6 pb (ETF), 3 et 1,6 pb (souverains), 25 et 20 pb (TotalEnergies, LVMH) ; "
   "les volumes de référence de 150 et 110 M€ (ETF, carnet et RFQ), 1,5 Md€ (OAT 10 ans), 60 Md$ (Treasury 10 ans), 7 et 6 M€ (obligations d'entreprise). "
   "Les transactions obligataires de gré à gré arrivent selon un processus de Poisson (6 et 5 par jour en moyenne), avec des tickets log-normaux et un signe aléatoire. "
   "Le journal des 9 000 méta-ordres tire $Q$ log-uniformément entre 0,5 % et 500 % du volume quotidien et $t$ entre une heure et vingt jours, le coût réalisé suivant l'équation [[eq:sqrt]] avec $Y \\in [0{,}55 ; 0{,}90]$, $\\delta = 1/2$ et un bruit multiplicatif log-normal d'écart-type 0,35.")
ah2("A.5 Actifs non cotés : valeur latente, lissage et enchères")
ap("La valeur latente trimestrielle interpole des niveaux annuels de référence (bureaux : 100 en 2015, 131 en 2019, 105 en 2025 ; Private Equity : 100 en 2015, 222 en 2025), auxquels s'ajoutent un bruit gaussien intégré ramené à zéro aux extrémités (écart-type trimestriel 4,5 % et 7,5 %) et des chocs de crise transitoires (bureaux : −4 % au 2e trimestre 2020, −3 % aux 2e et 3e trimestres 2023 ; Private Equity : −14 % au 1er trimestre 2020, −6 % et −5 % aux 2e et 3e trimestres 2022). "
   "La valeur publiée suit l'équation [[eq:geltner]]. Pour chaque mandat de vente, la durée de commercialisation $m$ est uniforme sur [5 ; 45] jours (25 % de vendeurs pressés) ou log-normale de médiane 150 jours (bureaux) et 170 jours (Private Equity) ; "
   "le nombre d'offres suit $\\mathcal{P}(\\nu m)$, les offres sont log-normales autour de la valeur latente et le prix est rapporté à la valeur publiée. Les paramètres générateurs sont résumés dans le tableau suivant.")
dp = P["deals"]
rows = [["Bureaux", fr(dp["RE"]["T_leg"], 0), "0,75 / 0,28", fr(dp["RE"]["mu_b"], 2) + " / −0,17", fr(dp["RE"]["sig_b"], 2), "0,45", str(dp["RE"]["n"])],
        ["Private Equity", fr(dp["PE"]["T_leg"], 0), "0,60 / 0,25 à 0,35", fr(dp["PE"]["mu_b"], 2) + " / −0,39 à −0,33", fr(dp["PE"]["sig_b"], 2), "0,35", str(dp["PE"]["n"])]]
atab(["Actif", "T_leg (j)", "ν (offres / mois) normal / stress", "μ_b normal / stress", "σ_b", "a (Geltner)", "Mandats"], rows,
     "Paramètres générateurs des actifs non cotés.", [2.8, 1.6, 3.4, 3.4, 1.4, 1.8, 1.6], font=8)
ah2("A.6 Méthodes d'estimation")
abl("**Moindres carrés ordinaires** pour la loi d'impact (équation [[eq:ols]]) et le λ de Kyle ; erreurs-types classiques.",
    "**Maximum de vraisemblance** pour le modèle d'enchère (équation [[eq:mle]]) : optimisation de Nelder-Mead, matrice d'information par différences finies.",
    "**Bootstrap historique** (20 000 tirages) des journées $(\\sigma_d, V_d, s)$ et des résidus pour les surfaces non paramétriques ; 2 000 rééchantillonnages pour les intervalles de confiance des quantiles empiriques.",
    "**Kaplan-Meier** pour les délais censurés et **quantiles à noyau gaussien** (fenêtre $h = 0{,}25$ sur $\\ln t$) pour la décote conditionnelle.",
    "**Dé-lissage de Geltner** avec $\\hat{a} = 1 - \\hat{\\rho}_1$, où $\\hat{\\rho}_1$ est l'autocorrélation d'ordre 1 des rendements publiés.",
    "**SLSQP** pour la liquidation optimale et l'allocation stratégique.")
ap("L'ensemble des codes (Python : NumPy, SciPy, pandas, Matplotlib) est déterministe (graines fixées) et permet de reproduire chaque figure et chaque tableau.")

ah1("Annexe B – Démonstrations")
ah2("B.1 Loi du meilleur prix dans le modèle d'enchère poissonnien")
ap("Soit $N \\sim \\mathcal{P}(\\Lambda)$ et, conditionnellement à $N$, des offres $X_j/V$ i.i.d. de fonction de répartition $F$. Par la formule des probabilités totales et la fonction génératrice de la loi de Poisson :")
aeq(r"\mathbb{P}(M \le x) = \sum_{n\ge 0} e^{-\Lambda}\frac{\Lambda^{n}}{n!}F(x)^{n} = \exp\left(-\Lambda\left(1 - F(x)\right)\right),", "eq:b1")
ap("où l'événement $\\{N = 0\\}$ (de probabilité $e^{-\\Lambda}$) est compté dans $\\{M \\le x\\}$ par convention. Conditionnellement à $N \\ge 1$, on obtient l'équation [[eq:cdfM]]. "
   "Pour le quantile de niveau $p$, on résout $\\exp(-\\Lambda(1-F(x))) = e^{-\\Lambda} + p\\,(1 - e^{-\\Lambda})$, soit $F(x) = 1 + \\ln\\left(e^{-\\Lambda} + p(1-e^{-\\Lambda})\\right)/\\Lambda$, puis $x = \\exp(\\mu_b + \\sigma_b\\,\\Phi^{-1}(F(x)))$ ; "
   "l'équation [[eq:qM]] en découle avec $p = 1 - \\alpha$. On vérifie que $\\Delta\\mathrm{PTV}_{\\alpha}(t)$ est décroissante en $t$ : $\\Lambda \\mapsto 1 + \\ln(e^{-\\Lambda} + p(1-e^{-\\Lambda}))/\\Lambda$ est croissante, conformément à la propriété [[eq:axiomes]].")
ah2("B.2 Vraisemblance du maximum de n offres")
ap("Si $n$ offres log-normales sont reçues, la densité de $\\ln M$ est celle du maximum de $n$ variables gaussiennes, $f(y) = \\frac{n}{\\sigma_b}\\varphi(z)\\Phi(z)^{n-1}$ avec $z = (y - \\mu_b)/\\sigma_b$, d'où l'équation [[eq:mle]]. "
   "La vraisemblance du nombre d'offres est poissonnienne de paramètre $\\nu m_i$ ; elle se factorise et donne $\\hat{\\nu} = \\sum_i n_i / \\sum_i m_i$, de variance asymptotique $\\hat{\\nu}/\\sum_i m_i$.")
ah2("B.3 Nombre d'acheteurs nécessaire")
ap("Les offres étant indépendantes, $\\mathbb{P}(M_N < xV_0) = F(x)^{N}$. La condition $1 - F(x)^{N} \\ge p$ équivaut à $N \\ln F(x) \\le \\ln(1-p)$, soit, puisque $\\ln F(x) < 0$, $N \\ge \\ln(1-p)/\\ln F(x)$ : c'est l'équation [[eq:Nstar]]. "
   "Le délai nécessaire pour réunir $N^{*}$ acheteurs dans un processus de Poisson d'intensité $\\nu$ suit une loi Gamma$(N^{*}, \\nu)$.")
ah2("B.4 Poids optimal de l'indicateur synthétique")
ap("Le critère $J(x) = \\sum_i (x(I_{1,i} - I_{2,i}) + I_{2,i} - S_i)^2$ est un polynôme du second degré en $x$, de coefficient dominant $\\lVert I_1 - I_2 \\rVert^{2} > 0$. Sa dérivée s'annule en $x_0 = \\langle S - I_2, I_1 - I_2\\rangle / \\lVert I_1 - I_2\\rVert^{2}$ ; la convexité de $J$ implique que le minimum sur $[0,1]$ est atteint en la projection de $x_0$ sur $[0,1]$, d'où l'équation [[eq:xstar]].")

ah1("Annexe C – Hypothèses de l'application ALM")
rows = [[{"CASH": "Trésorerie", "OATFR": "OAT 10 ans", "UST": "Treasury 10 ans", "TTE": "TotalEnergies", "LVMH": "LVMH", "CAC": "ETF CAC 40", "SPX": "ETF S&P 500", "RE": "Bureaux", "PE": "Private Equity"}[k],
         pct(A["W0"][k], 1), pct(A["MU"][k], 1), pct(A["vol_ann"][k], 1), pct(A["SHOCK"][k], 0), fr(A["Lsc"][k], 2)] for k in A["KEYS"]]
atab(["Actif", "Poids actuel", "Rendement espéré", "Volatilité", "Choc de valeur", "Score L"], rows,
     "Hypothèses de l'application ALM (rendements espérés prospectifs, volatilités estimées sur les données générées).", [3.4, 2.4, 2.8, 2.4, 2.4, 2.0])
ap("Bornes d'allocation : 60 % pour l'OAT, 15 % pour chacun des autres actifs, 10 % pour le Private Equity. Probabilité annuelle de vente forcée : 5 %. Taux de financement d'urgence : 8 % ; pénalité d'impasse : 2 % ; horizon de passif : 30 jours.")
