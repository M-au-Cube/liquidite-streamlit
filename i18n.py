"""Textes de l'interface en français, anglais et allemand."""

LANGS = {"Français": "fr", "English": "en", "Deutsch": "de"}

T = {
# ---------------------------------------------------------------- général
"app_title": {"fr": "Mesurer la liquidité en finance", "en": "Measuring liquidity in finance", "de": "Liquidität in der Finanzwirtschaft messen"},
"app_sub": {"fr": "Application interactive accompagnant l'article « Mesurer la liquidité des actifs financiers : liquidité juridique, liquidité financière et indicateur synthétique » — M. Moreau, F. Planchet",
            "en": "Interactive companion to the paper “Measuring the liquidity of financial assets: legal liquidity, financial liquidity and a synthetic indicator” — M. Moreau, F. Planchet",
            "de": "Interaktive Begleitanwendung zum Artikel „Die Liquidität von Finanzanlagen messen: rechtliche Liquidität, finanzielle Liquidität und ein synthetischer Indikator“ — M. Moreau, F. Planchet"},
"date": {"fr": "Version du 15/10/2026", "en": "Version of 15/10/2026", "de": "Version vom 15.10.2026"},
"lang": {"fr": "Langue", "en": "Language", "de": "Sprache"},
"disclaimer": {"fr": "Données fictives calibrées, à visée pédagogique. Ceci n'est pas un conseil en investissement.",
               "en": "Calibrated fictitious data for teaching purposes. This is not investment advice.",
               "de": "Kalibrierte fiktive Daten zu Lehrzwecken. Dies ist keine Anlageberatung."},
"tabs": {"fr": ["Accueil", "Actifs cotés", "Actifs non cotés", "Liquidité juridique", "Indicateur synthétique", "ALM prévoyance", "Données de l'article", "Codes Python de l'article"],
         "en": ["Home", "Listed assets", "Unlisted assets", "Legal liquidity", "Synthetic indicator", "Protection-insurer ALM", "Paper data", "Python code of the paper"],
         "de": ["Start", "Börsennotierte Anlagen", "Nicht börsennotierte Anlagen", "Rechtliche Liquidität", "Synthetischer Indikator", "ALM Risikoversicherer", "Daten des Artikels", "Python-Code des Artikels"]},
"assets": {"fr": {"CAC": "ETF CAC 40", "SPX": "ETF S&P 500", "OATFR": "OAT 10 ans", "UST": "Treasury 10 ans", "TTE": "Obligation TotalEnergies 10 ans", "LVMH": "Obligation LVMH 10 ans", "RE": "Immeuble de bureaux", "PE": "Private Equity small caps", "CASH": "Trésorerie"},
           "en": {"CAC": "CAC 40 ETF", "SPX": "S&P 500 ETF", "OATFR": "French OAT 10y", "UST": "US Treasury 10y", "TTE": "TotalEnergies 10y bond", "LVMH": "LVMH 10y bond", "RE": "Office building", "PE": "Small-cap private equity", "CASH": "Cash"},
           "de": {"CAC": "ETF CAC 40", "SPX": "ETF S&P 500", "OATFR": "OAT 10 J. (Frankreich)", "UST": "US-Treasury 10 J.", "TTE": "Anleihe TotalEnergies 10 J.", "LVMH": "Anleihe LVMH 10 J.", "RE": "Bürogebäude", "PE": "Private Equity Small Caps", "CASH": "Liquide Mittel"}},
# ---------------------------------------------------------------- accueil
"home_md": {
"fr": """
### Deux liquidités
La liquidité d'un actif est sa capacité à être vendu **rapidement**, en **quantité** importante, **sans perte de valeur**. L'article distingue :

* la **liquidité juridique** (ou physique) : le délai incompressible imposé par le droit et l'organisation des marchés — règlement-livraison T+1/T+2, droit de préemption urbain et acte notarié pour un immeuble, agrément et préemption pour une part de Private Equity ;
* la **liquidité financière** : la décote subie à la vente (ou la surcote à l'achat) faute de contreparties, fonction de la quantité vendue $Q$ et du délai $t$.

### La surface ΔPTV
Le coût unitaire de liquidité est la variable aléatoire $\\Delta P(Q,t) = 1 - \\Pi(Q,t)/Q$, où $\\Pi$ est le produit net de cession. L'indicateur est son quantile de niveau $\\alpha$ :
""",
"en": """
### Two kinds of liquidity
An asset is liquid when it can be sold **quickly**, in **large size**, **without losing value**. The paper separates:

* **legal (physical) liquidity**: the incompressible delay imposed by law and market organisation — T+1/T+2 settlement, municipal pre-emption right and notarial deed for a building, approval and pre-emption for a private equity stake;
* **financial liquidity**: the discount suffered when selling (or the premium paid when buying) because counterparties are missing, as a function of the amount sold $Q$ and of the delay $t$.

### The ΔPTV surface
The unit liquidity cost is the random variable $\\Delta P(Q,t) = 1 - \\Pi(Q,t)/Q$, where $\\Pi$ is the net sale proceeds. The indicator is its quantile at level $\\alpha$:
""",
"de": """
### Zwei Arten von Liquidität
Eine Anlage ist liquide, wenn sie **schnell**, in **großem Umfang** und **ohne Wertverlust** verkauft werden kann. Der Artikel unterscheidet:

* die **rechtliche (physische) Liquidität**: die nicht verkürzbare Frist, die Recht und Marktorganisation vorgeben — Abwicklung T+1/T+2, kommunales Vorkaufsrecht und notarielle Urkunde bei einer Immobilie, Zustimmung und Vorkaufsrechte bei einer Private-Equity-Beteiligung;
* die **finanzielle Liquidität**: der Abschlag beim Verkauf (bzw. Aufschlag beim Kauf) mangels Gegenparteien, abhängig von der verkauften Menge $Q$ und der Frist $t$.

### Die ΔPTV-Fläche
Die Liquiditätskosten je Einheit sind die Zufallsvariable $\\Delta P(Q,t) = 1 - \\Pi(Q,t)/Q$, wobei $\\Pi$ der Nettoverkaufserlös ist. Der Indikator ist ihr Quantil zum Niveau $\\alpha$:
"""},
"home_md2": {
"fr": """
avec la médiane (scénario central) et le quantile 99,5 % (scénario stressé, seuil de Solvabilité II).

### Comment utiliser l'application
Chaque onglet permet de faire varier les paramètres et d'observer les résultats en direct :
1. **Actifs cotés** — loi d'impact en racine carrée et surface ΔPTV par simulation ;
2. **Actifs non cotés** — modèle d'enchère à arrivée poissonnienne d'acheteurs, et calcul du nombre d'acheteurs nécessaire pour vendre au juste prix ;
3. **Liquidité juridique** — délai minimal de cession et notation lettrée ;
4. **Indicateur synthétique** — $L = x\\,I_1 + (1-x)\\,I_2$ et calibration du poids $x$ ;
5. **ALM prévoyance** — besoins de trésorerie en stress et échelle de liquidité ;
6. **Données** et **codes Python** de l'article.
""",
"en": """
with the median (central scenario) and the 99.5% quantile (stressed scenario, Solvency II threshold).

### How to use the app
Each tab lets you change the parameters and see the results live:
1. **Listed assets** — square-root impact law and ΔPTV surface by simulation;
2. **Unlisted assets** — Poisson-arrival auction model, and number of buyers needed to sell at a fair price;
3. **Legal liquidity** — minimum sale delay and letter rating;
4. **Synthetic indicator** — $L = x\\,I_1 + (1-x)\\,I_2$ and calibration of the weight $x$;
5. **Protection-insurer ALM** — stressed cash needs and liquidity ladder;
6. The paper's **data** and **Python code**.
""",
"de": """
mit dem Median (zentrales Szenario) und dem 99,5-%-Quantil (Stressszenario, Schwelle von Solvency II).

### So verwenden Sie die Anwendung
In jedem Reiter können Sie die Parameter verändern und die Ergebnisse live verfolgen:
1. **Börsennotierte Anlagen** — Quadratwurzelgesetz des Marktimpacts und ΔPTV-Fläche per Simulation;
2. **Nicht börsennotierte Anlagen** — Auktionsmodell mit Poisson-Ankunft von Käufern und Anzahl der Käufer für einen fairen Preis;
3. **Rechtliche Liquidität** — minimale Verkaufsfrist und Buchstabenrating;
4. **Synthetischer Indikator** — $L = x\\,I_1 + (1-x)\\,I_2$ und Kalibrierung des Gewichts $x$;
5. **ALM Risikoversicherer** — gestresster Liquiditätsbedarf und Liquiditätsleiter;
6. **Daten** und **Python-Code** des Artikels.
"""},
"home_results": {"fr": "Résultats de l'article : indicateur synthétique par type d'actif", "en": "Paper results: synthetic indicator by asset type", "de": "Ergebnisse des Artikels: synthetischer Indikator je Anlageart"},
"col_asset": {"fr": "Type d'actif", "en": "Asset type", "de": "Anlageart"},
"col_L": {"fr": "Indicateur de liquidité L", "en": "Liquidity indicator L", "de": "Liquiditätsindikator L"},
"col_note": {"fr": "Note", "en": "Rating", "de": "Note"},
# ---------------------------------------------------------------- cotés
"lst_intro": {"fr": "Le coût de vente d'un montant $Q$ étalé sur $t$ jours de bourse se décompose en frais, demi-fourchette et impact de marché (loi en racine carrée) :",
              "en": "The cost of selling an amount $Q$ spread over $t$ trading days splits into fees, half-spread and market impact (square-root law):",
              "de": "Die Kosten für den Verkauf eines Betrags $Q$ über $t$ Handelstage bestehen aus Gebühren, halbem Spread und Marktimpact (Quadratwurzelgesetz):"},
"preset": {"fr": "Paramètres de départ (calibrés dans l'article)", "en": "Starting parameters (calibrated in the paper)", "de": "Startparameter (im Artikel kalibriert)"},
"params": {"fr": "Paramètres", "en": "Parameters", "de": "Parameter"},
"sigma_ann": {"fr": "Volatilité annuelle σ (%)", "en": "Annual volatility σ (%)", "de": "Jährliche Volatilität σ (%)"},
"adv": {"fr": "Volume quotidien V (M€)", "en": "Daily volume V (€m)", "de": "Tagesvolumen V (Mio. €)"},
"spread": {"fr": "Fourchette s (pb)", "en": "Bid-ask spread s (bp)", "de": "Geld-Brief-Spanne s (Bp)"},
"fees": {"fr": "Frais f (pb)", "en": "Fees f (bp)", "de": "Gebühren f (Bp)"},
"Y": {"fr": "Coefficient d'impact Y", "en": "Impact coefficient Y", "de": "Impactkoeffizient Y"},
"delta": {"fr": "Exposant δ", "en": "Exponent δ", "de": "Exponent δ"},
"Q": {"fr": "Montant vendu Q (M€)", "en": "Amount sold Q (€m)", "de": "Verkaufter Betrag Q (Mio. €)"},
"t": {"fr": "Durée d'exécution t (jours de bourse)", "en": "Execution time t (trading days)", "de": "Ausführungsdauer t (Handelstage)"},
"unc": {"fr": "Incertitude de marché (dispersion de σ, V, s) — multiplicateur", "en": "Market uncertainty (dispersion of σ, V, s) — multiplier", "de": "Marktunsicherheit (Streuung von σ, V, s) — Multiplikator"},
"m_total": {"fr": "Coût médian ΔP₅₀", "en": "Median cost ΔP₅₀", "de": "Mediankosten ΔP₅₀"},
"m_stress": {"fr": "Coût stressé ΔPTV₉₉,₅", "en": "Stressed cost ΔPTV₉₉.₅", "de": "Gestresste Kosten ΔPTV₉₉,₅"},
"m_euro": {"fr": "Coût en euros (médian)", "en": "Cost in euros (median)", "de": "Kosten in Euro (Median)"},
"m_part": {"fr": "Taux de participation Q/(V·t)", "en": "Participation rate Q/(V·t)", "de": "Teilnahmequote Q/(V·t)"},
"decomp": {"fr": "Décomposition du coût médian (pb)", "en": "Median cost breakdown (bp)", "de": "Zerlegung der Mediankosten (Bp)"},
"c_fees": {"fr": "Frais", "en": "Fees", "de": "Gebühren"}, "c_half": {"fr": "Demi-fourchette", "en": "Half-spread", "de": "Halber Spread"},
"c_imp": {"fr": "Impact", "en": "Impact", "de": "Impact"},
"curve_Q": {"fr": "Coût ΔP en fonction de Q (médiane et q99,5 %)", "en": "Cost ΔP as a function of Q (median and 99.5% quantile)", "de": "Kosten ΔP in Abhängigkeit von Q (Median und 99,5-%-Quantil)"},
"surface": {"fr": "Surface ΔPTV médiane (log₁₀ pb)", "en": "Median ΔPTV surface (log₁₀ bp)", "de": "Mediane ΔPTV-Fläche (log₁₀ Bp)"},
"x_Q": {"fr": "Q (M€)", "en": "Q (€m)", "de": "Q (Mio. €)"}, "x_t": {"fr": "t (jours)", "en": "t (days)", "de": "t (Tage)"},
"y_bp": {"fr": "ΔP (pb)", "en": "ΔP (bp)", "de": "ΔP (Bp)"},
"lst_note": {"fr": "Doubler la durée d'exécution divise l'impact par √2 ; doubler la quantité le multiplie par √2. La fourchette et les frais ne dépendent ni de Q ni de t.",
             "en": "Doubling the execution time divides the impact by √2; doubling the amount multiplies it by √2. Spread and fees depend on neither Q nor t.",
             "de": "Eine Verdopplung der Ausführungsdauer teilt den Impact durch √2; eine Verdopplung der Menge multipliziert ihn mit √2. Spread und Gebühren hängen weder von Q noch von t ab."},
# ---------------------------------------------------------------- non cotés
"unl_intro": {"fr": "Un actif non coté est vendu en bloc. Après le délai juridique $T_{leg}$, des acheteurs arrivent au rythme $\\nu$ et font des offres log-normales $X_j = V\\,e^{\\mu_b+\\sigma_b\\varepsilon_j}$ ; le vendeur retient la meilleure. Plus le délai est long, plus il reçoit d'offres et plus la décote baisse.",
              "en": "An unlisted asset is sold as a block. After the legal delay $T_{leg}$, buyers arrive at rate $\\nu$ and make log-normal bids $X_j = V\\,e^{\\mu_b+\\sigma_b\\varepsilon_j}$; the seller takes the best one. The longer the delay, the more bids and the smaller the discount.",
              "de": "Eine nicht börsennotierte Anlage wird als Block verkauft. Nach der rechtlichen Frist $T_{leg}$ treffen Käufer mit der Rate $\\nu$ ein und geben log-normale Gebote $X_j = V\\,e^{\\mu_b+\\sigma_b\\varepsilon_j}$ ab; der Verkäufer nimmt das beste. Je länger die Frist, desto mehr Gebote und desto kleiner der Abschlag."},
"nu": {"fr": "Rythme d'arrivée ν (offres / mois)", "en": "Arrival rate ν (bids / month)", "de": "Ankunftsrate ν (Gebote / Monat)"},
"mu_b": {"fr": "Moyenne des offres μ_b (log)", "en": "Mean bid μ_b (log)", "de": "Mittleres Gebot μ_b (log)"},
"sig_b": {"fr": "Dispersion des offres σ_b", "en": "Bid dispersion σ_b", "de": "Streuung der Gebote σ_b"},
"Tleg": {"fr": "Délai juridique T_leg (jours)", "en": "Legal delay T_leg (days)", "de": "Rechtliche Frist T_leg (Tage)"},
"alpha": {"fr": "Seuil α (%)", "en": "Confidence level α (%)", "de": "Konfidenzniveau α (%)"},
"t_sale": {"fr": "Délai total de cession t (jours)", "en": "Total sale delay t (days)", "de": "Gesamte Verkaufsfrist t (Tage)"},
"m_med": {"fr": "Décote médiane", "en": "Median discount", "de": "Medianabschlag"},
"m_q": {"fr": "Décote au seuil α", "en": "Discount at level α", "de": "Abschlag zum Niveau α"},
"m_fail": {"fr": "Probabilité d'aucune offre", "en": "Probability of no bid", "de": "Wahrscheinlichkeit keines Gebots"},
"m_tmin": {"fr": "Délai minimal t_min,α", "en": "Minimum delay t_min,α", "de": "Minimale Frist t_min,α"},
"curve_t": {"fr": "Décote en fonction du délai (médiane et quantile α)", "en": "Discount as a function of the delay (median and α quantile)", "de": "Abschlag in Abhängigkeit von der Frist (Median und α-Quantil)"},
"y_disc": {"fr": "Décote (%)", "en": "Discount (%)", "de": "Abschlag (%)"},
"hist": {"fr": "Distribution simulée de la décote au délai t (10 000 ventes)", "en": "Simulated discount distribution at delay t (10,000 sales)", "de": "Simulierte Verteilung des Abschlags bei Frist t (10 000 Verkäufe)"},
"nstar_title": {"fr": "Combien d'acheteurs pour vendre au juste prix ?", "en": "How many buyers to sell at a fair price?", "de": "Wie viele Käufer für einen fairen Preis?"},
"nstar_txt": {"fr": "Probabilité qu'au moins une offre sur $N$ atteigne la fraction $x$ de la valeur : $1 - F(x)^N$. Nombre minimal d'acheteurs :",
              "en": "Probability that at least one of $N$ bids reaches the fraction $x$ of value: $1 - F(x)^N$. Minimum number of buyers:",
              "de": "Wahrscheinlichkeit, dass mindestens eines von $N$ Geboten den Anteil $x$ des Werts erreicht: $1 - F(x)^N$. Mindestanzahl der Käufer:"},
"x_frac": {"fr": "Fraction de la valeur visée x (%)", "en": "Target fraction of value x (%)", "de": "Angestrebter Wertanteil x (%)"},
"p_conf": {"fr": "Probabilité souhaitée p (%)", "en": "Desired probability p (%)", "de": "Gewünschte Wahrscheinlichkeit p (%)"},
"m_nstar": {"fr": "Acheteurs nécessaires N*", "en": "Buyers needed N*", "de": "Benötigte Käufer N*"},
"m_ndays": {"fr": "Délai pour les réunir (médiane)", "en": "Time to gather them (median)", "de": "Zeit, um sie zu finden (Median)"},
"x_N": {"fr": "Nombre d'acheteurs N", "en": "Number of buyers N", "de": "Anzahl der Käufer N"},
"days": {"fr": "jours", "en": "days", "de": "Tage"},
"impossible": {"fr": "inatteignable", "en": "unreachable", "de": "unerreichbar"},
# ---------------------------------------------------------------- juridique
"leg_intro": {"fr": "Le délai minimal de cession additionne le délai juridique et le temps nécessaire pour trouver les contreparties. Pour un titre coté vendu à une participation maximale $\\rho$ du volume en marché déprimé, $\\tau = Q/(\\rho V)$ ; pour un actif non coté, $\\tau_\\alpha = \\ln(1/(1-\\alpha))/\\nu$.",
              "en": "The minimum sale delay adds the legal delay and the time needed to find counterparties. For a listed security sold at maximum participation $\\rho$ of a depressed volume, $\\tau = Q/(\\rho V)$; for an unlisted asset, $\\tau_\\alpha = \\ln(1/(1-\\alpha))/\\nu$.",
              "de": "Die minimale Verkaufsfrist addiert die rechtliche Frist und die Zeit für die Suche nach Gegenparteien. Für ein börsennotiertes Wertpapier, das mit einer maximalen Teilnahmequote $\\rho$ an einem gedrückten Volumen verkauft wird, gilt $\\tau = Q/(\\rho V)$; für eine nicht notierte Anlage $\\tau_\\alpha = \\ln(1/(1-\\alpha))/\\nu$."},
"leg_table": {"fr": "Délais juridiques retenus dans l'article", "en": "Legal delays used in the paper", "de": "Im Artikel verwendete rechtliche Fristen"},
"leg_calc": {"fr": "Calculateur de délai minimal (titre coté)", "en": "Minimum delay calculator (listed security)", "de": "Rechner für die minimale Frist (börsennotiertes Wertpapier)"},
"rho": {"fr": "Participation maximale ρ (%)", "en": "Maximum participation ρ (%)", "de": "Maximale Teilnahmequote ρ (%)"},
"Vlow": {"fr": "Volume en marché déprimé (M€ / jour)", "en": "Depressed-market volume (€m / day)", "de": "Volumen im gedrückten Markt (Mio. € / Tag)"},
"rating_title": {"fr": "Notation lettrée (A à F)", "en": "Letter rating (A to F)", "de": "Buchstabenrating (A bis F)"},
"rating_txt": {"fr": "Note juridique selon le délai légal, note d'observabilité selon le nombre d'intervenants par jour ; la note finale est la plus mauvaise des deux.",
               "en": "Legal rating from the legal delay, observability rating from the number of participants per day; the final rating is the worse of the two.",
               "de": "Rechtliche Note nach der gesetzlichen Frist, Beobachtbarkeitsnote nach der Zahl der Marktteilnehmer pro Tag; die Endnote ist die schlechtere der beiden."},
"legal_days": {"fr": "Délai légal (jours)", "en": "Legal delay (days)", "de": "Gesetzliche Frist (Tage)"},
"obs": {"fr": "Intervenants ou transactions par jour", "en": "Participants or trades per day", "de": "Teilnehmer oder Transaktionen pro Tag"},
"n_leg": {"fr": "Note juridique", "en": "Legal rating", "de": "Rechtliche Note"}, "n_obs": {"fr": "Note d'observabilité", "en": "Observability rating", "de": "Beobachtbarkeitsnote"},
"n_fin": {"fr": "Note finale", "en": "Final rating", "de": "Endnote"},
"settle": {"fr": "Contrainte juridique", "en": "Legal constraint", "de": "Rechtliche Einschränkung"},
# ---------------------------------------------------------------- synthétique
"syn_intro": {"fr": "Les deux liquidités sont ramenées à des scores entre 0 et 1 (1 = parfaitement liquide) puis combinées :",
              "en": "Both liquidities are mapped to scores between 0 and 1 (1 = perfectly liquid) and then combined:",
              "de": "Beide Liquiditäten werden auf Werte zwischen 0 und 1 abgebildet (1 = vollkommen liquide) und dann kombiniert:"},
"x": {"fr": "Poids de la liquidité juridique x", "en": "Weight of legal liquidity x", "de": "Gewicht der rechtlichen Liquidität x"},
"use_xstar": {"fr": "Utiliser x* calibré sur le coût ALM", "en": "Use x* calibrated on the ALM cost", "de": "Auf ALM-Kosten kalibriertes x* verwenden"},
"Tmax": {"fr": "Horizon maximal T_max (jours)", "en": "Maximum horizon T_max (days)", "de": "Maximaler Horizont T_max (Tage)"},
"H": {"fr": "Horizon de passif H (jours)", "en": "Liability horizon H (days)", "de": "Verbindlichkeitshorizont H (Tage)"},
"re": {"fr": "Taux de financement d'urgence r_e (%)", "en": "Emergency funding rate r_e (%)", "de": "Notfinanzierungssatz r_e (%)"},
"pi": {"fr": "Pénalité d'impasse π (%)", "en": "Shortfall penalty π (%)", "de": "Fehlbetragsstrafe π (%)"},
"edit": {"fr": "Vous pouvez modifier le délai minimal et la décote de chaque actif dans le tableau.", "en": "You can edit each asset's minimum delay and discount in the table.", "de": "Sie können die minimale Frist und den Abschlag jeder Anlage in der Tabelle ändern."},
"c_tmin": {"fr": "t_min (jours)", "en": "t_min (days)", "de": "t_min (Tage)"}, "c_dp": {"fr": "ΔPTV₉₉,₅ (%)", "en": "ΔPTV₉₉.₅ (%)", "de": "ΔPTV₉₉,₅ (%)"},
"map": {"fr": "Carte de liquidité", "en": "Liquidity map", "de": "Liquiditätskarte"},
"sens": {"fr": "Sensibilité de L au poids x", "en": "Sensitivity of L to the weight x", "de": "Sensitivität von L gegenüber dem Gewicht x"},
"xstar_is": {"fr": "Poids calibré x*", "en": "Calibrated weight x*", "de": "Kalibriertes Gewicht x*"},
# ---------------------------------------------------------------- ALM
"alm_intro": {"fr": "Assureur prévoyance fictif (actif de 620 M€). Les flux mensuels de prestations (décès, incapacité, invalidité) et de cotisations sont simulés sur 12 mois ; la liquidité mobilisable de chaque actif à l'horizon h est nette du coût de liquidité stressé.",
              "en": "Fictitious protection insurer (€620m of assets). Monthly benefit flows (death, incapacity, disability) and premiums are simulated over 12 months; the cash each asset can raise by horizon h is net of the stressed liquidity cost.",
              "de": "Fiktiver Risikoversicherer (620 Mio. € Aktiva). Monatliche Leistungen (Tod, Arbeitsunfähigkeit, Invalidität) und Beiträge werden über 12 Monate simuliert; die bis zum Horizont h mobilisierbare Liquidität jeder Anlage ist um die gestressten Liquiditätskosten bereinigt."},
"stress_par": {"fr": "Scénario de stress", "en": "Stress scenario", "de": "Stressszenario"},
"mort": {"fr": "Multiplicateur de mortalité (6 mois)", "en": "Mortality multiplier (6 months)", "de": "Sterblichkeitsmultiplikator (6 Monate)"},
"ij": {"fr": "Multiplicateur d'arrêts de travail (3 mois)", "en": "Sick-leave multiplier (3 months)", "de": "Multiplikator Arbeitsunfähigkeit (3 Monate)"},
"prem": {"fr": "Baisse des cotisations (%)", "en": "Premium drop (%)", "de": "Beitragsrückgang (%)"},
"oneoff": {"fr": "Sortie exceptionnelle le 1er mois (M€)", "en": "One-off outflow in month 1 (€m)", "de": "Einmaliger Abfluss im 1. Monat (Mio. €)"},
"alloc": {"fr": "Allocation d'actifs (%)", "en": "Asset allocation (%)", "de": "Vermögensallokation (%)"},
"norm_note": {"fr": "Les poids sont renormalisés pour totaliser 100 %.", "en": "Weights are rescaled to sum to 100%.", "de": "Die Gewichte werden auf 100 % normiert."},
"need": {"fr": "Besoin de trésorerie cumulé (M€)", "en": "Cumulative cash need (€m)", "de": "Kumulierter Liquiditätsbedarf (Mio. €)"},
"month": {"fr": "mois", "en": "month", "de": "Monat"},
"ladder": {"fr": "Échelle de liquidité : liquidité mobilisable et besoin q99,5 %", "en": "Liquidity ladder: available cash and 99.5% need", "de": "Liquiditätsleiter: mobilisierbare Liquidität und 99,5-%-Bedarf"},
"need_q": {"fr": "Besoin q99,5 %", "en": "99.5% need", "de": "99,5-%-Bedarf"},
"RL": {"fr": "Ratio de liquidité RL", "en": "Liquidity ratio RL", "de": "Liquiditätsquote RL"},
"Lp": {"fr": "Score de liquidité du portefeuille L_p", "en": "Portfolio liquidity score L_p", "de": "Liquiditätswert des Portfolios L_p"},
"alm_warn": {"fr": "Impasse de trésorerie : la liquidité mobilisable ne couvre pas le besoin stressé à cet horizon.", "en": "Cash shortfall: available liquidity does not cover the stressed need at this horizon.", "de": "Liquiditätsengpass: Die mobilisierbare Liquidität deckt den gestressten Bedarf zu diesem Horizont nicht."},
"alm_ok": {"fr": "Pas d'impasse de trésorerie à 99,5 % sur 12 mois.", "en": "No cash shortfall at 99.5% over 12 months.", "de": "Kein Liquiditätsengpass zu 99,5 % über 12 Monate."},
"horizon": {"fr": "Horizon", "en": "Horizon", "de": "Horizont"},
# ---------------------------------------------------------------- données / codes
"data_intro": {"fr": "Historiques fictifs calibrés utilisés dans l'article (2015-2025). Zones grisées : épisodes de stress.", "en": "Calibrated fictitious histories used in the paper (2015-2025). Shaded areas: stress episodes.", "de": "Im Artikel verwendete kalibrierte fiktive Zeitreihen (2015-2025). Grau: Stressphasen."},
"choose": {"fr": "Actifs affichés", "en": "Assets shown", "de": "Angezeigte Anlagen"},
"base100": {"fr": "Prix (base 100)", "en": "Price (base 100)", "de": "Preis (Basis 100)"},
"deals": {"fr": "Transactions simulées sur actifs non cotés", "en": "Simulated unlisted transactions", "de": "Simulierte Transaktionen nicht notierter Anlagen"},
"download": {"fr": "Télécharger", "en": "Download", "de": "Herunterladen"},
"code_intro": {"fr": "Ensemble des scripts Python ayant produit les données, les analyses, les figures et les documents Word de l'article. Ils sont déterministes (graines fixées) : les exécuter dans l'ordre reproduit l'article.",
               "en": "All Python scripts that produced the paper's data, analyses, figures and Word documents. They are deterministic (fixed seeds): running them in order reproduces the paper.",
               "de": "Alle Python-Skripte, die Daten, Analysen, Abbildungen und Word-Dokumente des Artikels erzeugt haben. Sie sind deterministisch (feste Seeds): In der angegebenen Reihenfolge ausgeführt, reproduzieren sie den Artikel."},
"code_order": {"fr": "Ordre d'exécution", "en": "Execution order", "de": "Ausführungsreihenfolge"},
"code_file": {"fr": "Fichier", "en": "File", "de": "Datei"},
"code_zip": {"fr": "Télécharger tous les codes (.zip)", "en": "Download all code (.zip)", "de": "Gesamten Code herunterladen (.zip)"},
"code_desc": {
  "fr": {"gen_data.py": "Génération des données fictives calibrées", "analysis.py": "Indicateurs de liquidité, surfaces ΔPTV, indicateur synthétique, figures 1-13", "alm.py": "Application ALM prévoyance, figures 14-17", "style.py": "Style graphique commun", "content.py": "Texte de l'article (valeurs lues dans les résultats)", "build_docx.py": "Construction des documents Word ArXiv et BMI", "omml.py": "Conversion LaTeX → équations Word"},
  "en": {"gen_data.py": "Generation of calibrated fictitious data", "analysis.py": "Liquidity indicators, ΔPTV surfaces, synthetic indicator, figures 1-13", "alm.py": "Protection-insurer ALM application, figures 14-17", "style.py": "Common chart style", "content.py": "Paper text (values read from results)", "build_docx.py": "Builds the ArXiv and BMI Word documents", "omml.py": "LaTeX → Word equation conversion"},
  "de": {"gen_data.py": "Erzeugung der kalibrierten fiktiven Daten", "analysis.py": "Liquiditätsindikatoren, ΔPTV-Flächen, synthetischer Indikator, Abbildungen 1-13", "alm.py": "ALM-Anwendung Risikoversicherer, Abbildungen 14-17", "style.py": "Gemeinsamer Diagrammstil", "content.py": "Text des Artikels (Werte aus den Ergebnissen)", "build_docx.py": "Erstellung der Word-Dokumente ArXiv und BMI", "omml.py": "Umwandlung LaTeX → Word-Formeln"}},
"median": {"fr": "médiane", "en": "median", "de": "Median"},
"q995": {"fr": "q99,5 %", "en": "99.5% quantile", "de": "99,5-%-Quantil"},
"qa": {"fr": "quantile α", "en": "α quantile", "de": "α-Quantil"},
"stress_lbl": {"fr": "stress", "en": "stress", "de": "Stress"},
"normal_lbl": {"fr": "normal", "en": "normal", "de": "normal"},
}


def tr(key, lang):
    v = T[key]
    return v[lang] if isinstance(v, dict) and lang in v else v
