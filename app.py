import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import requests

# Configuración de página limpia y neutral
st.set_page_config(page_title="Sistema de Cumpleaños", page_icon="📊", layout="centered")

st.title("📊 Sistema de Cumpleaños")
st.write("Control y envío de saludos para egresados desde la nube (PC o Celular).")

# Reemplaza aquí con el enlace correcto de tu Google Sheets en formato CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vS8C29gP9Aih69mX2G8N8v6f4o9fWJzG9V9a1b1c1d1/export?format=csv"

@st.cache_data(ttl=60)
def cargar_datos(url):
    return pd.read_csv(url)

try:
    df = cargar_datos(SHEET_URL)
    st.success("✅ Conexión con Google Sheets exitosa.")
    
    # Control de fecha
    fecha_actual = st.date_input("📅 Selecciona la fecha a procesar:", datetime.now().date())
    dia_mes_buscado = fecha_actual.strftime("%d/%m")
    
    # Asegurar formatos de las columnas del Excel
    df['FECHA CUMPLEAÑOS'] = df['FECHA CUMPLEAÑOS'].astype(str).str.strip()
    cumpleañeros = df[df['FECHA CUMPLEAÑOS'].str.contains(dia_mes_buscado, na=False)]
    
    st.markdown(f"### 🎂 Cumpleañeros del día {fecha_actual.strftime('%d/%m')}:")
    
    if not cumpleañeros.empty:
        for idx, fila in cumpleañeros.iterrows():
            nombre = str(fila['NOMBRES']).upper()
            carrera = str(fila['CARRERA PROFESIONAL']).upper()
            celular = str(fila['CELULAR']).replace(".0", "").strip()
            if not celular.startswith("51"):
                celular = "51" + celular
                
            col1, col2 = st.columns([1, 1.5])
            
            with col1:
                # --- GENERACIÓN DE LA TARJETA OPTIMIZADA EN ALTA RESOLUCIÓN ---
                ancho, alto = 1200, 800
                imagen = Image.new("RGB", (ancho, alto), "#F4F6F9")
                draw = ImageDraw.Draw(imagen)
                
                # Encabezado azul institucional masivo
                draw.rectangle([(0, 0), (ancho, 220)], fill="#1B365D")
                # Pie de página azul
                draw.rectangle([(0, alto - 100), (ancho, alto)], fill="#0B1D33")
                
                # Intentar usar una fuente preinstalada en Linux que soporta tildes perfectamente
                try:
                    font_titulo = ImageFont.truetype("DejaVuSans-Bold.ttf", 46)
                    font_sub = ImageFont.truetype("DejaVuSans.ttf", 28)
                    font_cuerpo = ImageFont.truetype("DejaVuSans.ttf", 32)
                    font_pie = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
                except IOError:
                    # Alternativa por si el sistema usa la por defecto
                    font_titulo = font_sub = font_cuerpo = font_pie = ImageFont.load_default()
                
                # Dibujar textos de la tarjeta con codificación limpia
                draw.text((60, 50), f"¡Feliz Cumpleaños, {nombre}!", fill="#FFFFFF", font=font_titulo)
                draw.text((60, 130), f"Egresado(a) de {carrera}", fill="#A3C1AD", font=font_sub)
                
                texto_saludo = (
                    f"Estimado(a) egresado(a),\n\n"
                    f"Hoy es un día muy especial, y desde la Unidad de Seguimiento al\n
