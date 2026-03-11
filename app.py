import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import plugins

st.set_page_config(page_title="Mes Coins à Morilles - Tavernes", layout="wide")

st.title("🎯 Mes Points GPS - Commune de Tavernes")
st.write("Analyse basée sur le biotope 'Sale' (Lierre / Forêt Mixte)")

# Les points précis sur Tavernes
points = [
    {"nom": "Zone 1 - Les Lauvières (Sale)", "pos": [43.5796, 6.0312]},
    {"nom": "Zone 2 - Vallon Peirière (Humide)", "pos": [43.5938, 6.0355]},
    {"nom": "Zone 3 - Ubac Peirière (Forêt Mixte)", "pos": [43.5852, 6.0421]}
]

m = folium.Map(location=[43.585, 6.035], zoom_start=14)

# Fond Satellite pour bien voir la forêt
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satellite'
).add_to(m)

# Ajout des marqueurs
for p in points:
    folium.Marker(
        location=p["pos"],
        popup=p["nom"],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# GPS en temps réel
plugins.LocateControl(flyTo=True).add_to(m)

st_folium(m, use_container_width=True, height=600)
