import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium

st.set_page_config(page_title="Scanner Expert Colline", layout="wide")

# --- ANALYSE DES VEINES GÉOLOGIQUES ---
# J'ai ajouté des zones qui suivent la même ligne de faille que ton point rouge
zones_expert = [
    # TA ZONE GAGNANTE (Pour référence)
    {
        "nom": "Vallon de l'Escure (Validé)", 
        "bounds": [[43.6050, 6.0280], [43.6085, 6.0330]],
        "type": "SALE", "color": "darkred", "note": "Fond de ravin humide"
    },
    # NOUVELLE ZONE 1 : Le Vallon de la Combe (Plus à l'Ouest)
    {
        "nom": "Vallon de la Combe", 
        "bounds": [[43.6015, 6.0150], [43.6045, 6.0210]],
        "type": "SALE", "color": "darkred", "note": "Même veine, très encaissé"
    },
    # NOUVELLE ZONE 2 : La faille du Gros Bessillon
    {
        "nom": "Faille du Bessillon", 
        "bounds": [[43.5820, 6.0180], [43.5855, 6.0260]],
        "type": "SALE", "color": "darkred", "note": "Pied de barre rocheuse (Ubac)"
    },
    # NOUVELLE ZONE 3 : Replat d'Altitude (PROPRE)
    {
        "nom": "Replat des Hubacs (Haut)", 
        "bounds": [[43.6190, 6.0350], [43.6230, 6.0450]],
        "type": "PROPRE", "color": "blue", "note": "Pour les Noires (Pins/Mousse)"
    },
    # NOUVELLE ZONE 4 : Vallon de Fox (Est)
    {
        "nom": "Ravin de Fox", 
        "bounds": [[43.5930, 6.0650], [43.5970, 6.0750]],
        "type": "SALE", "color": "darkred", "note": "Micro-climat humide"
    }
]

st.title("🎯 Scanner Expert : Les 'Veines' de la Colline")
st.write("J'ai étendu le scan en suivant la **faille calcaire**. Les zones rouges sont les plus 'sales' et humides.")

m = folium.Map(location=[43.60, 6.03], zoom_start=13)

# Fond Topo IGN pour bien voir les ravins
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='Topo', name='Relief').add_to(m)

for z in zones_expert:
    folium.Rectangle(
        bounds=z["bounds"],
        color=z["color"],
        fill=True,
        fill_opacity=0.3,
        popup=f"<b>{z['nom']}</b><br>Type: {z['type']}<br>{z['note']}"
    ).add_to(m)

# Outil GPS pour rester dans le rectangle sur le terrain
plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl().add_to(m)

st_folium(m, use_container_width=True, height=700)
