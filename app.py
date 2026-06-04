import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración estética de la página web
st.set_page_config(page_title="Control de Cumpleaños", page_icon="🎓", layout="centered")

st.title("🎓 Sistema de Cumpleaños UNAMAD")
st.write("Control y envío de saludos para egresados desde la nube (PC o Celular).")

# Selector de fecha interactivo
fecha_seleccionada = st.date_input("Selecciona la fecha a procesar:", datetime.now())
dia_buscado = fecha_seleccionada.strftime("%d/%m")

# Tu enlace de Google Sheets real
url_google_sheets = "https://docs.google.com/spreadsheets/d/1ScZqatCGsyBUAOQBTdwkTxfOoZNlRfuTD5bhy_iRCao/edit?usp=sharing"

def descargar_datos():
    if "edit" in url_google_sheets:
        url_descarga = url_google_sheets.split('/edit')[0] + '/export?format=xlsx'
    else:
        url_descarga = url_google_sheets
    resp = requests.get(url_descarga)
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

# DESCARGA DE FUENTES CORREGIDA (Enlaces estables de jsDelivr)
@st.cache_data
def descargar_fuentes():
    try:
        url_bold = "https://cdn.jsdelivr.net/gh/google/fonts@main/apache/roboto/static/Roboto-Bold.ttf"
        url_reg = "https://cdn.jsdelivr.net/gh/google/fonts@main/apache/roboto/static/Roboto-Regular.ttf"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        f_bold = io.BytesIO(requests.get(url_bold, headers=headers).content)
        f_reg = io.BytesIO(requests.get(url_reg, headers=headers).content)
        return f_bold, f_reg
    except:
        return None, None

def generar_imagen_tarjeta(nombre, carrera, es_varon):
    ancho, alto = 1200, 850
    img = Image.new('RGB', (ancho, alto), color='#F8FAFC')
    draw = ImageDraw.Draw(img)
    
    color_cabecera = "#1B365D" if es_varon else "#6B21A8"
    color_pie = "#0F172A" if es_varon else "#4C1D95"
    
    draw.rectangle([0, 0, ancho, 200], fill=color_cabecera)
    draw.rectangle([0, alto-110, ancho, alto], fill=color_pie)
    
    f_bold, f_reg = descargar_fuentes()
    if f_bold and f_reg:
        font_titulo = ImageFont.truetype(f_bold, 44)
        font_sub = ImageFont.truetype(f_reg, 26)
        font_cuerpo = ImageFont.truetype(f_reg, 32)
        font_pie_bold = ImageFont.truetype(f_bold, 22)
        font_pie_reg = ImageFont.truetype(f_reg, 20)
    else:
        # Respaldo seguro por si falla la red
        font_titulo = font_sub = font_cuerpo = font_pie_bold = font_pie_reg = ImageFont.load_default()
    
    draw.text((60, 45), f"¡Feliz Cumpleaños, {nombre}!", fill="#FFFFFF", font=font_titulo)
    draw.text((60, 120), f"Egresado(a) de {carrera}", fill="#E2E8F0", font=font_sub)
    
    cuerpo_texto = (
        f"Estimado(a) egresado(a),\n\n"
        f"Hoy es un día muy especial, y desde la Unidad de Seguimiento al\n"
        f"Egresado y Bolsa de Trabajo queremos hacerte llegar nuestras más\n"
        f"sinceras felicitaciones por tu cumpleaños.\n\n"
        f"Nos sentimos muy orgullosos de tus pasos. Deseamos que pases un\n"
        f"día extraordinario junto a tus seres queridos.\n\n"
        f"¡Que disfrutes mucho de tu día!"
    )
    draw.text((60, 260), cuerpo_texto, fill="#334155", font=font_cuerpo, spacing=14)
    
    draw.text((60, alto-85), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo", fill="#FFFFFF", font=font_pie_bold)
    draw.text((60, alto-50), "Universidad Nacional Amazónica de Madre de Dios", fill="#CBD5E1", font=font_pie_reg)
    
    img_ram = io.BytesIO()
    img.save(img_ram, format='PNG')
    return img_ram.getvalue()

try:
    df = descargar_datos()
    st.success("✅ Conexión con la base de datos exitosa.")
    
    st.subheader(f"🎂 Cumpleañeros del día {dia_buscado}:")
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
                col1, col2 = st.columns([1.3, 1.2])
                with col1:
                    st.image(datos_imagen, use_container_width=True)
                    st.download_button(label="💾 Guardar Imagen", data=datos_imagen, file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png", mime="image/png", key=f"dl_{index}")
                with col2:
                    st.markdown(f"## 🥳 {nombre_egresado}")
                    st.info(texto_whatsapp)
                    st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:16px;">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
