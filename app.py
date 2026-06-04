import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
import io
import os
from PIL import Image, ImageDraw, ImageFont

# Configuración de la plataforma
st.set_page_config(page_title="Control de Cumpleaños UNAMAD", page_icon="🎓", layout="centered")

st.title("🎓 Sistema de Cumpleaños UNAMAD")
st.write("Control y envío de saludos para egresados desde la nube (PC o Celular).")

# Selector de fecha interactivo
fecha_seleccionada = st.date_input("Selecciona la fecha a procesar:", datetime.now())
dia_buscado = fecha_seleccionada.strftime("%d/%m")

# Enlace de tu base de datos en Google Sheets
url_google_sheets = "https://docs.google.com/spreadsheets/d/1ScZqatCGsyBUAOQBTdwkTxfOoZNlRfuTD5bhy_iRCao/edit?usp=sharing"

def descargar_datos():
    if "edit" in url_google_sheets:
        url_descarga = url_google_sheets.split('/edit')[0] + '/export?format=xlsx'
    else:
        url_descarga = url_google_sheets
    resp = requests.get(url_descarga)
    # Pandas procesa la lectura manteniendo la integridad de caracteres especiales
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

def conseguir_fuente_servidor(es_bold, tamano):
    """Descarga e integra dinámicamente tipografías con soporte UTF-8 completo (tildes, Ñ, ¡, ¿)"""
    nombre_archivo = "fuente_latina_bold.ttf" if es_bold else "fuente_latina_regular.ttf"
    
    # Repositorio oficial de Google Fonts (Garantiza renderizado perfecto en servidores Linux)
    url_font = (
        "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Bold.ttf"
        if es_bold else
        "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf"
    )
    
    # Descarga local en la caché del servidor (Solo ocurre la primera vez que se ejecuta)
    if not os.path.exists(nombre_archivo):
        try:
            r = requests.get(url_font, timeout=6)
            with open(nombre_archivo, "wb") as f:
                f.write(r.content)
        except:
            pass

    # Forzar uso del set de caracteres descargado
    if os.path.exists(nombre_archivo):
        try:
            return ImageFont.truetype(nombre_archivo, tamano)
        except:
            pass
            
    # Rutas físicas secundarias de contingencia en sistemas Linux Debian/Ubuntu
    rutas_fuentes = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if es_bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if es_bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    
    for ruta in rutas_fuentes:
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, tamano)
            except:
                continue
                
    try:
        return ImageFont.load_default(size=tamano)
    except:
        return ImageFont.load_default()

