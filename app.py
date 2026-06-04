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
                # --- GENERACIÓN DE LA TARJETA EN ALTA RESOLUCIÓN ---
                ancho, alto = 1200, 800
                imagen = Image.new("RGB", (ancho, alto), "#F4F6F9")
                draw = ImageDraw.Draw(imagen)
                
                # Encabezado azul institucional masivo
                draw.rectangle([(0, 0), (ancho, 220)], fill="#1B365D")
                # Pie de página azul
                draw.rectangle([(0, alto - 100), (ancho, alto)], fill="#0B1D33")
                
                # Cargar fuentes (usando las por defecto si no hay archivos .ttf)
                try:
                    font_titulo = ImageFont.truetype("arialbd.ttf", 46)
                    font_sub = ImageFont.truetype("arial.ttf", 28)
                    font_cuerpo = ImageFont.truetype("arial.ttf", 32)
                    font_pie = ImageFont.truetype("arialbd.ttf", 22)
                except IOError:
                    font_titulo = font_sub = font_cuerpo = font_pie = ImageFont.load_default()
                
                # Dibujar textos de la tarjeta con codificación UTF-8
                draw.text((60, 50), f"¡Feliz Cumpleaños, {nombre}!", fill="#FFFFFF", font=font_titulo)
                draw.text((60, 130), f"Egresado(a) de {carrera}", fill="#A3C1AD", font=font_sub)
                
                # --- AQUÍ ESTABA EL ERROR: HEMOS CERRADO LA COMILLA ---
                texto_saludo = (
                    f"Estimado(a) egresado(a),\n\n"
                    f"Hoy es un día muy especial, y desde la Unidad de Seguimiento al\n"
                    f"Egresado y Bolsa de Trabajo queremos hacerte llegar nuestras más\n"
                    f"sinceras felicitaciones por tu cumpleaños.\n\n"
                    f"Nos sentimos muy orgullosos de tus pasos. Deseamos que pases un\n"
                    f"día extraordinario junto a tus seres queridos.\n\n"
                    f"¡Que disfrutes mucho de tu día!"
                )
                draw.text((60, 270), texto_saludo, fill="#2C3E50", font=font_cuerpo, spacing=12)
                
                draw.text((60, alto - 75), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", font=font_pie)
                draw.text((60, alto - 45), "Universidad Nacional Amazónica de Madre de Dios", fill="#A3C1AD", font=font_pie)
                
                # Convertir imagen para descarga instantánea
                buf = io.BytesIO()
                imagen.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.image(imagen, caption=f"Tarjeta de {nombre}", use_container_width=True)
                st.download_button(label="💾 Guardar Imagen", data=byte_im, file_name=f"Tarjeta_{nombre}.png", mime="image/png", key=f"btn_{idx}")
                
            with col2:
                st.markdown(f"## 🥳 {nombre}")
                st.caption(f"🎓 {carrera}")
                
                texto_whatsapp = (
                    f"✨ *¡HOY CELEBRAMOS SU CUMPLEAÑOS!* 🎂🎉\n\n"
                    f"Desde la *Unidad de Seguimiento al Egresado UNAMAD*, enviamos un afectuoso "
                    f"saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n"
                    f"👤 *{nombre}*\n"
                    f"🎓 {carrera}\n\n"
                    f"¡Muchas felicidades y que tenga un excelente día! 🌟🎈"
                )
                
                st.info(texto_whatsapp)
                st.text_input("Número destino:", value=celular, key=f"num_{idx}")
                
                # Enlace de envío directo
                texto_encoded = requests.utils.quote(texto_whatsapp)
                link_ws = f"https://api.whatsapp.com/send?phone={celular}&text={texto_encoded}"
                st.markdown(f'<a href="{link_ws}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            
            st.markdown("---")
    else:
        st.info("🎈 No se encontraron cumpleañeros para la fecha seleccionada.")

except Exception as e:
    st.error(f"Ocurrió un error general: {e}")
