import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Morel Sniper Pro - Haut-Var", page_icon="🍄", layout="wide")

# --- 1. FONCTION MÉTÉO ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.60&longitude=6.05&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        return sum(data['daily']['precipitation_sum'][:7]), data['daily']['temperature_2m_max'][0]
    except: return 0.0, 15.0

precip_reelle, tmax = get_weather()

# --- 2. VOS TROUVAILLES RÉELLES (ÉTOILES DORÉES) ---
points_reels = [
    {"lat": 43.5867, "lon": 6.0524, "nom": "Trouvaille 1", "alt": 460},
    {"lat": 43.6085, "lon": 6.0041, "nom": "Trouvaille 2", "alt": 530}
]

# --- 3. DASHBOARD LATÉRAL ---
st.sidebar.title("🧭 Contrôle de Chasse")
mode_test = st.sidebar.checkbox("Simuler Pluie (Voir toutes les zones)", value=True)
alt_target = st.sidebar.slider("Altitude cible (m)", 300, 900, 480)

precip = 20.0 if mode_test else precip_reelle
is_ideal = precip >= 12 # Seuil de pluie pour activer les cercles

# --- 4. LES 10 ZONES STRATÉGIQUES (Haut-Var) ---
hotspots = [
    # Secteur Tavernes / Est (Proche point 1)
    {"nom": "Extension Est (Vallon)", "coords": [43.5880, 6.0550], "alt": 465, "info": "Même veine calcaire que votre point 1"},
    {"nom": "Vallon de la Cascade", "coords": [43.5930, 6.0350], "alt": 440, "info": "Humidité garantie au fond"},
    {"nom": "Route de Fox (Bas-côté)", "coords": [43.5960, 6.0750], "alt": 430, "info": "Lisière de feuillus mixte"},
    
    # Secteur Nord / Ouest (Proche point 2)
    {"nom": "Extension Nord (Pente)", "coords": [43.6095, 6.0060], "alt": 525, "info": "Même roche que votre point 2"},
    {"nom": "Plateau des Lauves (Bord)", "coords": [43.6050, 6.0250], "alt": 510, "info": "Eboulis calcaires sous chênes"},
    {"nom": "Pied du Bessillon (Sud)", "coords": [43.5820, 6.0080], "alt": 490, "info": "Zone abritée du vent"},
    
    # Secteurs élargis (Voisins)
    {"nom": "Montmeyan (Entrée)", "coords": [43.6250, 6.0350], "alt": 480, "info": "Zone ombragée humide"},
    {"nom": "Varages (Hauts)", "coords": [43.6010, 5.9650], "alt": 550, "info": "Forêt dense de feuillus"},
    {"nom": "Fox-Amphoux (Plaine)", "coords": [43.5950, 6.1020], "alt": 450, "info": "Terre argilo-calcaire"},
    {"nom": "Vers Aups (Lisière)", "coords": [43.6450, 6.2050], "alt": 650, "info": "Saison plus tardive (Avril)"}
]

# --- 5. CARTE ---
st.title("🎯 Morel Sniper Pro : Tavernes & Haut-Var")

# Centrage de la carte
m = folium.Map(location=[43.60, 6.05], zoom_start=12, tiles=None)

# Couches de fond
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='1. Relief').add_to(m)

# Couches SIG (Végétation, Géologie, Hydro)
couches = [
    ("https://data.geopf.ign.fr/wms-r/wms", "LANDCOVER.FORESTINVENTORY.V2", "2. Végétation (IGN)"),
    ("https://geoservices.brgm.fr/geologie", "GEOLOGIE", "3. Géologie (BRGM)"),
    ("https://data.geopf.ign.fr/wms-r/wms", "HYDROGRAPHY.NETWORK", "4. Ruisseaux (Eau)")
]

for url, layer, name in couches:
    folium.WmsTileLayer(url=url, layers=layer, name=name, transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

# AFFICHAGE DES ÉTOILES (VOS POINTS)
for pt in points_reels:
    folium.Marker(
        location=[pt["lat"], pt["lon"]],
        icon=folium.Icon(color='orange', icon='star'),
        popup=f"🏆 <b>{pt['nom']}</b><br>Alt: {pt['alt']}m"
    ).add_to(m)

# AFFICHAGE DES CIBLES (SI IDÉAL)
if is_ideal:
    for spot in hotspots:
        # Filtre souple : affiche si l'altitude est à +/- 250m du curseur
        if abs(spot["alt"] - alt_target) <= 250:
            folium.Circle(
                location=spot["coords"], radius=300, color="red", fill=True, fill_opacity=0.3,
                popup=f"<b>ZONE SNIPER</b><br>Alt: {spot['alt']}m<br>{spot['info']}"
            ).add_to(m)
            folium.Marker(location=spot["coords"], icon=folium.Icon(color='red', icon='screenshot', prefix='fa')).add_to(m)

# Outils
plugins.LocateControl(flyTo=True).add_to(m)
plugins.Fullscreen().add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# Affichage final
st_folium(m, width="100%", height=700)

st.markdown("---")
st.caption(f"Analyse basée sur vos points : {points_reels[0]['lat']}, {points_reels[0]['lon']} et {points_reels[1]['lat']}, {points_reels[1]['lon']}")
