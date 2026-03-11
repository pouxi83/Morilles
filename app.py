import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium

st.set_page_config(page_title="Morel Oracle - Full Wild", layout="wide")

# --- LES NOUVELLES ZONES OPTIMALES (HORS HABITATIONS) ---
zones_sauvages = [
    {
        "nom": "L'Enclos des Chèvres (Nord-Est)", 
        "bounds": [[43.6180, 6.0550], [43.6220, 6.0650]],
        "type": "MIXTE", "color": "darkgreen", 
        "raison": "Zone de transition plateau/vallon. Très sauvage, loin des sentiers battus."
    },
    {
        "nom": "Ravin de la Peirière (Thalweg profond)", 
        "bounds": [[43.6110, 6.0120], [43.6150, 6.0180]],
        "type": "SALE", "color": "darkred", 
        "raison": "Encaissement maximal. L'humidité y reste bloquée même en plein soleil."
    },
    {
        "nom": "Ubac du Grand Bessillon (Crêtes)", 
        "bounds": [[43.5410, 6.0720], [43.5450, 6.0820]],
        "type": "PROPRE", "color": "blue", 
        "raison": "Altitude élevée (700m+). Pour les morilles noires tardives sous les pins."
    },
    {
        "nom": "Combe de l'Eouvière", 
        "bounds": [[43.6250, 6.0280], [43.6300, 6.0350]],
        "type": "SALE", "color": "darkred", 
        "raison": "Zone de 'terre grasse' avec bois mort en décomposition. Très prometteur."
    }
]

st.title("🎯 Scanner Haute Précision : Secteurs de Colline Vierge")
st.write("Ce scan cible uniquement les zones de rupture de pente situées à plus de 500m des premières maisons.")

m = folium.Map(location=[43.60, 6.04], zoom_start=13)

# Fond Relief Topographique
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='Topo', name='Relief').add_to(m)

for z in zones_sauvages:
    folium.Rectangle(
        bounds=z["bounds"],
        color=z["color"],
        fill=True,
        fill_opacity=0.3,
        popup=f"<b>{z['nom']}</b><br>Altitude & Type: {z['type']}<br>{z['raison']}"
    ).add_to(m)

# Outil de localisation GPS
plugins.LocateControl(flyTo=True, keepCurrentZoomLevel=True).add_to(m)
folium.LayerControl().add_to(m)

st_folium(m, use_container_width=True, height=700)
