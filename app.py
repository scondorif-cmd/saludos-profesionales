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
st.write("Generación automatizada de tarjetas institucionales con descarga en alta calidad.")

# Selector de fecha interactivo
fecha_seleccionada = st.date_input("Selecciona la fecha a procesar:", datetime.now())
dia_buscado = fecha_seleccionada.strftime("%d/%m")

url_google_sheets = "https://docs.google.com/spreadsheets/d/1ScZqatCGsyBUAOQBTdwkTxfOoZNlRfuTD5bhy_iRCao/edit?usp=sharing"

def descargar_datos():
    if "edit" in url_google_sheets:
        url_descarga = url_google_sheets.split('/edit')[0] + '/export?format=xlsx'
    else:
        url_descarga = url_google_sheets
    resp = requests.get(url_descarga)
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

def crear_tarjeta_imagen(nombre, carrera):
    # Dimensiones de lienzo idénticas a la tarjeta original
    ancho, alto = 750, 850
    imagen = Image.new("RGB", (ancho, alto), "#FFFFFF")
    draw = ImageDraw.Draw(imagen)
    
    # 1. Encabezado Institucional Azul
    draw.rectangle([0, 0, ancho, 150], fill="#1B365D")
    
    # Fuentes por defecto del sistema seguras para evitar errores de archivo roto ("broken file")
    try:
        # Intentamos cargar una fuente estándar del servidor si estuviera disponible
        f_tit = ImageFont.truetype("LiberationSans-Bold.ttf", 26)
        f_sub = ImageFont.truetype("LiberationSans-Regular.ttf", 14)
        f_txt = ImageFont.truetype("LiberationSans-Regular.ttf", 16)
    except:
        # Respaldo absoluto para que jamás vuelva a salir "broken file"
        f_tit = ImageFont.load_default()
        f_sub = ImageFont.load_default()
        f_txt = ImageFont.load_default()

    # Escribir textos en el encabezado
    draw.text((ancho // 2, 45), f"¡Feliz Cumpleaños, {nombre.upper()}! 🎂🎉", fill="#FFFFFF", font=f_tit, anchor="mm")
    draw.text((ancho // 2, 95), f"Egresado(a) de la Carrera Profesional de {carrera.upper()}", fill="#E2E8F0", font=f_sub, anchor="mm")
    
    # 2. Textos del Cuerpo (Alineados a la izquierda sobre fondo blanco limpio)
    draw.text((45, 190), "Estimado(a) egresado(a),", fill="#1E293B", font=f_tit)
    
    lineas_mensaje = [
        "Hoy es un día muy especial, y desde la Unidad de Seguimiento al",
        "Egresado y Bolsa de Trabajo queremos hacerte llevar nuestras más",
        "sinceras felicitaciones por tu cumpleaños.",
        "",
        "Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo",
        "de nuestra comunidad de graduados. Deseamos que pases un día",
        "extraordinario junto a tus seres queridos y que este nuevo año esté lleno",
        "de salud, felicidad y grandes éxitos profesionales."
    ]
    
    y_lineas = 235
    for linea in lineas_mensaje:
        draw.text((45, y_lineas), linea, fill="#334155", font=f_txt)
        y_lineas += 32
        
    draw.text((ancho // 2, 580), "¡Que disfrutes mucho de tu día!", fill="#1B365D", font=f_tit, anchor="mm")
    
    # 3. Franja Azul Inferior (Pie de página)
    draw.rectangle([0, alto - 140, ancho, alto], fill="#0B1D33")
    draw.text((ancho // 2, alto - 105), "ATENTAMENTE,", fill="#38BDF8", font=f_sub, anchor="mm")
    draw.text((ancho // 2, alto - 75), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", font=f_sub, anchor="mm")
    draw.text((ancho // 2, alto - 45), "Universidad Nacional Amazónica de Madre de Dios", fill="#94A3B8", font=f_sub, anchor="mm")
    
    # 4. Inyección de la Mascota sin usar el enlace problemático de Google Drive
    try:
        url_mascota = "https://raw.githubusercontent.com/scondorif-cmd/saludos-profesionales/principal/mascota.png"
        res_img = requests.get(url_mascota, timeout=5)
        img_mascota = Image.open(io.BytesIO(res_img.content)).convert("RGBA")
        img_mascota = img_mascota.resize((150, 175))
        # Pegar mascota de forma exacta en el espacio blanco superior derecho
        imagen.paste(img_mascota, (540, 180), img_mascota)
    except:
        pass # Evita que se caiga el sistema si el servidor de imágenes falla momentáneamente
        
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
            
            # Texto para WhatsApp
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            # Generar la imagen real de la tarjeta
            imagen_tarjeta = crear_tarjeta_imagen(nombre_egresado, carrera_profesional)
            
            # Convertir la imagen final a bytes legibles por el botón de descarga
            buf = io.BytesIO()
            imagen_tarjeta.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                # Muestra la imagen generada de forma nativa e idéntica
                st.image(imagen_tarjeta, use_container_width=True, caption=f"Vista previa de la Tarjeta Oficial de {nombre_egresado}")
                
                # --- BOTÓN DE DESCARGA DIRECTA FUNCIONAL ---
                st.download_button(
                    label=f"📥 Descargar Tarjeta PNG Real",
                    data=byte_im,
                    file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"btn_descarga_{index}"
                )
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:15px;">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error crítico en el sistema de tarjetas: {e}")
