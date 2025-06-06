import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    html, body, .main {
        height: 100%;
        margin: 0;
        padding: 0;
    }
    .block-container {
        padding: 0rem 1rem;
    }
    .folium-map {
        height: 100vh !important;
    }
    </style>
""", unsafe_allow_html=True)

df = pd.read_csv("dataset/dados_terrorismo_limpo.csv")

ataques_unicos = sorted(df['attacktype1_txt'].dropna().unique())

cores_disponiveis = [
    'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightblue', 'darkgreen', 'cadetblue'
]

cores_ataques = {
    nome: cores_disponiveis[i % len(cores_disponiveis)] for i, nome in enumerate(ataques_unicos)
}

with st.sidebar:
    st.title("🎯 Filtros")

    min_year = int(df["iyear"].min())
    max_year = int(df["iyear"].max())
    year_range = st.slider("Ano", min_year, max_year, (2010, 2020))

    paises = sorted(df['country_txt'].unique())
    pais = st.selectbox("País", ["Todos"] + paises)

    legenda_tipos = ""
    for tipo, cor in cores_ataques.items():
        legenda_tipos += f'<span style="background:{cor};display:inline-block;width:15px;height:15px;margin-right:8px;border-radius:3px;"></span>{tipo}<br>'

    st.markdown("### Tipos de ataque e suas cores")
    st.markdown(legenda_tipos, unsafe_allow_html=True)

    tipos = st.multiselect("Tipos de ataque", ataques_unicos, default=ataques_unicos)

    limite = st.number_input("Máximo de atentados no mapa", min_value=100, max_value=10000, value=2000, step=100)

df = df[(df['iyear'] >= year_range[0]) & (df['iyear'] <= year_range[1])]
if pais != "Todos":
    df = df[df['country_txt'] == pais]
df = df[df['attacktype1_txt'].isin(tipos)]
df = df.dropna(subset=['latitude', 'longitude']).head(limite)

st.markdown(f"### Total de atentados exibidos no mapa: `{len(df)}`")

m = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles="CartoDB dark_matter"
)
for _, row in df.iterrows():
    cor = cores_ataques.get(row['attacktype1_txt'], 'gray')
    popup = folium.Popup(f"""
        <b>País:</b> {row['country_txt']}<br>
        <b>Ano:</b> {row['iyear']}<br>
        <b>Tipo:</b> {row['attacktype1_txt']}<br>
        <b>Mortos:</b> {int(row['nkill']) if pd.notna(row['nkill']) else 'Desconhecido'}<br>
        <b>Sucesso:</b> {'Sim' if row['success'] == 1 else 'Não'}
    """, max_width=300)

    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=cor,
        fill=True,
        fill_color=cor,
        fill_opacity=0.7,
        popup=popup
    ).add_to(m)

st_folium(m, use_container_width=True, height=800)
