import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests

st.set_page_config(page_title="Black Morel Tracker", page_icon="🍄", layout="wide")

# --- ANALYSE MÉTÉO (Temps réel) ---
@st.cache_data(ttl=3600)
def get_weather():
    # Coordonnées centrées sur les hauteurs de Tavernes / Montmeyan
    url = "https://api.open-meteo.com/v1/forecast?latitude=43.61&longitude=6.05&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin&past_days=3"
    data = requests.get(url).json()
    return sum(data['daily']['precipitation_sum']), data['daily']['temperature_2m_max'][-1]

pluie_3j, temp_max = get_weather()

# --- LES SPOTS "PROPRES" (Ciblés Noires) ---
# On cherche des plateaux calcaires avec pins
black_spots = [
    {"nom": "Plateau de la Grande Colle", "coords": [43.6150, 6.0450], "alt": 560, "expo": "SE", "sol": "Calcaire/Pins", "pente": 8},
    {"nom": "Crêtes de Barjols (Haut)", "coords": [43.5820, 6.0080], "alt": 480, "expo": "E", "sol": "Mousse/Chênes rases", "pente": 5},
    {"nom": "Replat des Hubacs", "coords": [43.6230, 6.0620], "alt": 590, "expo": "E", "sol": "Pins sylvestres", "pente": 12},
    {"nom": "Versant des Adrets (Lisière)", "coords": [43.5950, 6.0310], "alt": 420, "expo": "SE", "sol": "Aiguilles de pins", "pente": 15}
]

def calcul_proba_noire(spot, pluie, temp):
    score = 50
    # La noire aime l'altitude en ce moment (mars)
    if spot["alt"] > 450: score += 20
    
    # L'exposition Est/SE est capitale pour le réveil du matin
    if spot["expo"] in ["E", "SE"]: score += 15
    
    # Si pluie récente < 5mm, elle préfère les pentes un peu plus fortes (10-15%)
    if pluie < 5 and spot["pente"] > 10: score += 10
    
    # Température idéale pour la noire (entre 12 et 16 degrés)
    if 12 <= temp <= 17: score += 10
    
    return min(score, 98)

# --- CARTE ---
st.title("🍄 Oracle Noire : Cible 'Chaussures Propres'")
st.markdown(f"**Analyse actuelle :** Pluie {pluie_3j}mm | Temp. Max {temp_max}°C. Focus : *Replats d'altitude & Exposition Est.*")

m = folium.Map(location=[43.60, 6.03], zoom_start=13, tiles='OpenStreetMap')

# Ajout de la couche Relief IGN pour voir les plateaux
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='Topo', name='Relief').add_to(m)

for spot in black_spots:
    proba = calcul_proba_noire(spot, pluie_3j, temp_max)
    
    # Couleur selon probabilité
    color = 'green' if proba > 75 else 'orange' if proba > 50 else 'red'
    
    folium.Marker(
        location=spot["coords"],
        popup=f"<b>{spot['nom']}</b><br>Proba Noires: {proba}%<br>Type: {spot['sol']}",
        icon=folium.Icon(color=color, icon='eye')
    ).add_to(m)

st_folium(m, use_container_width=True)
