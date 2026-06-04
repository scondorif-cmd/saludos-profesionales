import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración estética de la página web
st.set_page_config(page_title="Cumpleaños UNAMAD", page_icon="🎓", layout="centered")

st.title("📊 Sistema de Cumpleaños UNAMAD")
st.write("Control y envío de saludos para egresados desde la nube (PC o Celular).")

# 1. Selector de fecha interactivo en la pantalla
fecha_seleccionada = st.date_input("📆 Selecciona la fecha a procesar:", datetime.now())
dia_buscado = fecha_seleccionada.strftime("%d/%m")

# Enlace de tu base de datos
url_google_sheets = "https://docs.google.com/spreadsheets/d/1ScZqatCGsyBUAOQBTdwkTxfOoZNlRfuTD5bhy_iRCao/edit?usp=sharing"

def descargar_datos():
    if "edit" in url_google_sheets:
        url_descarga = url_google_sheets.split('/edit')[0] + '/export?format=xlsx'
    else:
        url_descarga = url_google_sheets
    
    resp = requests.get(url_descarga)
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

def generar_imagen_tarjeta(nombre, carrera, es_varon):
    # Crear una imagen limpia desde cero estilo tarjeta digital
    ancho, alto = 600, 500
    img = Image.new('RGB', (ancho, alto), color='#f6f6f6')
    draw = ImageDraw.Draw(img)
    
    # Definir colores según el sexo
    color_cabecera = "#1b365d" if es_varon else "#871b83"
    color_pie = "#0b1d33" if es_varon else "#4a0e47"
    
    # Dibujar Cabecera
    draw.rectangle([0, 0, ancho, 100], fill=color_cabecera)
    
    # Dibujar Bordes y Pie de página
    draw.rectangle([0, alto-80, ancho, alto], fill=color_pie)
    
    # Intentar cargar fuentes por defecto
    try:
        font_titulo = ImageFont.load_default()
    except:
        font_titulo = None
        
    # Escribir textos en la tarjeta de manera limpia
    draw.text((30, 30), f"¡Feliz Cumpleaños, {nombre}!", fill="white")
    draw.text((30, 65), f"Egresado(a) de {carrera}", fill="#e2e8f0")
    
    # Mensaje central institucional
    cuerpo_texto = (
        f"Estimado(a) egresado(a),\n\n"
        f"Hoy es un día muy especial, y desde la Unidad de Seguimiento al\n"
        f"Egresado y Bolsa de Trabajo queremos hacerte llegar nuestras más\n"
        f"sinceras felicitaciones por tu cumpleaños.\n\n"
        f"Nos sentimos muy orgullosos de tus pasos. Deseamos que pases un\n"
        f"día extraordinario junto a tus seres queridos.\n\n"
        f"¡Que disfrutes mucho de tu día!"
    )
    draw.text((30, 130), cuerpo_texto, fill="#334155")
    
    # Texto de Cierre institucional en el pie
    draw.text((30, alto-60), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="white")
    draw.text((30, alto-35), "Universidad Nacional Amazónica de Madre de Dios", fill="#e2e8f0")
    
    # Guardar en memoria para descarga
    img_ram = io.BytesIO()
    img.save(img_ram, format='PNG')
    return img_ram.getvalue()

try:
    df = descargar_datos()
    st.success("✅ Conexión con Google Sheets exitosa.")
    
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
            emoji = "👨‍🎓" if es_varon else "👩‍🎓"
            
            # Formatear el mensaje de WhatsApp
            texto_whatsapp = f"✨ *¡HOY CELEBRAMOS SU CUMPLEAÑOS!* 🎂🎉\n\nDesde la *Unidad de Seguimiento al Egresado UNAMAD*, enviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n{emoji} *{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! 🌟🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}" if num_limpio and num_limpio != "nan" else f"https://api.whatsapp.com/send?text={texto_codificado}"
            
            # Crear la tarjeta gráfica en memoria
            datos_imagen = generar_imagen_tarjeta(nombre_egresado, carrera_profesional, es_varon)
            
            # --- DISEÑO VISUAL DE CADA CASILLA EN LA PÁGINA WEB ---
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(datos_imagen, caption=f"Tarjeta de {nombre_egresado}", use_container_width=True)
                    # Botón para descargar la imagen directamente al almacenamiento del celular
                    st.download_button(label="💾 Guardar Imagen", data=datos_imagen, file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png", mime="image/png", key=f"dl_{index}")
                with col2:
                    st.markdown(f"### 🎉 {nombre_egresado}")
                    st.caption(f"🎓 {carrera_profesional}")
                    st.info(texto_whatsapp)
                    # Botón de envío directo a la app de WhatsApp
                    st.text_input("Número destino:", value=num_limpio if num_limpio != "nan" else "No registrado", disabled=True, key=f"num_{index}")
                    st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer;">🟢 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"📅 No hay egresados que cumplan años en la fecha elegida ({dia_buscado}).")

except Exception as e:
    st.error(f"Ocurrió un error general: {e}")