import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Morel Hunter Pro - Tavernes",
    page_icon="🍄",
    layout="wide"
)

# --- FONCTIONS TECHNIQUES (MÉTÉO & ALTITUDE) ---
def get_weather():
    try:
        # Coordonnées Tavernes (Var)
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.59&longitude=6.01&daily=precipitation_sum,temperature_2m_max,temperature_2m_min&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        precip_7j = sum(data['daily']['precipitation_sum'][:7])
        tmax = data['daily']['temperature_2m_max'][0]
        tmin = data['daily']['temperature_2m_min'][0]
        return precip_7j, tmax, tmin
    except:
        return 0.0, 0.0, 0.0

def get_ideal_altitude():
    day_of_year = datetime.now().timetuple().tm_yday
    # Saison commence jour 60 (1er mars) à 300m, monte de 8m/jour
    if day_of_year < 60: return 300
    alt = 300 + ((day_of_year - 60) * 8)
    return min(int(alt), 1000)

# --- PRÉPARATION DES DONNÉES ---
precip, tmax, tmin = get_weather()
ideal_alt = get_ideal_altitude()

# --- BARRE LATÉRALE (DASHBOARD) ---
st.sidebar.title("🌲 Tableau de Bord")
st.sidebar.metric("Altitude Idéale", f"{ideal_alt} m")

with st.sidebar.expander("🌤️ Météo (Tavernes)", expanded=True):
    st.write(f"Pluie 7j : **{precip} mm**")
    st.write(f"Amplitude T° : **{tmax-tmin:.1f} °C**")

if precip > 15 and 10 < tmax < 19:
    st.sidebar.success("🚀 PROBABILITÉ ÉLEVÉE")
else:
    st.sidebar.warning("⏳ CONDITIONS MOYENNES")

# --- CARTE INTERACTIVE ---
st.title("🍄 Morel Hunter : Secteur Tavernes")

tab1, tab2 = st.tabs(["🗺️ Carte de Prospection", "📖 Guide Terrain"])

with tab1:
    # Initialisation de la carte
    m = folium.Map(location=[43.5936, 6.0167], zoom_start=14, tiles=None)

    # 1. Fond de carte Relief (OpenTopoMap)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='OpenTopoMap',
        name='Relief & Vallons'
    ).add_to(m)

    # 2. Couche Géologique BRGM (Le Calcaire)
    folium.WmsTileLayer(
        url="https://geoservices.brgm.fr/geologie",
        layers="GEOLOGIE",
        fmt="image/png",
        transparent=True,
        name="Géologie (Zones Calcaires)",
        overlay=True,
        opacity=0.5
    ).add_to(m)

    # 3. Couche Végétation (Nouvelle Géoplateforme IGN)
    folium.WmsTileLayer(
        url="https://data.geopf.ign.fr/wms-r/wms",
        layers="LANDCOVER.FORESTINVENTORY.V2",
        fmt="image/png",
        transparent=True,
        name="Végétation (Chercher Feuillus)",
        overlay=True,
        opacity=0.4,
        attr="IGN - BD Forêt"
    ).add_to(m)

    # OUTILS GPS ET CONTRÔLE
    plugins.LocateControl(flyTo=True, keepCurrentZoomLevel=True).add_to(m)
    plugins.Fullscreen().add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    # Affichage de la carte
    st_folium(m, width="100%", height=600)

with tab2:
    st.subheader("💡 Conseils pour Tavernes")
    st.markdown("""
    - **Géologie :** Les morilles adorent les sols calcaires. Sur la carte, cherchez les zones de couleur **bleu clair ou vert pomme**.
    - **Végétation :** Activez la couche 'Végétation' et visez les zones de feuillus (souvent en vert plus sombre ou marron) près des ruisseaux.
    - **Le Choc :** Si vous voyez une pluie > 15mm suivie d'un après-midi à 16°C, les morilles sortiront 3 à 5 jours après.
    """)

st.sidebar.markdown("---")
if st.sidebar.button("🚨 SOS : Partager ma position"):
    st.sidebar.code("Je suis en prospection à Tavernes. Position centre carte : 43.59, 6.01")
