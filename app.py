import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración estética de la página web
st.set_page_config(page_title="Control de Cumpleaños", page_icon="🎓", layout="centered")

st.title("📊 Sistema de Cumpleaños")
st.write("Control y envío de saludos para egresados desde la nube (PC o Celular).")

# Selector de fecha interactivo
fecha_seleccionada = st.date_input("Selecciona la fecha a procesar:", datetime.now())
dia_buscado = fecha_seleccionada.strftime("%d/%m")

# TU ENLACE REAL Y CORRECTO
url_google_sheets = "https://docs.google.com/spreadsheets/d/1ScZqatCGsyBUAOQBTdwkTxfOoZNlRfuTD5bhy_iRCao/edit?usp=sharing"

def descargar_datos():
    if "edit" in url_google_sheets:
        url_descarga = url_google_sheets.split('/edit')[0] + '/export?format=xlsx'
    else:
        url_descarga = url_google_sheets
    resp = requests.get(url_descarga)
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

def generar_imagen_tarjeta(nombre, carrera, es_varon):
    ancho, alto = 1200, 850
    img = Image.new('RGB', (ancho, alto), color='#f6f6f6')
    draw = ImageDraw.Draw(img)
    
    color_cabecera = "#1b365d" if es_varon else "#871b83"
    color_pie = "#0b1d33" if es_varon else "#4a0e47"
    
    draw.rectangle([0, 0, ancho, 180], fill=color_cabecera)
    draw.rectangle([0, alto-100, ancho, alto], fill=color_pie)
    
    # Intentar usar fuentes compatibles con Linux en la nube para evitar símbolos rotos
    try:
        font_titulo = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 26)
        font_cuerpo = ImageFont.truetype("DejaVuSans.ttf", 30)
        font_pie = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except IOError:
        font_titulo = font_sub = font_cuerpo = font_pie = ImageFont.load_default()
    
    # Textos dentro de la tarjeta con soporte de tildes
    draw.text((50, 40), f"¡Feliz Cumpleaños, {nombre}!", fill="white", font=font_titulo)
    draw.text((50, 110), f"Egresado(a) de {carrera}", fill="#e2e8f0", font=font_sub)
    
    cuerpo_texto = (
        f"Estimado(a) egresado(a),\n\n"
        f"Hoy es un día muy especial, y desde la Unidad de Seguimiento al\n"
        f"Egresado y Bolsa de Trabajo queremos hacerte llegar nuestras más\n"
        f"sinceras felicitaciones por tu cumpleaños.\n\n"
        f"Nos sentimos muy orgullosos de tus pasos. Deseamos que pases un\n"
        f"día extraordinario junto a tus seres queridos.\n\n"
        f"¡Que disfrutes mucho de tu día!"
    )
    draw.text((50, 240), cuerpo_texto, fill="#334155", font=font_cuerpo, spacing=12)
    
    draw.text((50, alto-75), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo", fill="white", font=font_pie)
    draw.text((50, alto-45), "Universidad Nacional Amazónica de Madre de Dios", fill="#e2e8f0", font=font_pie)
    
    img_ram = io.BytesIO()
    img.save(img_ram, format='PNG')
    return img_ram.getvalue()

try:
    df = descargar_datos()
    st.success("Conexión con la base de datos exitosa.")
    
    st.subheader(f"Cumpleañeros del día {dia_buscado}:")
    contador = 0
    
    for index, fila in df.iterrows():
        try:
            nombre_completo = str(fila[3]).strip()       
            carrera_profesional = str(fila[4]).strip()   
            sexo_celda = str(fila[42]).strip().upper()   
            fecha_celda = str(fila[43]).strip()          
            celular_celda = str(fila[7]).strip().replace(".0", "").replace(" ", "")
        except:
            continue
            
        if not fecha_celda or fecha_celda == "nan" or fecha_celda == "-":
            continue
            
        fecha_texto = ""
        if "-" in fecha_celda and len(fecha_celda) >= 10:
            partes = fecha_celda.split(" ")[0].split("-")
            fecha_texto = f"{partes[2]}/{partes[1]}"
        elif "/" in fecha_celda:
            partes = fecha_celda.split("/")
            fecha_texto = f"{partes[0].zfill(2)}/{partes[1].zfill(2)}"
            
        if fecha_texto == dia_buscado:
            contador += 1
            nombre_egresado = nombre_completo.split(",")[1].strip() if "," in nombre_completo else nombre_completo
            es_varon = sexo_celda in ["M", "MASCULINO", "VARON", "VARÓN"]
            
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}" if num_limpio and num_limpio != "nan" else f"https://api.whatsapp.com/send?text={texto_codificado}"
            
            datos_imagen = generar_imagen_tarjeta(nombre_egresado, carrera_profesional, es_varon)
            
            with st.container():
                col1, col2 = st.columns([1.2, 1.5])
                with col1:
                    st.image(datos_imagen, use_container_width=True)
                    st.download_button(label="💾 Guardar Imagen", data=datos_imagen, file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png", mime="image/png", key=f"dl_{index}")
                with col2:
                    st.markdown(f"### {nombre_egresado}")
                    st.info(texto_whatsapp)
                    st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer;">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"No hay egresados que cumplan años en la fecha elegida ({dia_buscado}).")

except Exception as e:
    st.error(f"Error: {e}")
