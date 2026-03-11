import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium

st.set_page_config(page_title="Morel Commando - Haut Var", layout="wide")

# --- NOUVEAUX POINTS : LES REPLATS DE CRÊTE (PROPRES) ---
# On vise les zones "en balcon" au-dessus de Tavernes
commando_spots = [
    {"nom": "Replat du Haut-Bessillon", "coords": [43.5785, 6.0120], "alt": 610, "type": "Dalle calcaire / Mousse"},
    {"nom": "Crête de la Sainte-Baume (Nord Tavernes)", "coords": [43.6180, 6.0350], "alt": 580, "type": "Pins clairsemés"},
    {"nom": "Le Signal (Plateau supérieur)", "coords": [43.6020, 6.0650], "alt": 540, "type": "Sol rocailleux propre"},
    {"nom": "Balcon de l'Eure", "coords": [43.5910, 5.9750], "alt": 520, "type": "Lisière chênes verts"}
]

st.title("🦅 Morel Commando : Stratégie des Crêtes")
st.info("Oublie les vallons humides. On cherche les 'points chauds' d'altitude où le sol est propre et calcaire.")

m = folium.Map(location=[43.60, 6.02], zoom_start=13)

# Couche Relief obligatoire pour comprendre
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='Topo', name='Relief').add_to(m)

for spot in commando_spots:
    folium.Marker(
        location=spot["coords"],
        popup=f"<b>{spot['nom']}</b><br>Alt: {spot['alt']}m<br>Terrain: {spot['type']}",
        icon=folium.Icon(color='black', icon='location-arrow', prefix='fa')
    ).add_to(m)

# Outils de précision
plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl().add_to(m)

st_folium(m, use_container_width=True, height=650)
