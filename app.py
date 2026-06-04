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
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

def conseguir_fuente_sistema(es_bold, tamano):
    """Busca de forma infalible fuentes sans-serif escalables en el servidor Linux de Streamlit"""
    opciones = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if es_bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if es_bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if es_bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]
    for ruta in opciones:
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, tamano)
    
    # Intentos por carga directa de fuentes del sistema
    try:
        return ImageFont.truetype("LiberationSans-Bold.ttf" if es_bold else "LiberationSans-Regular.ttf", tamano)
    except:
        return ImageFont.load_default()

def crear_tarjeta_perfecta(nombre, carrera):
    # Dimensiones exactas basadas en Tarjeta_SHANIRA.png (750 x 850)
    ancho, alto = 750, 850
    imagen = Image.new("RGB", (ancho, alto), "#FFFFFF")
    draw = ImageDraw.Draw(imagen)
    
    # === TAMAÑOS MÁXIMOS INTERNOS (Grosor idéntico a Arial de Windows) ===
    f_titulo = conseguir_fuente_sistema(True, 32)        # Título del Egresado
    f_subtitulo = conseguir_fuente_sistema(False, 14)    # Carrera profesional
    f_cuerpo_bold = conseguir_fuente_sistema(True, 22)   # "Estimado(a) egresado(a),"
    f_cuerpo = conseguir_fuente_sistema(False, 19)      # Texto completo del cuerpo
    f_eslogan = conseguir_fuente_sistema(True, 26)       # "¡Que disfrutes mucho de tu día!"
    f_pie_tit = conseguir_fuente_sistema(True, 13)       # "ATENTAMENTE,"
    f_pie_sub = conseguir_fuente_sistema(True, 15)       # Unidad de seguimiento
    f_pie_univ = conseguir_fuente_sistema(False, 13)     # Universidad

    # 1. Encabezado Azul Institucional
    draw.rectangle([0, 0, ancho, 155], fill="#1B365D")
    draw.text((ancho // 2, 55), f"¡Feliz Cumpleaños, {nombre.upper()}!", fill="#FFFFFF", font=f_titulo, anchor="mm")
    
    # Manejo de carreras largas para evitar desbordes visuales
    texto_carrera = f"Egresado(a) de la Carrera Profesional de {carrera.upper()}"
    if len(texto_carrera) > 65:
        draw.text((ancho // 2, 105), texto_carrera[:65] + "...", fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    else:
        draw.text((ancho // 2, 105), texto_carrera, fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    
    # 2. Bloque de Texto del Cuerpo (Perfectamente formateado y alineado a la izquierda)
    draw.text((50, 200), "Estimado(a) egresado(a),", fill="#1E293B", font=f_cuerpo_bold)
    
    lineas = [
        "Hoy es un día muy especial, y desde la Unidad de",
        "Seguimiento al Egresado y Bolsa de Trabajo queremos",
        "hacerte llegar nuestras más sinceras felicitaciones por tu",
        "cumpleaños.",
        "",
        "Nos sentimos muy orgullosos de tus pasos y de tenerte como",
        "miembro activo de nuestra comunidad de graduados. Deseamos",
        "que pases un día extraordinario junto a tus seres queridos y que",
        "este nuevo año esté lleno de salud, felicidad y grandes éxitos",
        "profesionales."
    ]
    
    y_linea = 250
    for linea in lineas:
        draw.text((50, y_linea), linea, fill="#334155", font=f_cuerpo)
        y_linea += 36  # Separación perfecta
        
    # Mensaje de Cierre Destacado
    draw.text((ancho // 2, 680), "¡Que disfrutes mucho de tu día!", fill="#1B365D", font=f_eslogan, anchor="mm")
    
    # 3. Pie de Página Azul Oscuro Ampliado
    draw.rectangle([0, alto - 140, ancho, alto], fill="#0B1D33")
    draw.text((ancho // 2, alto - 105), "ATENTAMENTE,", fill="#38BDF8", font=f_pie_tit, anchor="mm")
    draw.text((ancho // 2, alto - 75), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", font=f_pie_sub, anchor="mm")
    draw.text((ancho // 2, alto - 48), "Universidad Nacional Amazónica de Madre de Dios", fill="#94A3B8", font=f_pie_univ, anchor="mm")
    
    # 4. Inserción de la Mascota Jaguar desde Google Drive con Fallback Seguro
    try:
        id_drive = "10fW68y7oiTcr-VcPoEW1V-OQ4O3psxup"
        url_mascota = f"https://docs.google.com/uc?export=download&id={id_drive}"
        res_img = requests.get(url_mascota, timeout=8)
        img_mascota = Image.open(io.BytesIO(res_img.content)).convert("RGBA")
        img_mascota = img_mascota.resize((155, 180)) 
        imagen.paste(img_mascota, (540, 200), img_mascota)
    except:
        # Si falla la descarga, dibuja un recuadro estético para evitar dejar la zona rota
        draw.rectangle([540, 200, 695, 380], outline="#E2E8F0", width=1)
        
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
            
            # Mensaje estructurado de WhatsApp
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            # Generar la imagen real usando el motor de fuentes fijas del sistema
            imagen_tarjeta = crear_tarjeta_perfecta(nombre_egresado, carrera_profesional)
            
            buf = io.BytesIO()
            imagen_tarjeta.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                st.image(imagen_tarjeta, use_container_width=True, caption=f"Tarjeta Oficial - {nombre_egresado}")
                
                # --- BOTÓN DE DESCARGA CON ESTILO REFORZADO ---
                st.download_button(
                    label="💾 Descargar Tarjeta PNG",
                    data=byte_im,
                    file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"btn_dl_{index}",
                    use_container_width=True
                )
                
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
