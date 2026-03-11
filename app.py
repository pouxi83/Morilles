import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests

st.set_page_config(page_title="Morel Oracle - Full Spectrum", layout="wide")

# --- ANALYSE MÉTÉO ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.59&longitude=6.01&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin&past_days=5"
        data = requests.get(url).json()
        return sum(data['daily']['precipitation_sum']), data['daily']['temperature_2m_max'][-1]
    except: return 12.0, 16.0

pluie, tmax = get_weather()

# --- BASE DE DONNÉES BIOTOPES ---
spots = [
    # LE "PROPRE" (Noires, Plateaux, Pins, Chaussures sèches)
    {"nom": "Plateau du Signal", "coords": [43.6025, 6.0660], "alt": 545, "style": "PROPRE", "desc": "Pins/Mousses. Viser les zones dénudées.", "icon": "star", "color": "blue"},
    {"nom": "Crêtes du Bessillon", "coords": [43.5780, 6.0150], "alt": 620, "style": "PROPRE", "desc": "Dalles calcaires. Très propre.", "icon": "star", "color": "blue"},
    
    # LE "SALE" (Blondes/Noires, Vallons, Frênes, Humus gras)
    {"nom": "Ravin des Brandes", "coords": [43.5965, 6.0280], "alt": 410, "style": "SALE", "desc": "Terre noire/Lierre. Très humide et collant.", "icon": "tint", "color": "darkred"},
    {"nom": "Bords de l'Orb (Bas)", "coords": [43.5840, 5.9540], "alt": 350, "style": "SALE", "desc": "Frênes et ronces. Terre très grasse.", "icon": "tint", "color": "darkred"}
]

st.title("🍄 Oracle Intégral : Propre vs Sale")
st.markdown(f"**Conditions :** Pluie récente {pluie}mm. *La pluie favorise le 'Sale', le soleil favorise le 'Propre'.*")

m = folium.Map(location=[43.60, 6.01], zoom_start=13)
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='Topo', name='Relief').add_to(m)

# Ajout des couches Géologie et Forêt
for u, l, n in [("https://geoservices.brgm.fr/geologie", "GEOLOGIE", "Géologie"), ("https://data.geopf.ign.fr/wms-r/wms", "LANDCOVER.FORESTINVENTORY.V2", "Forêt")]:
    folium.WmsTileLayer(url=u, layers=l, name=n, transparent=True, fmt="image/png", opacity=0.3).add_to(m)

for s in spots:
    folium.Marker(
        location=s["coords"],
        popup=f"<b>{s['nom']}</b> ({s['style']})<br>{s['desc']}",
        icon=folium.Icon(color=s["color"], icon=s["icon"])
    ).add_to(m)

plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl().add_to(m)

st_folium(m, use_container_width=True, height=650)
