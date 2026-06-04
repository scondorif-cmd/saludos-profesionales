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

@st.cache_data(ttl=3600)
def cargar_fuente_web(es_bold, tamano):
    """Descarga dinámicamente tipografías modernas con soporte nativo de tildes y Ñ en español"""
    try:
        if es_bold:
            url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"
        else:
            url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
        
        respuesta = requests.get(url, timeout=10)
        return ImageFont.truetype(io.BytesIO(respuesta.content), tamano)
    except:
        # En caso de un fallo extremo de red, usa la fuente de respaldo del sistema escalada
        try:
            return ImageFont.load_default(size=tamano)
        except:
            return ImageFont.load_default()

def dibujar_texto_justificado(draw, texto, x_inicio, y_inicio, ancho_maximo, font, color="#334155", interlineado=30):
    """Genera una distribución matemática exacta de espacios para justificar bloques de texto de manera perfecta"""
    palabras = texto.split()
    if not palabras:
        return y_inicio

    lineas = []
    linea_actual = []
    
    # 1. Agrupar palabras respetando el ancho límite
    for palabra in palabras:
        test_linea = ' '.join(linea_actual + [palabra])
        bbox = draw.textbbox((0, 0), test_linea, font=font)
        ancho_test = bbox[2] - bbox[0]
        
        if ancho_test <= ancho_maximo:
            linea_actual.append(palabra)
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = [palabra]
    if linea_actual:
        lineas.append(linea_actual)

    y = y_inicio
    
    # 2. Renderizar cada línea de forma justificada
    for idx, linea in enumerate(lineas):
        es_ultima_linea = (idx == len(lineas) - 1)
        
        # Si es la última línea o solo tiene una palabra, se alinea de forma natural a la izquierda
        if es_ultima_linea or len(linea) == 1:
            texto_linea = ' '.join(linea)
            draw.text((x_inicio, y), texto_linea, fill=color, font=font)
        else:
            # Calcular el espacio exacto que ocupan los caracteres juntos (sin espacios intermedios)
            bbox_letras = draw.textbbox((0, 0), ''.join(linea), font=font)
            ancho_letras = bbox_letras[2] - bbox_letras[0]
            
            # Repartir equitativamente el espacio en blanco sobrante
            espacio_disponible = ancho_maximo - ancho_letras
            espacio_entre_palabras = espacio_disponible / (len(linea) - 1)
            
            x_cursor = x_inicio
            for i, palabra in enumerate(linea):
                draw.text((x_cursor, y), palabra, fill=color, font=font)
                bbox_p = draw.textbbox((0, 0), palabra, font=font)
                ancho_p = bbox_p[2] - bbox_p[0]
                x_cursor += ancho_p + espacio_entre_palabras
                
        y += interlineado
        
    return y

def crear_tarjeta_perfecta(nombre, carrera):
    # Lienzo de alta resolución e institucional
    ancho, alto = 750, 850
    imagen = Image.new("RGB", (ancho, alto), "#FFFFFF")
    draw = ImageDraw.Draw(imagen)
    
    # Carga de fuentes garantizadas desde Google Fonts
    f_titulo = cargar_fuente_web(True, 30)         
    f_subtitulo = cargar_fuente_web(False, 14)   
    f_cuerpo_bold = cargar_fuente_web(True, 20)    
    f_cuerpo = cargar_fuente_web(False, 17)       
    f_eslogan = cargar_fuente_web(True, 25)        
    f_pie_tit = cargar_fuente_web(True, 13)        
    f_pie_sub = cargar_fuente_web(True, 15)        
    f_pie_univ = cargar_fuente_web(False, 13)    

    # 1. Encabezado Azul Premium
    draw.rectangle([0, 0, ancho, 155], fill="#1B365D")
    draw.text((ancho // 2, 55), f"¡Feliz Cumpleaños, {nombre.upper()}!🎂🎉", fill="#FFFFFF", font=f_titulo, anchor="mm")
    
    texto_carrera = f"Egresado(a) de la Carrera Profesional de {carrera.upper()}"
    if len(texto_carrera) > 68:
        draw.text((ancho // 2, 110), texto_carrera[:65] + "...", fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    else:
        draw.text((ancho // 2, 110), texto_carrera, fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    
    # 2. Cuerpo del Mensaje con Justificado Impecable
    draw.text((50, 195), "Estimado(a) egresado(a),", fill="#1E293B", font=f_cuerpo_bold)
    
    parrafo_1 = "Hoy es un día muy especial, y desde la Unidad de Seguimiento al Egresado y Bolsa de Trabajo queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños."
    parrafo_2 = "Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra comunidad de graduados. Deseamos que pases un día extraordinario junto a tus seres queridos y que este nuevo año esté lleno de salud, felicidad y grandes éxitos profesionales."
    
    # Ejecutar la justificación avanzada restringiendo el texto al espacio libre (ancho máximo de 430px)
    proxima_y = dibujar_texto_justificado(draw, parrafo_1, x_inicio=50, y_inicio=240, ancho_maximo=430, font=f_cuerpo, interlineado=30)
    dibujar_texto_justificado(draw, parrafo_2, x_inicio=50, y_inicio=proxima_y + 15, ancho_maximo=430, font=f_cuerpo, interlineado=30)
        
    # Mensaje de Cierre
    draw.text((ancho // 2, 705), "¡Que disfrutes mucho de tu día!", fill="#1B365D", font=f_eslogan, anchor="mm")
    
    # 3. Pie de Página Institucional
    draw.rectangle([0, alto - 115, ancho, alto], fill="#0B1D33")
    draw.text((ancho // 2, alto - 85), "ATENTAMENTE,", fill="#38BDF8", font=f_pie_tit, anchor="mm")
    draw.text((ancho // 2, alto - 60), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", font=f_pie_sub, anchor="mm")
    draw.text((ancho // 2, alto - 35), "Universidad Nacional Amazónica de Madre de Dios", fill="#94A3B8", font=f_pie_univ, anchor="mm")
    
    # 4. Inserción de la Mascota Jaguar (Perfectamente integrada a la derecha)
    try:
        id_drive = "10fW68y7oiTcr-VcPoEW1V-OQ4O3psxup"
        url_mascota = f"https://docs.google.com/uc?export=download&id={id_drive}"
        res_img = requests.get(url_mascota, timeout=10)
        img_mascota = Image.open(io.BytesIO(res_img.content)).convert("RGBA")
        img_mascota = img_mascota.resize((210, 240)) 
        imagen.paste(img_mascota, (505, 235), img_mascota) 
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
            
            imagen_tarjeta = crear_tarjeta_perfecta(nombre_egresado, carrera_profesional)
            
            buf = io.BytesIO()
            imagen_tarjeta.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                st.image(imagen_tarjeta, use_container_width=True, caption=f"Tarjeta Oficial - {nombre_egresado}")
                
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
