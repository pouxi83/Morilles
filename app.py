import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium

st.set_page_config(page_title="Morel Sniper - Scan Topo", layout="wide")

st.title("🕵️‍♂️ Scanner de Relief Réel : Tavernes")
st.markdown("""
**Mode d'emploi :** 1. Active la couche **'Carte des Pentes'**. 
2. Les zones **jaunes/oranges** (pentes 10-25%) sont tes zones de 'Sale' (ravins). 
3. Les zones **blanches en altitude** sont les replats 'Propres' (Noires).
""")

# Centrage sur le massif sauvage (Le Défends / Bessillon) - On évite le village.
m = folium.Map(location=[43.6100, 6.0350], zoom_start=14, tiles=None)

# 1. Fond Image Satellite (Pour voir les vrais arbres)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='1. Vue Satellite'
).add_to(m)

# 2. La Carte des Pentes IGN (LA référence pour le chasseur)
# Elle colore le relief : Jaune = Pente douce, Orange = Pente moyenne, Violet = Falaise.
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="GEOGRAPHICALGRIDSYSTEMS.SLOPES.3D",
    name="2. Analyse des Pentes (IGN)",
    fmt="image/png",
    transparent=True,
    opacity=0.6
).add_to(m)

# 3. Réseau Hydrographique (Pour trouver le fond des ravins)
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="HYDROGRAPHY.NETWORK",
    name="3. Ruisseaux et Talwegs",
    fmt="image/png",
    transparent=True,
    opacity=0.8
).add_to(m)

# Outil GPS (Indispensable quand tu es dans la colline)
plugins.LocateControl(
    flyTo=True, 
    keepCurrentZoomLevel=True,
    strings={"title": "Ma position réelle"}
).add_to(m)

# Ajout d'une échelle pour mesurer la distance des barres rocheuses
folium.LayerControl(collapsed=False).add_to(m)

st_folium(m, use_container_width=True, height=750)
