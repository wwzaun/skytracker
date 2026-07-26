# ✈️ SkyTracker 
## Installation

```bash
pip install streamlit pandas plotly requests
python generate_db.py
streamlit run app.py
```

## Activer les vrais prix (SerpApi)

### Étape 1 — Créer un compte gratuit
1. Allez sur **https://serpapi.com**
2. Cliquez **"Start Free Trial"**
3. Entrez votre email → vérifiez votre boîte mail
4. Connectez-vous → allez dans **Dashboard**
5. Copiez votre **API Key**

**Free tier : 100 recherches/mois gratuites**

### Étape 2 — Entrer la clé dans l'app
- Lancez l'app : `streamlit run app.py`
- Dans le **menu latéral gauche**, collez votre clé
- Cliquez **"🔌 Activer les prix réels"**
- Relancez une recherche → les vols affichent **"✅ Prix réel"**

### OU via fichier secrets (permanent)
Ouvrez `.streamlit/secrets.toml` et remplacez :
```
SERPAPI_KEY = "votre_vraie_cle_ici"
```

## Structure
```
skytracker/
├── app.py              # Interface Streamlit
├── serpapi_client.py   # Client SerpApi Google Flights
├── generate_db.py      # Génère données de démo
├── skytracker.db       # Base SQLite (démo)
├── .streamlit/
│   └── secrets.toml    # Clé API (ne pas partager)
└── README.md
```

## Fonctionnalités
- ✅ Vrais prix Google Flights en temps réel (avec SerpApi)
- 📊 Données démo si pas de clé
- 🌍 7000+ aéroports mondiaux
- ✈️ 35+ compagnies aériennes
- 🔗 Liens directs vers les sites des compagnies
- 🌿 Émissions CO₂ affichées
- 🗺️ Carte interactive du trajet
- 📈 Graphique évolution des prix
