import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium

st.set_page_config(page_title="Morel Precision Scanner", layout="wide")

st.title("🛡️ Scanner de Précision Géologique - Tavernes")
st.markdown("""
**Arrêtons les suppositions.** Cette carte affiche les données réelles du sous-sol. 
1. Regarde les zones **bleues/violettes** : c'est le calcaire (le seul endroit où il y a des morilles).
2. Superpose avec la couche **Forêt** pour éviter les habitations.
""")

# Centrage précis sur la zone sauvage entre Tavernes et Fox-Amphoux
m = folium.Map(location=[43.5950, 6.0400], zoom_start=14, tiles=None)

# 1. Fond Relief Topo (Pour voir les pentes et les ravins)
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='1. Relief & Ravins').add_to(m)

# 2. Couche Géologique BRGM (INDISPENSABLE)
# Le calcaire Jurassique est la clé. Si c'est pas sur cette couche, y'a rien.
folium.WmsTileLayer(
    url="https://geoservices.brgm.fr/geologie",
    layers="GEOLOGIE",
    name="2. Géologie (Chercher le Bleu/Violet)",
    fmt="image/png",
    transparent=True,
    opacity=0.6
).add_to(m)

# 3. Couche Forêt IGN (Pour éviter les maisons)
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="LANDCOVER.FORESTINVENTORY.V2",
    name="3. Forêt (Éviter le blanc = maisons)",
    fmt="image/png",
    transparent=True,
    opacity=0.4
).add_to(m)

# 4. Couche Ruisseaux (Pour le 'Sale')
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="HYDROGRAPHY.NETWORK",
    name="4. Ruisseaux & Vallons",
    fmt="image/png",
    transparent=True,
    opacity=0.8
).add_to(m)

# Outil GPS pour que tu te vois avancer dans la colline
plugins.LocateControl(flyTo=True, keepCurrentZoomLevel=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

st_folium(m, use_container_width=True, height=750)
