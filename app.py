import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel Sniper - Tavernes", page_icon="🎯", layout="wide")

# --- FONCTIONS MÉTÉO ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.59&longitude=6.01&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        return sum(data['daily']['precipitation_sum'][:7]), data['daily']['temperature_2m_max'][0]
    except: return 0.0, 0.0

precip, tmax = get_weather()

# --- INTERFACE ---
st.title("🎯 Morel Sniper : Tavernes & Alentours")
st.sidebar.title("🔍 Filtres Experts")

# Aide à la lecture géologique
with st.sidebar.expander("💎 Guide des Roches", expanded=True):
    st.write("**Cherchez ces codes sur la carte :**")
    st.info("✅ **j2, j3, j4** : Calcaires Jurassique (Le TOP)")
    st.info("✅ **n1, n2** : Crétacé inférieur (Très bon)")
    st.error("❌ **m, p** : Argiles/Sables (Mauvais)")

# --- CARTE DE HAUTE PRÉCISION ---
m = folium.Map(location=[43.5936, 6.0167], zoom_start=14, tiles=None)

# 1. FOND DE CARTE RELIEF (Indispensable pour voir les vallons)
folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='OpenTopoMap', name='1. Relief & Courbes de niveau'
).add_to(m)

# 2. COUCHE HYDROGRAPHIE (Ruisseaux et Sources)
# C'est ici que l'humidité se concentre
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="HYDROGRAPHY.NETWORK",
    fmt="image/png", transparent=True,
    name="2. Rivières & Ruisseaux (L'Humidité)",
    overlay=True, opacity=0.8, attr="IGN"
).add_to(m)

# 3. COUCHE GÉOLOGIE (BRGM)
folium.WmsTileLayer(
    url="https://geoservices.brgm.fr/geologie",
    layers="GEOLOGIE",
    fmt="image/png", transparent=True,
    name="3. Nature du Sol (Chercher Bleu/Vert)",
    overlay=True, opacity=0.5, attr="BRGM"
).add_to(m)

# 4. COUCHE VÉGÉTATION DÉTAILLÉE
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="LANDCOVER.FORESTINVENTORY.V2",
    fmt="image/png", transparent=True,
    name="4. Forêts (Chercher Feuillus)",
    overlay=True, opacity=0.4, attr="IGN"
).add_to(m)

# --- AJOUT DE POINTS STRATÉGIQUES (EXEMPLES) ---
# Vous pouvez ajouter vos propres points ici
folium.Marker(
    [43.598, 6.025], 
    popup="Vallon Humide + Calcaire (Zone à fort potentiel)",
    icon=folium.Icon(color='green', icon='leaf')
).add_to(m)

# --- OUTILS SUPPLÉMENTAIRES ---
plugins.LocateControl(flyTo=True).add_to(m)
plugins.Fullscreen().add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# Affichage
st_folium(m, width="100%", height=700)

# --- CONSEILS DE CHASSE ---
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.subheader("📍 Où regarder précisément ?")
    st.write("""
    1. **Les Talus :** Souvent la terre est remuée, les morilles adorent ça.
    2. **Les zones de brûlis :** Si un feu a eu lieu il y a 1 ou 2 ans, c'est le jackpot.
    3. **Sous les Frênes :** Arbre n°1 à Tavernes pour la morille. Reconnaissable à ses bourgeons noirs.
    """)
with col2:
    st.subheader("🌡️ Le Timing")
    if tmax > 15:
        st.success(f"Il fait {tmax}°C. Si le sol est humide, les morilles poussent en ce moment !")
    else:
        st.info("Encore un peu frais. Attendez une journée ensoleillée après la pluie.")
