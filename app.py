import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel AI - Tavernes", page_icon="🍄", layout="wide")

# --- 1. RÉCUPÉRATION MÉTÉO ---
def get_weather():
    try:
        # Coordonnées Tavernes
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.59&longitude=6.01&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        precip_7j = sum(data['daily']['precipitation_sum'][:7])
        tmax = data['daily']['temperature_2m_max'][0]
        return precip_7j, tmax
    except:
        return 0.0, 0.0

precip, tmax = get_weather()

# --- 2. CALCUL DE LA PROBABILITÉ (LOGIQUE 90%) ---
# La morille sort si : il a plu (>15mm) et qu'il fait doux (12-20°C)
is_ideal = precip >= 15 and 12 <= tmax <= 20

# --- 3. BARRE LATÉRALE (INDICATEURS) ---
st.sidebar.title("📊 Analyse en temps réel")
st.sidebar.metric("Pluie (7 derniers jours)", f"{precip} mm")
st.sidebar.metric("Température Max", f"{tmax} °C")

st.sidebar.markdown("---")
if is_ideal:
    st.sidebar.success("🚀 CONDITIONS IDÉALES (90%) : Les spots sont visibles sur la carte !")
    chance_score = 90
else:
    st.sidebar.warning("⏳ ATTENDRE LA PLUIE : Le sol est trop sec. Spots masqués.")
    chance_score = 30

# --- 4. LISTE DES SPOTS STRATÉGIQUES (Tavernes) ---
# Ces points n'apparaissent que si is_ideal est vrai
spots = [
    {"name": "Vallon des Ferrages (Humide)", "lat": 43.5982, "lon": 6.0251, "desc": "Fond de thalweg, zone calcaire j2."},
    {"name": "Pied du Petit Bessillon", "lat": 43.5850, "lon": 6.0120, "desc": "Adret calcaire sous les frênes."},
    {"name": "Ravin de la Blanquière", "lat": 43.6050, "lon": 6.0350, "desc": "Zone très ombragée, idéal fin de saison."},
    {"name": "Source de l'Argens (Secteur)", "lat": 43.5910, "lon": 5.9980, "desc": "Proximité eau + calcaire dur."}
]

# --- 5. CARTE ---
st.title("🍄 Morel AI : Cartographie Prédictive")

m = folium.Map(location=[43.5936, 6.0167], zoom_start=14, tiles=None)

# Couches de base
folium.TileLayer(tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='Relief').add_to(m)

# Couche GÉOLOGIE (BRGM)
folium.WmsTileLayer(
    url="https://geoservices.brgm.fr/geologie",
    layers="GEOLOGIE", fmt="image/png", transparent=True,
    name="Géologie (Bleu = Calcaire)", overlay=True, opacity=0.5
).add_to(m)

# Couche HYDRO (Réseau d'eau)
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="HYDROGRAPHY.NETWORK", fmt="image/png", transparent=True,
    name="Ruisseaux (Humidité)", overlay=True, opacity=0.7
).add_to(m)

# LOGIQUE D'AFFICHAGE DES MARQUEURS
if is_ideal:
    for spot in spots:
        folium.Marker(
            location=[spot["lat"], spot["lon"]],
            popup=f"<b>{spot['name']}</b><br>{spot['desc']}",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
else:
    # On met un seul marqueur informatif si les conditions ne sont pas réunies
    folium.Marker(
        location=[43.5936, 6.0167],
        popup="Revenez après la pluie pour voir les points chauds.",
        icon=folium.Icon(color='red', icon='time')
    ).add_to(m)

# Outils
plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# Affichage
st_folium(m, width="100%", height=700)

st.info("💡 Note : Les marqueurs 'Sniper' ne s'activent que lorsque le cumul de pluie dépasse 15mm sur 7 jours.")
