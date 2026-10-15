# Mesurer la liquidité en finance — application interactive

*Version du 15/10/2026 — Matthieu Moreau, Frédéric Planchet*

Application Streamlit (français, anglais, allemand) accompagnant l'article
« Mesurer la liquidité des actifs financiers : liquidité juridique, liquidité financière et indicateur synthétique.
Application à la gestion actif-passif d'un assureur prévoyance ».

| Onglet | Contenu interactif |
|---|---|
| Accueil | Concepts, surface ΔPTV, résultats de l'article |
| Actifs cotés | Loi d'impact en racine carrée, coût ΔP(Q,t), quantile 99,5 %, surface 3D |
| Actifs non cotés | Modèle d'enchère poissonnien, décote selon le délai, nombre d'acheteurs N* |
| Liquidité juridique | Délai minimal de cession, notation lettrée A–F |
| Indicateur synthétique | L = x·I₁ + (1−x)·I₂, calibration de x*, carte de liquidité |
| ALM prévoyance | Stress de passif, échelle de liquidité, ratio RL, allocation |
| Données de l'article | Historiques fictifs calibrés 2015-2025 |
| Codes Python de l'article | Tous les scripts de l'article, consultables et téléchargeables |

Données fictives calibrées, à visée pédagogique — ce n'est pas un conseil en investissement.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure

```
app.py            application Streamlit
i18n.py           textes FR / EN / DE
models.py         modèles de liquidité (fonctions pures)
data/             résultats et données fictives de l'article
article_code/     scripts Python ayant produit l'article
requirements.txt  dépendances
.streamlit/       thème
```

## Publier sur Streamlit Community Cloud

1. Se connecter sur <https://share.streamlit.io> avec le compte GitHub qui héberge ce dépôt.
2. Cliquer sur **Create app** → **Deploy a public app from GitHub** (ou *Yup, I have an app*).
3. Renseigner : dépôt `<compte>/<nom-du-dépôt>`, branche `main`, fichier principal `app.py`.
4. (Facultatif) **Advanced settings** → choisir Python 3.12 ; choisir une URL personnalisée, par exemple `liquidite-finance.streamlit.app`.
5. Cliquer sur **Deploy**. Le premier déploiement installe `requirements.txt` (2 à 5 minutes).
6. Chaque `git push` sur `main` redéploie automatiquement l'application.

Pour un dépôt privé, autoriser Streamlit à accéder aux dépôts privés lors de la connexion GitHub ;
l'application peut ensuite rester publique ou être restreinte à des comptes invités (*Share* → *Who can view this app*).
