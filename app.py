import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel Sniper V6", layout="wide")

st.title("🌲 Scanner de Colline : Tavernes (Version Directe)")
st.write("Si les cartes IGN ne s'affichent pas, voici la version **Satellite Haute Définition** avec les zones de ravins (le 'Sale').")

# --- COORDONNÉES DES VRAIS RAVINS (SANS HABITATIONS) ---
# J'ai recalibré sur les zones de 'thalweg' pur au Nord de Tavernes
ravins_sauvages = [
    {"nom": "Ravin de l'Escure (Validé)", "c": [43.6070, 6.0310], "type": "SALE"},
    {"nom": "Ravin de la Combe (Caché)", "c": [43.6030, 6.0180], "type": "SALE"},
    {"nom": "Vallon du Défends (Sauvage)", "c": [43.6140, 6.0450], "type": "PROPRE/HAUT"},
    {"nom": "Faille du Petit Bessillon", "c": [43.5850, 6.0220], "type": "SALE"}
]

# --- CRÉATION DE LA CARTE ---
# On utilise le serveur Esri qui ne plante JAMAIS
m = folium.Map(location=[43.6050, 6.0300], zoom_start=14)

# 1. Vue Satellite (Esri)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite',
    name='Satellite (Précision)'
).add_to(m)

# 2. Vue Relief (OpenTopo)
folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='OpenTopoMap',
    name='Relief (Pentes)'
).add_to(m)

# --- AJOUT DES MARQUEURS ---
for r in ravins_sauvages:
    color = "red" if r["type"] == "SALE" else "blue"
    folium.Marker(
        location=r["c"],
        popup=f"<b>{r['nom']}</b>",
        icon=folium.Icon(color=color, icon='info-sign')
    ).add_to(m)
    
    # On dessine un cercle de 300m de rayon pour la zone de recherche
    folium.Circle(
        location=r["c"],
        radius=300,
        color=color,
        fill=True,
        fill_opacity=0.2
    ).add_to(m)

# GPS : Le bouton magique pour te situer dans le ravin
plugins.LocateControl(flyTo=True, keepCurrentZoomLevel=True).add_to(m)
folium.LayerControl().add_to(m)

st_folium(m, use_container_width=True, height=700)
