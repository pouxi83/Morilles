import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel Intelligence - Haut-Var", layout="wide")

# --- 1. GESTION DES POINTS TROUVÉS (SESSION) ---
if 'my_spots' not in st.session_state:
    st.session_state['my_spots'] = []

# --- 2. INTERFACE LATÉRALE ---
st.sidebar.title("📒 Mon Journal de Chasse")
st.sidebar.write("Cliquez sur la carte pour enregistrer une trouvaille.")

if st.session_state['my_spots']:
    for i, spot in enumerate(st.session_state['my_spots']):
        st.sidebar.success(f"Trouvée n°{i+1}: {spot['lat']:.4f}, {spot['lon']:.4f}")
    
    if st.sidebar.button("🗑️ Effacer les points locaux"):
        st.session_state['my_spots'] = []
        st.rerun()

# --- 3. CONFIGURATION CARTE & COUCHES ---
m = folium.Map(location=[43.60, 6.05], zoom_start=12, tiles=None)
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='Relief').add_to(m)

# Couches SIG (Géo, Forêt, Eau)
for layer in [
    {"url": "https://data.geopf.ign.fr/wms-r/wms", "lay": "LANDCOVER.FORESTINVENTORY.V2", "name": "Végétation"},
    {"url": "https://geoservices.brgm.fr/geologie", "lay": "GEOLOGIE", "name": "Géologie"},
    {"url": "https://data.geopf.ign.fr/wms-r/wms", "lay": "HYDROGRAPHY.NETWORK", "name": "Ruisseaux"}
]:
    folium.WmsTileLayer(url=layer["url"], layers=layer["lay"], name=layer["name"], 
                        transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

# AFFICHER VOS TROUVAILLES (Points Or)
for spot in st.session_state['my_spots']:
    folium.Marker(
        location=[spot['lat'], spot['lon']],
        icon=folium.Icon(color='orange', icon='star'),
        popup="MA TROUVAILLE"
    ).add_to(m)

# --- 4. GESTION DU CLIC ---
m.add_child(folium.LatLngPopup()) # Affiche les coordonnées au clic
plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

st.title("🍄 Morel Intelligence - Haut-Var")
st.info("💡 **Mode d'emploi** : Cliquez sur la carte là où vous avez trouvé des morilles. Notez les coordonnées qui s'affichent et envoyez-les moi pour que j'affine les zones rouges !")

# Affichage et capture du clic
output = st_folium(m, width="100%", height=600)

# Enregistrement du clic dans la session
if output.get("last_clicked"):
    clicked = output["last_clicked"]
    # Éviter les doublons
    if clicked not in [s for s in st.session_state['my_spots']]:
        st.session_state['my_spots'].append({"lat": clicked["lat"], "lon": clicked["lng"]})
        st.rerun()
