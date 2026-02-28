import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel Predictor - Tavernes", page_icon="🍄", layout="wide")

# --- 1. GESTION MÉTÉO & SIMULATION ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.59&longitude=6.01&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        return sum(data['daily']['precipitation_sum'][:7]), data['daily']['temperature_2m_max'][0]
    except: return 0.0, 0.0

precip_reelle, tmax = get_weather()

# Mode Simulation pour voir les zones même s'il fait sec
st.sidebar.title("🛠️ Paramètres")
mode_test = st.sidebar.checkbox("Simuler une pluie (>15mm)", value=True)
precip = 20.0 if mode_test else precip_reelle

is_ideal = precip >= 15 and 10 <= tmax <= 22

# --- 2. DÉFINITION DES ZONES À HAUT POTENTIEL ---
# Coordonnées précises basées sur la géologie calcaire de Tavernes
hotspots = [
    {
        "nom": "ZONE A : Vallon des Ferrages",
        "coords": [43.5985, 6.0260],
        "raison": "Intersection calcaire dur et ruissellement. Présence de frênes.",
        "conseil": "Cherchez dans le lit du ruisseau à sec."
    },
    {
        "nom": "ZONE B : Pied du Petit Bessillon (Nord)",
        "coords": [43.5875, 6.0145],
        "raison": "Zone d'éboulis calcaires ombragée. Humidité résiduelle forte.",
        "conseil": "Regardez sous les touffes de lierre."
    },
    {
        "nom": "ZONE C : Ravin de la Blanquière",
        "coords": [43.6060, 6.0380],
        "raison": "Orientation Nord-Est (Ubac). Idéal si le soleil tape fort.",
        "conseil": "Zones moussues et souches pourries."
    },
    {
        "nom": "ZONE D : Secteur Saint-Cassien",
        "coords": [43.5920, 5.9950],
        "raison": "Sol argilo-calcaire (marnes). Excellent pour les morilles blondes.",
        "conseil": "Lisières de bois et vieux vergers."
    },
    {
        "nom": "ZONE E : Plateau des Lauves (Bordures)",
        "coords": [43.6120, 6.0180],
        "raison": "Plateau calcaire avec micro-dépressions retenant l'eau.",
        "conseil": "Zones où les feuilles mortes s'accumulent."
    }
]

# --- 3. INTERFACE & LÉGENDE ---
st.sidebar.markdown("---")
st.sidebar.subheader("📚 Légende de Prospection")
st.sidebar.info("🔵 **Lignes** : Ruisseaux (Humidité)")
st.sidebar.success("🟢 **Zones** : Feuillus (Habitat)")
st.sidebar.warning("🟡 **Couleurs** : Calcaire (Sol)")
st.sidebar.write("📍 **Cibles** : Zones à 90% de probabilité")

# --- 4. LA CARTE ---
st.title("🎯 Zones de Chasse Prédictives - Tavernes")

m = folium.Map(location=[43.5936, 6.0167], zoom_start=14, tiles=None)

# Couches de fond
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='1. Relief').add_to(m)

# Couches SIG (Végétation, Géologie, Hydro)
folium.WmsTileLayer(url="https://data.geopf.ign.fr/wms-r/wms", layers="LANDCOVER.FORESTINVENTORY.V2", 
                    name="2. Végétation (Feuillus)", transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

folium.WmsTileLayer(url="https://geoservices.brgm.fr/geologie", layers="GEOLOGIE", 
                    name="3. Géologie (Calcaire)", transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

folium.WmsTileLayer(url="https://data.geopf.ign.fr/wms-r/wms", layers="HYDROGRAPHY.NETWORK", 
                    name="4. Ruisseaux (Eau)", transparent=True, fmt="image/png", overlay=True, opacity=0.8).add_to(m)

# AFFICHAGE DES ZONES SI CONDITIONS RÉUNIES
if is_ideal:
    for spot in hotspots:
        # On dessine un cercle de 200m autour du point
        folium.Circle(
            location=spot["coords"], radius=200, color="red", fill=True, fill_opacity=0.2,
            popup=f"<b>{spot['nom']}</b><br><i>{spot['raison']}</i><br>💡 {spot['conseil']}"
        ).add_to(m)
        # On ajoute un marqueur au centre
        folium.Marker(location=spot["coords"], icon=folium.Icon(color='red', icon='bullseye')).add_to(m)
else:
    st.warning("⚠️ Les conditions météo ne sont pas optimales. Cochez 'Simuler une pluie' pour voir les zones théoriques.")

# Outils GPS
plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# Affichage final
st_folium(m, width="100%", height=700)
