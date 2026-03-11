import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium

st.set_page_config(page_title="Scan Colline Tavernes", layout="wide")

# --- LES VRAIS SECTEURS DE COLLINE (LOIN DES MAISONS) ---
# Analyse basée sur les courbes de niveau réelles au Nord de Tavernes
secteurs_sauvages = [
    {
        "nom": "Rupture de pente - La Blanquière", 
        "coords": [43.6068, 6.0365], 
        "biotope": "Sale (Vallon encaissé)", 
        "raison": "Zone d'ombre permanente, humidité bloquée au pied de la barre rocheuse."
    },
    {
        "nom": "Replat des Pins - Crête Nord", 
        "coords": [43.6125, 6.0420], 
        "biotope": "Propre (Plateau)", 
        "raison": "Zone de pins après la montée. Sol calcaire dénudé (Noires)."
    },
    {
        "nom": "Versant Nord du Grand Bessillon", 
        "coords": [43.5825, 6.0210], 
        "biotope": "Mixte (Ubac)", 
        "raison": "Pente sauvage raide. Chercher sous les chênes verts et les mousses."
    },
    {
        "nom": "Ancienne Combe (Loin lotissements)", 
        "coords": [43.5955, 5.9890], 
        "biotope": "Sale (Humus profond)", 
        "raison": "Cuvette naturelle loin de toute route. Accumulation de feuilles."
    }
]

st.title("🕵️‍♂️ Scan Colline : Secteurs Sauvages")
st.warning("⚠️ Ces points sont en pleine colline. Prévoyez de bonnes chaussures, on oublie les plaines et les maisons.")

# Carte centrée sur la zone sauvage entre Tavernes et Montmeyan
m = folium.Map(location=[43.60, 6.02], zoom_start=14)

# ON FORCE LE RELIEF IGN POUR BIEN VOIR LES PENTES
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='Topo', name='Vue Relief').add_to(m)

# Ajout des zones de scan (Cérucles de prospection)
for s in secteurs_sauvages:
    color = "darkred" if "Sale" in s["biotope"] else "blue"
    
    # On dessine la zone de recherche (250m autour du point sauvage)
    folium.Circle(
        location=s["coords"],
        radius=250,
        color=color,
        fill=True,
        fill_opacity=0.2,
        popup=f"<b>{s['nom']}</b><br>{s['raison']}"
    ).add_to(m)
    
    folium.Marker(
        location=s["coords"],
        icon=folium.Icon(color=color, icon='tree', prefix='fa'),
        popup=s["nom"]
    ).add_to(m)

plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl().add_to(m)

st_folium(m, use_container_width=True, height=700)