def crear_tarjeta_perfecta(nombre, carrera):
    # Dimensiones exactas (750 x 850)
    ancho, alto = 750, 850
    imagen = Image.new("RGB", (ancho, alto), "#FFFFFF")
    draw = ImageDraw.Draw(imagen)
    
    # === ASIGNACIÓN DE TIPOGRAFÍAS CON SOPORTE CORREGIDO ===
    f_titulo = conseguir_fuente_servidor(True, 32)         # Nombre arriba
    f_subtitulo = conseguir_fuente_servidor(False, 15)     # Carrera profesional
    f_cuerpo_bold = conseguir_fuente_servidor(True, 23)    # "Estimado(a) egresado(a),"
    f_cuerpo = conseguir_fuente_servidor(False, 19)       # Texto de felicitación
    f_eslogan = conseguir_fuente_servidor(True, 26)        # ¡Que disfrutes mucho de tu día!
    f_pie_tit = conseguir_fuente_servidor(True, 14)        # ATENTAMENTE,
    f_pie_sub = conseguir_fuente_servidor(True, 16)        # Unidad de Seguimiento...
    f_pie_univ = conseguir_fuente_servidor(False, 13)      # Universidad Nacional...

    # 1. Banner Superior Azul Institucional
    draw.rectangle([0, 0, ancho, 155], fill="#1B365D")
    draw.text((ancho // 2, 55), f"¡Feliz Cumpleaños, {nombre.upper()}!", fill="#FFFFFF", font=f_titulo, anchor="mm")
    
    texto_carrera = f"Egresado(a) de la Carrera Profesional de {carrera.upper()}"
    if len(texto_carrera) > 68:
        draw.text((ancho // 2, 110), texto_carrera[:65] + "...", fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    else:
        draw.text((ancho // 2, 110), texto_carrera, fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    
    # 2. Cuerpo del Mensaje con Ortografía y Tildes Estables
    draw.text((50, 205), "Estimado(a) egresado(a),", fill="#1E293B", font=f_cuerpo_bold)
    
    lineas = [
        "Hoy es un día muy especial, y desde la",
        "Unidad de Seguimiento al Egresado y",
        "Bolsa de Trabajo queremos hacerte llegar",
        "nuestras más sinceras felicitaciones por",
        "tu cumpleaños.",
        "",
        "Nos sentimos muy orgullosos de tus pasos y",
        "de tenerte como miembro activo de nuestra",
        "comunidad de graduados. Deseamos que",
        "pases un día extraordinario junto a tus seres",
        "queridos y que este nuevo año esté lleno de",
        "salud, felicidad y grandes éxitos profesionales."
    ]
    
    y_linea = 260
    for linea in lineas:
        draw.text((50, y_linea), linea, fill="#334155", font=f_cuerpo)
        y_linea += 36  
        
    # Mensaje de Cierre destacado abajo
    draw.text((ancho // 2, 705), "¡Que disfrutes mucho de tu día!", fill="#1B365D", font=f_eslogan, anchor="mm")
    
    # 3. Bloque Inferior del Pie de Página (Azul Oscuro Limpio)
    draw.rectangle([0, alto - 115, ancho, alto], fill="#0B1D33")
    draw.text((ancho // 2, alto - 85), "ATENTAMENTE,", fill="#38BDF8", font=f_pie_tit, anchor="mm")
    draw.text((ancho // 2, alto - 60), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", font=f_pie_sub, anchor="mm")
    draw.text((ancho // 2, alto - 35), "Universidad Nacional Amazónica de Madre de Dios", fill="#94A3B8", font=f_pie_univ, anchor="mm")
    
    # 4. Integración de la Mascota Jaguar (Desde Google Drive)
    try:
        id_drive = "10fW68y7oiTcr-VcPoEW1V-OQ4O3psxup"
        url_mascota = f"https://docs.google.com/uc?export=download&id={id_drive}"
        res_img = requests.get(url_mascota, timeout=10)
        img_mascota = Image.open(io.BytesIO(res_img.content)).convert("RGBA")
        img_mascota = img_mascota.resize((190, 220)) 
        imagen.paste(img_mascota, (525, 230), img_mascota) 
    except:
        pass
        
    return imagen

try:
    df = descargar_datos()
    st.success("✅ Conexión con la base de datos exitosa.")
    
    st.subheader(f"🎂 Cumpleañeros del día {dia_buscado}:")
    contador = 0
    
    for index, fila in df.iterrows():
        try:
            nombre_completo = str(fila[3]).strip()       
            carrera_profesional = str(fila[4]).strip()   
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
            
            # Formateo de mensaje para WhatsApp
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            # Generar tarjeta con motor tipográfico adaptado
            imagen_tarjeta = crear_tarjeta_perfecta(nombre_egresado, carrera_profesional)
            
            buf = io.BytesIO()
            imagen_tarjeta.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                st.image(imagen_tarjeta, use_container_width=True, caption=f"Tarjeta Oficial - {nombre_egresado}")
                
                # Botón de Descarga Estilizado en Azul Premium
                st.download_button(
                    label="💾 Descargar Tarjeta PNG",
                    data=byte_im,
                    file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"btn_dl_{index}",
                    use_container_width=True
                )
                
                # Inyección estética CSS
                st.markdown("""
                    <style>
                    div.stDownloadButton > button {
                        background: linear-gradient(135deg, #1B365D 0%, #0B1D33 100%) !important;
                        color: white !important;
                        border: 1px solid #38BDF8 !important;
                        padding: 12px 24px !important;
                        font-weight: bold !important;
                        border-radius: 8px !important;
                        transition: all 0.3s ease !important;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
                        font-size: 16px !important;
                    }
                    div.stDownloadButton > button:hover {
                        background: linear-gradient(135deg, #38BDF8 0%, #1B365D 100%) !important;
                        transform: translateY(-2px) !important;
                        box-shadow: 0 6px 12px rgba(56, 189, 248, 0.4) !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
