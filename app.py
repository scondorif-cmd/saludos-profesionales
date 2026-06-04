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

def obtener_fuente_segura(url, tamano):
    """Descarga una fuente TTF directamente de internet para evitar distorsiones en el servidor"""
    try:
        respuesta = requests.get(url)
        return ImageFont.truetype(io.BytesIO(respuesta.content), tamano)
    except:
        return ImageFont.load_default()

def crear_tarjeta_imagen(nombre, carrera):
    # Dimensiones óptimas para tarjetas de felicitación
    ancho, alto = 750, 850
    imagen = Image.new("RGB", (ancho, alto), "#FFFFFF")
    draw = ImageDraw.Draw(imagen)
    
    # Enlaces de fuentes seguras (Arial / Roboto equivalentes desde GitHub público)
    url_fuente_bold = "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Bold.ttf"
    url_fuente_regular = "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf"
    
    f_titulo = obtener_fuente_segura(url_fuente_bold, 28)
    f_subtitulo = obtener_fuente_segura(url_fuente_regular, 15)
    f_cuerpo_bold = obtener_fuente_segura(url_fuente_bold, 18)
    f_cuerpo = obtener_fuente_segura(url_fuente_regular, 17)
    f_eslogan = obtener_fuente_segura(url_fuente_bold, 20)
    f_pie_tit = obtener_fuente_segura(url_fuente_bold, 13)
    f_pie_sub = obtener_fuente_segura(url_fuente_bold, 15)
    f_pie_univ = obtener_fuente_segura(url_fuente_regular, 13)

    # 1. Encabezado Azul Institucional (#1B365D)
    draw.rectangle([0, 0, ancho, 140], fill="#1B365D")
    draw.text((ancho // 2, 45), f"¡Feliz Cumpleaños, {nombre.upper()}! 🎂🎉", fill="#FFFFFF", font=f_titulo, anchor="mm")
    draw.text((ancho // 2, 95), f"Egresado(a) de la Carrera Profesional de {carrera.upper()}", fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    
    # 2. Contenido del Cuerpo (Texto alineado a la izquierda en color oscuro)
    draw.text((50, 190), "Estimado(a) egresado(a),", fill="#1E293B", font=f_cuerpo_bold)
    
    lineas = [
        "Hoy es un día muy especial, y desde la Unidad de Seguimiento al",
        "Egresado y Bolsa de Trabajo queremos hacerte llegar nuestras más",
        "sinceras felicitaciones por tu cumpleaños.",
        "",
        "Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo",
        "de nuestra comunidad de graduados. Deseamos que pases un día",
        "extraordinario junto a tus seres queridos y que este nuevo año esté lleno",
        "de salud, felicidad y grandes éxitos profesionales."
    ]
    
    y_linea = 240
    for linea in lineas:
        draw.text((50, y_linea), linea, fill="#334155", font=f_cuerpo)
        y_linea += 32
        
    # Mensaje de cierre destacado
    draw.text((ancho // 2, 570), "¡Que disfrutes mucho de tu día!", fill="#1B365D", font=f_eslogan, anchor="mm")
    
    # 3. Pie de Página Azul Oscuro (#0B1D33)
    draw.rectangle([0, alto - 150, ancho, alto], fill="#0B1D33")
    draw.text((ancho // 2, alto - 110), "ATENTAMENTE,", fill="#38BDF8", font=f_pie_tit, anchor="mm")
    draw.text((ancho // 2, alto - 80), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", font=f_pie_sub, anchor="mm")
    draw.text((ancho // 2, alto - 50), "Universidad Nacional Amazónica de Madre de Dios", fill="#CBD5E1", font=f_pie_univ, anchor="mm")
    
    # 4. Superponer la Mascota Institucional de forma correcta
    try:
        url_mascota = "https://raw.githubusercontent.com/scondorif-cmd/saludos-profesionales/principal/mascota.png"
        res_img = requests.get(url_mascota)
        img_mascota = Image.open(io.BytesIO(res_img.content)).convert("RGBA")
        # Ajustar tamaño proporcional
        img_mascota = img_mascota.resize((150, 175))
        # Colocar en la esquina derecha del cuerpo de texto
        imagen.paste(img_mascota, (540, 180), img_mascota)
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
            
            # Formatear el texto de envío para WhatsApp
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            # Generar la imagen sólida con Pillow
            imagen_tarjeta = crear_tarjeta_imagen(nombre_egresado, carrera_profesional)
            
            # Preparar descarga de la imagen en memoria
            buf = io.BytesIO()
            imagen_tarjeta.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            # Interfaz de visualización limpia en 2 columnas fijas
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                st.image(imagen_tarjeta, use_container_width=True, caption=f"Tarjeta Oficial - {nombre_egresado}")
                
                # Botón oficial para guardar el archivo .png real
                st.download_button(
                    label=f"💾 Guardar / Descargar Tarjeta (.png)",
                    data=byte_im,
                    file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"btn_dl_{index}"
                )
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
