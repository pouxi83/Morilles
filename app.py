import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel AI - Haut-Var Expert", page_icon="🍄", layout="wide")

# --- 1. MÉTÉO & LOGIQUE ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.60&longitude=6.05&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        return sum(data['daily']['precipitation_sum'][:7]), data['daily']['temperature_2m_max'][0]
    except: return 0.0, 15.0

precip_reelle, tmax = get_weather()

# --- 2. VOS POINTS RÉELS (HISTORIQUE) ---
# Ces points servent de base pour adapter les prédictions
points_reels = [
    {"lat": 43.5867, "lon": 6.0524, "nom": "Trouvaille 1 (460m)", "desc": "Calcaire Jurassique dur"},
    {"lat": 43.6085, "lon": 6.0041, "nom": "Trouvaille 2 (530m)", "desc": "Marnes Néocomien"}
]

# --- 3. INTERFACE LATÉRALE ---
st.sidebar.title("🧭 Expert Haut-Var")
mode_test = st.sidebar.checkbox("Simuler Pluie (Voir Zones)", value=True)
alt_target = st.sidebar.slider("Altitude cible (m)", 300, 850, 480)

precip = 20.0 if mode_test else precip_reelle
is_ideal = precip >= 15 and 10 <= tmax <= 22

# --- 4. ZONES PRÉDICTIVES (ADAPTÉES À VOS POINTS) ---
hotspots = [
    # Zones basées sur vos coordonnées
    {"nom": "Extension Secteur Est", "coords": [43.5880, 6.0550], "alt": 465, "info": "Même veine que votre point 1"},
    {"nom": "Extension Secteur Nord", "coords": [43.6095, 6.0060], "alt": 525, "info": "Même roche que votre point 2"},
    # Zones classiques à fort potentiel
    {"nom": "Tavernes - Ferrages", "coords": [43.5985, 6.0260], "alt": 420, "info": "Thalweg humide"},
    {"nom": "Montmeyan - Ravin", "coords": [43.6350, 6.0450], "alt": 480, "info": "Vallon encaissé"},
    {"nom": "Fox - Bois de la Plaine", "coords": [43.5950, 6.1020], "alt": 450, "info": "Lisières calcaires"}
]

# --- 5. CARTE ---
st.title("🎯 Morel Sniper : Analyse de Terrain")

m = folium.Map(location=[43.60, 6.05], zoom_start=12, tiles=None)

# Fond de carte
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='1. Relief').add_to(m)

# Couches SIG (Végétation, Géologie, Hydro)
for layer in [
    {"url": "https://data.geopf.ign.fr/wms-r/wms", "lay": "LANDCOVER.FORESTINVENTORY.V2", "name": "2. Végétation (IGN)"},
    {"url": "https://geoservices.brgm.fr/geologie", "lay": "GEOLOGIE", "name": "3. Géologie (BRGM)"},
    {"url": "https://data.geopf.ign.fr/wms-r/wms", "lay": "HYDROGRAPHY.NETWORK", "name": "4. Ruisseaux (Eau)"}
]:
    folium.WmsTileLayer(url=layer["url"], layers=layer["lay"], name=layer["name"], 
                        transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

# AFFICHAGE DE VOS TROUVAILLES (OR)
for pt in points_reels:
    folium.Marker(
        location=[pt["lat"], pt["lon"]],
        icon=folium.Icon(color='orange', icon='star'),
        popup=f"🏆 <b>{pt['nom']}</b><br>{pt['desc']}"
    ).add_to(m)

# AFFICHAGE DES CIBLES (ROUGE)
if is_ideal:
    for spot in hotspots:
        # Filtre altitude intelligent
        if abs(spot["alt"] - alt_target) <= 120:
            folium.Circle(
                location=spot["coords"], radius=280, color="red", fill=True, fill_opacity=0.3,
                popup=f"<b>ZIBE PROBABLE</b><br>Alt: {spot['alt']}m<br>{spot['info']}"
            ).add_to(m)

# Outils GPS
plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# Affichage final
st_folium(m, width="100%", height=700)

st.markdown("---")
st.write("📈 **Analyse de vos données** : Votre point n°2 à **530m** indique que la poussée est active sur les plateaux. Réglez le curseur sur 500m+ pour voir les zones similaires.")
