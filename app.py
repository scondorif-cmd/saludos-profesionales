import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
import io
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

def cargar_fuente_google(url, tamano):
    """Descarga fuentes profesionales con soporte completo de tildes y eñes desde Google Fonts"""
    try:
        respuesta = requests.get(url, timeout=10)
        return ImageFont.truetype(io.BytesIO(respuesta.content), tamano)
    except Exception as e:
        st.warning(f"No se pudo cargar la fuente remota, usando respaldo: {e}")
        return ImageFont.load_default()

def crear_tarjeta_perfecta(nombre, carrera):
    # Dimensiones exactas de la tarjeta original (750 x 850)
    ancho, alto = 750, 850
    imagen = Image.new("RGB", (ancho, alto), "#FFFFFF")
    draw = ImageDraw.Draw(imagen)
    
    # URL de fuentes de Google de alta calidad con soporte total para español (Tildes y Ñ)
    url_bold = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf"
    url_regular = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf"
    
    # === TAMAÑOS MAXIMIZADOS PARA LLENAR EL LIENZO (Idéntico a Tarjeta_SHANIRA.png) ===
    f_titulo = cargar_fuente_google(url_bold, 34)         # ¡Feliz Cumpleaños!
    f_subtitulo = cargar_fuente_google(url_regular, 15)   # Carrera profesional
    f_cuerpo_bold = cargar_fuente_google(url_bold, 24)    # "Estimado(a) egresado(a),"
    f_cuerpo = cargar_fuente_google(url_regular, 20)       # Bloque de texto principal
    f_eslogan = cargar_fuente_google(url_bold, 26)        # ¡Que disfrutes mucho de tu día!
    f_pie_tit = cargar_fuente_google(url_bold, 14)        # ATENTAMENTE,
    f_pie_sub = cargar_fuente_google(url_bold, 15)        # Unidad de Seguimiento...
    f_pie_univ = cargar_fuente_google(url_regular, 13)    # Universidad Nacional...

    # 1. Encabezado Azul Institucional
    draw.rectangle([0, 0, ancho, 155], fill="#1B365D")
    draw.text((ancho // 2, 55), f"¡Feliz Cumpleaños, {nombre.upper()}!", fill="#FFFFFF", font=f_titulo, anchor="mm")
    draw.text((ancho // 2, 108), f"Egresado(a) de la Carrera Profesional de {carrera.upper()}", fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    
    # 2. Bloque de Texto del Cuerpo (Letras grandes, bien espaciadas y adaptadas a la mascota)
    draw.text((50, 205), "Estimado(a) egresado(a),", fill="#1E293B", font=f_cuerpo_bold)
    
    # Alineación manual exacta para cubrir todo el ancho sin chocar con la mascota derecha
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
    
    y_linea = 255
    for linea in lineas:
        draw.text((50, y_linea), linea, fill="#334155", font=f_cuerpo)
        y_linea += 36  # Interlineado perfecto y espacioso
        
    # Mensaje de Cierre destacado abajo
    draw.text((ancho // 2, 675), "¡Que disfrutes mucho de tu día!", fill="#1B365D", font=f_eslogan, anchor="mm")
    
    # 3. Pie de Página Azul Oscuro Formato Completo
    draw.rectangle([0, alto - 140, ancho, alto], fill="#0B1D33")
    draw.text((ancho // 2, it_y := (alto - 105)), "ATENTAMENTE,", fill="#38BDF8", font=f_pie_tit, anchor="mm")
    draw.text((ancho // 2, it_y + 28), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", font=f_pie_sub, anchor="mm")
    draw.text((ancho // 2, it_y + 55), "Universidad Nacional Amazónica de Madre de Dios", fill="#94A3B8", font=f_pie_univ, anchor="mm")
    
    # 4. Inserción de la Mascota Jaguar desde Google Drive
    try:
        id_drive = "10fW68y7oiTcr-VcPoEW1V-OQ4O3psxup"
        url_mascota = f"https://docs.google.com/uc?export=download&id={id_drive}"
        res_img = requests.get(url_mascota, timeout=10)
        img_mascota = Image.open(io.BytesIO(res_img.content)).convert("RGBA")
        img_mascota = img_mascota.resize((155, 180)) # Escala idéntica a la original
        imagen.paste(img_mascota, (545, 205), img_mascota)
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
            
            # Mensaje estructurado de WhatsApp
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            # Generar la tarjeta procesada con tipografías premium Montserrat de Google
            imagen_tarjeta = crear_tarjeta_perfecta(nombre_egresado, carrera_profesional)
            
            buf = io.BytesIO()
            imagen_tarjeta.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                st.image(imagen_tarjeta, use_container_width=True, caption=f"Tarjeta Oficial - {nombre_egresado}")
                
                # --- BOTÓN DE DESCARGA CON ESTILO AZUL INSTITUCIONAL PREMIUM ---
                st.download_button(
                    label="💾 Descargar Tarjeta PNG",
                    data=byte_im,
                    file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"btn_dl_{index}",
                    use_container_width=True
                )
                
                # Inyección de estilos CSS avanzados para transformar el botón de descarga
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
