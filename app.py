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

def conseguir_fuente_servidor(es_bold, tamano):
    """Busca de forma exhaustiva fuentes con soporte latino nativo en Linux (Streamlit Cloud)"""
    
    # Lista de rutas absolutas de fuentes del sistema Linux de Streamlit que SÍ soportan Ñ y tildes
    rutas_fuentes = [
        # Ruta estándar de DejaVu (Excelente soporte latino)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if es_bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # Ruta alternativa de Liberation (Soporte latino garantizado)
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if es_bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Segunda ruta alternativa de DejaVu en algunas distros Linux minimalistas
        "/usr/share/fonts/fonts-dejavu/DejaVuSans-Bold.ttf" if es_bold else "/usr/share/fonts/fonts-dejavu/DejaVuSans.ttf"
    ]
    
    for ruta in rutas_fuentes:
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, tamano)
            except:
                continue

    # Si el servidor no tiene las rutas anteriores, descargamos directo una fuente latina estándar de respaldo
    nombre_local = "backup_bold.ttf" if es_bold else "backup_reg.ttf"
    if not os.path.exists(nombre_local):
        try:
            url_font = "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Bold.ttf" if es_bold else "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf"
            r = requests.get(url_font, timeout=5)
            with open(nombre_local, "wb") as f:
                f.write(r.content)
        except:
            pass

    if os.path.exists(nombre_local):
        try:
            return ImageFont.truetype(nombre_local, tamano)
        except:
            pass
                
    # Último recurso del sistema (Pillow cargará su fuente por defecto si todo lo demás falla)
    try:
        return ImageFont.load_default(size=tamano)
    except:
        return ImageFont.load_default()

def crear_tarjeta_perfecta(nombre, carrera):
    # Dimensiones exactas (750 x 850)
    ancho, alto = 750, 850
    imagen = Image.new("RGB", (ancho, alto), "#FFFFFF")
    draw = ImageDraw.Draw(imagen)
    
    # === FUENTES DE ALTA RESOLUCIÓN Y GROSOR ===
    f_titulo = conseguir_fuente_servidor(True, 30)         # Nombre arriba
    f_subtitulo = conseguir_fuente_servidor(False, 15)     # Carrera profesional
    f_cuerpo_bold = conseguir_fuente_servidor(True, 22)    # "Estimado(a) egresado(a),"
    f_cuerpo = conseguir_fuente_servidor(False, 19)       # Texto de felicitación
    f_eslogan = conseguir_fuente_servidor(True, 25)        # ¡Que disfrutes mucho de tu día!
    f_pie_tit = conseguir_fuente_servidor(True, 14)        # ATENTAMENTE,
    f_pie_sub = conseguir_fuente_servidor(True, 15)        # Unidad de Seguimiento...
    f_pie_univ = conseguir_fuente_servidor(False, 13)      # Universidad Nacional...

    # 1. Banner Superior Azul Institucional
    draw.rectangle([0, 0, ancho, 155], fill="#1B365D")
    
    # Asegurando el texto del título en variables limpias
    titulo_saludo = f"\u00A1Feliz Cumplea\u00F1os, {nombre.upper()}!"  # Usa códigos Unicode nativos para ¡ y Ñ
    draw.text((ancho // 2, 55), titulo_saludo, fill="#FFFFFF", font=f_titulo, anchor="mm")
    
    texto_carrera = f"Egresado(a) de la Carrera Profesional de {carrera.upper()}"
    if len(texto_carrera) > 68:
        draw.text((ancho // 2, 110), texto_carrera[:65] + "...", fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    else:
        draw.text((ancho // 2, 110), texto_carrera, fill="#E2E8F0", font=f_subtitulo, anchor="mm")
    
    # 2. Cuerpo del Mensaje Justificado y con Ortografía Perfecta
    draw.text((50, 205), "Estimado(a) egresado(a),", fill="#1E293B", font=f_cuerpo_bold)
    
    # Renglones estructurados sin caracteres conflictivos directos
    lineas = [
        "Hoy es un d\u00EDa muy especial, y desde la", # d\u00EDa = día
        "Unidad de Seguimiento al Egresado y",
        "Bolsa de Trabajo queremos hacerte llegar",
        "nuestras m\u00E1s sinceras felicitaciones por", # m\u00E1s = más
        "tu cumplea\u00F1os.", # cumplea\u00F1os = cumpleaños
        "",
        "Nos sentimos muy orgullosos de tus pasos y",
        "de tenerte como miembro activo de nuestra",
        "comunidad de graduados. Deseamos que",
        "pases un d\u00EDa extraordinario junto a tus seres",
        "queridos y que este nuevo a\u00F1o est\u00E9 lleno de", # a\u00F1o est\u00E9 = año esté
        "salud, felicidad y grandes \u00E9xitos profesionales." # \u00E9xitos = éxitos
    ]
    
    y_linea = 260
    for linea in lineas:
        draw.text((50, y_linea), linea, fill="#334155", font=f_cuerpo)
        y_linea += 36  
        
    # Mensaje de Cierre destacado abajo usando Unicode Seguro
    cierre_texto = "\u00A1Que disfrutes mucho de tu d\u00EDa!" # ¡Que disfrutes mucho de tu día!
    draw.text((ancho // 2, 705), cierre_texto, fill="#1B365D", font=f_eslogan, anchor="mm")
    
    # 3. Bloque Inferior del Pie de Página (Azul Oscuro con ortografía limpia)
    draw.rectangle([0, alto - 115, ancho, alto], fill="#0B1D33")
    draw.text((ancho // 2, alto - 85), "ATENTAMENTE,", fill="#38BDF8", font=f_pie_tit, anchor="mm")
    draw.text((ancho // 2, alto - 60), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", font=f_pie_sub, anchor="mm")
    draw.text((ancho // 2, alto - 35), "Universidad Nacional Amaz\u00F3nica de Madre de Dios", fill="#94A3B8", font=f_pie_univ, anchor="mm") # Amaz\u00F3nica
    
    # 4. Integración de la Mascota Jaguar (Desde tu Google Drive)
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
            
            # Generar tarjeta final usando el motor interno corregido
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
