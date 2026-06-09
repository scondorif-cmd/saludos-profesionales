import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
import io
import base64
import os
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont

# Configuración premium de la plataforma institucional
st.set_page_config(page_title="Portal Institucional UNAMAD", page_icon="🎓", layout="wide")

# Estilos CSS globales inyectados para refinar la UI de Streamlit
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1 { color: #1B365D; font-weight: 800; font-size: 2.2rem !important; margin-bottom: 0.1rem; }
    .subtitulo-app { color: #475569; font-size: 1.05rem; margin-bottom: 1.5rem; }
    .panel-metricas {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    .bloque-egresado {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .btn-whatsapp-nativo {
        display: block;
        text-align: center;
        background-color: #25D366;
        color: white !important;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 16px;
        border-radius: 10px;
        text-decoration: none;
        width: 100%;
        box-sizing: border-box;
    }
    .btn-deshabilitado {
        display: block;
        text-align: center;
        background-color: #F1F5F9;
        color: #94A3B8 !important;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 16px;
        border-radius: 10px;
        text-decoration: none;
        border: 1px solid #E2E8F0;
        width: 100%;
        box-sizing: border-box;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎓 Portal de Gestión Institucional - UNAMAD</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo-app'>Unidad de Seguimiento al Egresado y Bolsa de Trabajo</p>", unsafe_allow_html=True)

tab_cumple, tab_convocatoria = st.tabs(["🎂 Control de Cumpleaños", "📰 Imagen de Boletín de Convocatorias"])

DB_LOG_FILE = "registro_envios_ax.csv"

def cargar_log_permanente():
    if os.path.exists(DB_LOG_FILE):
        return set(pd.read_csv(DB_LOG_FILE)["id_unico"].tolist())
    return set()

def guardar_log_permanente(id_unico):
    saludados = cargar_log_permanente()
    saludados.add(id_unico)
    pd.DataFrame({"id_unico": list(saludados)}).to_csv(DB_LOG_FILE, index=False)

def obtener_jaguar_base64():
    nombre_archivo = "cumpleanos.png"
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded_string}"
    return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='110' height='110'><rect width='110' height='110' fill='%23cccccc'/></svg>"

jaguar_src = obtener_jaguar_base64()

if "egresados_saludados" not in st.session_state:
    st.session_state.egresados_saludados = cargar_log_permanente()

# ==========================================
# PESTAÑA 1: SISTEMA DE CUMPLEAÑOS
# ==========================================
with tab_cumple:
    col_control1, _ = st.columns([1, 2])
    with col_control1:
        fecha_seleccionada = st.date_input("📅 Fecha de procesamiento:", datetime.now(), key="fecha_cumple_tab")
        dia_buscado = fecha_seleccionada.strftime("%d/%m")

    url_google_sheets = "https://docs.google.com/spreadsheets/d/1ScZqatCGsyBUAOQBTdwkTxfOoZNlRfuTD5bhy_iRCao/edit?usp=sharing"

    def descargar_datos():
        url_descarga = url_google_sheets.split('/edit')[0] + '/export?format=xlsx' if "edit" in url_google_sheets else url_google_sheets
        resp = requests.get(url_descarga)
        return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

    def generar_tarjeta_html(nombre, carrera, index, jaguar_src, titulo_egresado, saludo_inicial, colores):
        return f"""
        <!DOCTYPE html>
        <html lang="es"><head><meta charset="UTF-8"><script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            html, body {{ margin: 0; padding: 0; background-color: #FFFFFF; font-family: 'Segoe UI', Arial, sans-serif; }}
            .tarjeta-contenedor {{ background-color: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.08); overflow: hidden; max-width: 440px; margin: 0 auto; border: 1px solid #E2E8F0; }}
            .banner-superior {{ background: {colores['banner']}; padding: 22px 16px; text-align: center; color: white; }}
            .banner-superior h2 {{ margin: 0; font-size: 19px;
