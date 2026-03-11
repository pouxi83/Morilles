import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel Live Tracker - Tavernes", page_icon="🍄", layout="wide")

# --- 1. MOTEUR DE DONNÉES EN TEMPS RÉEL (Open-Meteo) ---
@st.cache_data(ttl=3600) # Mise à jour toutes les heures
def get_live_weather():
    try:
        # API météo pour Tavernes avec radiations solaires et pluie
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.59&longitude=6.01&daily=precipitation_sum,temperature_2m_max,shortwave_radiation_sum&timezone=Europe%2FBerlin&past_days=5"
        data = requests.get(url, timeout=5).json()
        
        # Calculs sur les 5 derniers jours
        pluie_totale = sum(data['daily']['precipitation_sum'][:5])
        temp_moyenne = sum(data['daily']['temperature_2m_max'][:5]) / 5
        soleil_total = sum(data['daily']['shortwave_radiation_sum'][:5])
        
        return pluie_totale, temp_moyenne, soleil_total
    except:
        return 15.0, 14.0, 15.0 # Valeurs de secours si pas de réseau

pluie_live, temp_live, soleil_live = get_live_weather()

# --- 2. BASE TOPOGRAPHIQUE (Les points avec Pente et Exposition) ---
# expo: 'S' (Sud/Soleil), 'N' (Nord/Ombre), 'E' (Est/Matin)
# pente: douce (<10°), moyenne (10-20°), forte (>20°)
topography_spots = [
    {"nom": "Faille de la Blanquière", "coords": [43.6062, 6.0385], "alt": 515, "expo": "N", "pente": "forte", "geologie": "Calcaire"},
    {"nom": "Marnes de Saint-Cassien", "coords": [43.5915, 5.9940], "alt": 390, "expo": "S", "pente": "douce", "geologie": "Marnes"},
    {"nom": "Replat du Petit Bessillon", "coords": [43.5855, 6.0125], "alt": 485, "expo": "E", "pente": "moyenne", "geologie": "Eboulis"},
    {"nom": "Vallon de l'Orb", "coords": [43.5842, 5.9548], "alt": 355, "expo": "N", "pente": "douce", "geologie": "Alluvions"},
    {"nom": "Plateau des Lauves", "coords": [43.6125, 6.0175], "alt": 545, "expo": "S", "pente": "douce", "geologie": "Calcaire dur"},
    {"nom": "Lisière Nord-Amphoux", "coords": [43.5970, 6.1050], "alt": 445, "expo": "E", "pente": "moyenne", "geologie": "Calcaire mixte"}
]

# --- 3. L'ALGORITHME DE PROBABILITÉ ---
def calculer_probabilite(spot, pluie, temp, soleil):
    score = 40 # Base de départ (si la géologie est bonne)
    raisons = []
    
    # Facteur 1 : Pluie et Pente (Drainage)
    if pluie > 10:
        if spot["pente"] == "forte":
            score += 10; raisons.append("Drainage parfait après la pluie")
        elif spot["pente"] == "douce":
            score += 20; raisons.append("L'eau s'est accumulée idéalement")
    else: # Si c'est sec
        if spot["pente"] == "forte":
            score -= 15; raisons.append("Pente forte : sol trop sec")
        else:
            score += 5; raisons.append("Pente douce : garde un peu d'humidité")
            
    # Facteur 2 : Ensoleillement et Exposition
    if soleil > 18: # Beaucoup de soleil récent
        if spot["expo"] == "N":
            score += 25; raisons.append("Ubac (Nord) : protégé de l'évaporation")
        elif spot["expo"] == "S":
            score -= 10; raisons.append("Adret (Sud) : risque de dessèchement")
    else: # Temps gris
        if spot["expo"] == "S":
            score += 20; raisons.append("Adret (Sud) : a profité du peu de chaleur")
            
    # Facteur 3 : Altitude vs Température
    if 10 <= temp <= 16:
        if spot["alt"] < 450:
            score += 15; raisons.append("Altitude basse idéale pour ces températures")
    elif temp > 16:
        if spot["alt"] >= 450:
            score += 15; raisons.append("La pousse monte en altitude avec la chaleur")
            
    # Borner le score entre 10 et 99%
    score = max(10, min(99, score))
    return score, raisons

# --- 4. INTERFACE UTILISATEUR ---
st.sidebar.title("📡 Télémétrie en Direct")
st.sidebar.info(f"🌧️ Pluie (5j) : **{pluie_live:.1f} mm**\n\n🌡️ Temp. moy. : **{temp_live:.1f}°C**\n\n☀️ Soleil : **{soleil_live:.1f} MJ/m²**")

st.sidebar.markdown("---")
st.sidebar.write("🟢 **Vert** : Probabilité > 75%\n\n🟠 **Orange** : Probabilité 50-75%\n\n🔴 **Rouge** : Probabilité < 50%")

# --- 5. CARTOGRAPHIE ---
st.title("🛰️ Morel Live Tracker : Analyse Topo-Météo")

m = folium.Map(location=[43.60, 6.02], zoom_start=13, tiles=None)
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='Relief').add_to(m)

# Couches BRGM et IGN
for url, layer, name in [
    ("https://data.geopf.ign.fr/wms-r/wms", "LANDCOVER.FORESTINVENTORY.V2", "Forêts (IGN)"),
    ("https://geoservices.brgm.fr/geologie", "GEOLOGIE", "Géologie (BRGM)"),
    ("https://data.geopf.ign.fr/wms-r/wms", "HYDROGRAPHY.NETWORK", "Ruisseaux (IGN)")
]:
    folium.WmsTileLayer(url=url, layers=layer, name=name, transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

# Traitement des points avec l'algorithme
for spot in topography_spots:
    proba, motifs = calculer_probabilite(spot, pluie_live, temp_live, soleil_live)
    
    # Détermination de la couleur selon le score calculé en direct
    if proba >= 75: color = "green"
    elif proba >= 50: color = "orange"
    else: color = "red"
    
    # Formatage du texte pour la bulle
    explications = "<br>".join([f"- {m}" for m in motifs])
    
    folium.Circle(
        location=spot["coords"], radius=280, color=color, fill=True, fill_opacity=0.4,
        popup=f"<b>{spot['nom']}</b><br>Score Direct : <b>{proba}%</b><br><i>Analyse de l'IA :</i><br>{explications}"
    ).add_to(m)
    
    folium.Marker(
        location=spot["coords"],
        icon=folium.Icon(color=color, icon='bolt', prefix='fa')
    ).add_to(m)

plugins.LocateControl(flyTo=True, keepCurrentZoomLevel=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

st_folium(m, use_container_width=True, height=700)
