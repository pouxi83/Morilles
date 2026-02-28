import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel Sniper Pro", page_icon="🍄", layout="wide")

# --- 1. RÉCUPÉRATION MÉTÉO ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.59&longitude=6.01&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        precip_7j = sum(data['daily']['precipitation_sum'][:7])
        tmax = data['daily']['temperature_2m_max'][0]
        return precip_7j, tmax
    except: return 0.0, 0.0

precip, tmax = get_weather()
is_ideal = precip >= 15 and 12 <= tmax <= 20

# --- 2. BARRE LATÉRALE : LÉGENDE ET INFOS ---
st.sidebar.title("📚 Guide de Lecture")

with st.sidebar.expander("🗺️ Légende des Couches", expanded=True):
    st.write("---")
    st.write("🔵 **Lignes Bleues :** Ruisseaux et sources (Cherchez l'humidité).")
    st.write("🟢 **Zones Vertes :** Forêts de feuillus (Frênes, Chênes).")
    st.write("🎨 **Couleurs Géologie :**")
    st.info("✅ Bleu/Vert (j, n) : CALCAIRE (90% de chance)")
    st.error("❌ Rouge/Orange : Acide/Sable (Peu de chance)")
    st.write("---")
    st.write("📍 **Marqueurs Verts :** Apparaissent uniquement si Pluie > 15mm.")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Météo Tavernes")
st.sidebar.metric("Pluie (7j)", f"{precip} mm")
if is_ideal:
    st.sidebar.success("🚀 CONDITIONS IDÉALES")
else:
    st.sidebar.warning("⏳ ATTENDRE LA PLUIE")

# --- 3. POINTS STRATÉGIQUES ---
spots = [
    {"name": "Vallon des Ferrages", "lat": 43.5982, "lon": 6.0251, "desc": "Humidité + Calcaire dur."},
    {"name": "Pied du Petit Bessillon", "lat": 43.5850, "lon": 6.0120, "desc": "Pente Sud sous les frênes."},
    {"name": "Ravin de la Blanquière", "lat": 43.6050, "lon": 6.0350, "desc": "Zone fraîche, idéal fin de saison."}
]

# --- 4. LA CARTE ---
st.title("🎯 Cartographie de Précision - Tavernes")

# Création de la carte
m = folium.Map(location=[43.5936, 6.0167], zoom_start=14, tiles=None)

# A. Fond Relief
folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='OpenTopoMap', name='1. Relief (Courbes de niveau)', active=True
).add_to(m)

# B. Couche Végétation (FEUILLUS) - Réactivée ici
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="LANDCOVER.FORESTINVENTORY.V2",
    fmt="image/png", transparent=True,
    name="2. Forêts & Feuillus (IGN)",
    overlay=True, opacity=0.5, attr="IGN"
).add_to(m)

# C. Couche Géologie (CALCAIRE)
folium.WmsTileLayer(
    url="https://geoservices.brgm.fr/geologie",
    layers="GEOLOGIE",
    fmt="image/png", transparent=True,
    name="3. Nature du Sol (BRGM)",
    overlay=True, opacity=0.5, attr="BRGM"
).add_to(m)

# D. Couche Hydro (EAU)
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="HYDROGRAPHY.NETWORK",
    fmt="image/png", transparent=True,
    name="4. Ruisseaux & Humidité",
    overlay=True, opacity=0.8, attr="IGN"
).add_to(m)

# LOGIQUE DES MARQUEURS
if is_ideal:
    for spot in spots:
        folium.Marker(
            location=[spot["lat"], spot["lon"]],
            popup=f"<b>{spot['name']}</b><br>{spot['desc']}",
            icon=folium.Icon(color='green', icon='leaf')
        ).add_to(m)
else:
    folium.Marker(
        location=[43.5936, 6.0167],
        popup="Attendez la pluie pour voir les points Sniper.",
        icon=folium.Icon(color='red', icon='time')
    ).add_to(m)

# OUTILS
plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# AFFICHAGE
st_folium(m, width="100%", height=700)
