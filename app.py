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
st.write("Generación de tarjetas institucionales con descarga en alta calidad.")

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
    # Crear un lienzo en alta definición con el fondo exacto
    ancho, alto = 800, 950
    imagen = Image.new("RGB", (ancho, alto), "#FFFFFF")
    draw = ImageDraw.Draw(imagen)
    
    # 1. Franja Azul Superior
    draw.rectangle([0, 0, ancho, 180], fill="#1B365D")
    
    # 2. Franja Azul Inferior
    draw.rectangle([0, alto - 150, ancho, alto], fill="#0B1D33")
    
    # Intentar cargar fuentes predeterminadas seguras para evitar errores del servidor
    try:
        fuente_titulo = ImageFont.load_default()
    except:
        fuente_titulo = None

    # Dibujar Textos Básicos y Estructuras de la Tarjeta de forma limpia
    # Encabezado
    draw.text((400, 50), f"¡Feliz Cumpleaños, {nombre.upper()}! 🎂🎉", fill="#FFFFFF", anchor="mm")
    draw.text((400, 110), f"Egresado(a) de la Carrera Profesional de {carrera.upper()}", fill="#E2E8F0", anchor="mm")
    
    # Cuerpo del Mensaje
    draw.text((50, 230), "Estimado(a) egresado(a),", fill="#1E293B")
    
    lineas_mensaje = [
        "Hoy es un día muy especial, y desde la Unidad de Seguimiento al Egresado",
        "y Bolsa de Trabajo queremos hacerte llegar nuestras más sinceras",
        "felicitaciones por tu cumpleaños.",
        "",
        "Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo",
        "de nuestra comunidad de graduados. Deseamos que pases un día",
        "extraordinario junto a tus seres queridos y que este nuevo año esté",
        "lleno de salud, felicidad y grandes éxitos profesionales."
    ]
    
    y_ini = 290
    for linea in lineas_mensaje:
        draw.text((50, y_ini), linea, fill="#334155")
        y_ini += 35
        
    draw.text((400, 680), "¡Que disfrutes mucho de tu día!", fill="#1B365D", anchor="mm")
    
    # Pie de página Institucional
    draw.text((400, alto - 110), "ATENTAMENTE,", fill="#38BDF8", anchor="mm")
    draw.text((400, alto - 80), "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA", fill="#FFFFFF", anchor="mm")
    draw.text((400, alto - 50), "Universidad Nacional Amazónica de Madre de Dios", fill="#CBD5E1", anchor="mm")
    
    # 3. Superponer Mascota desde el repositorio oficial de GitHub
    try:
        url_mascota = "https://raw.githubusercontent.com/scondorif-cmd/saludos-profesionales/principal/mascota.png"
        res_img = requests.get(url_mascota)
        img_mascota = Image.open(io.BytesIO(res_img.content)).convert("RGBA")
        img_mascota = img_mascota.resize((160, 180))
        # Posicionar de forma exacta a la derecha del contenido
        imagen.paste(img_mascota, (580, 240), img_mascota)
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
            
            # Formatear texto para WhatsApp
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            # Generar la imagen sólida de la tarjeta
            imagen_tarjeta = crear_tarjeta_imagen(nombre_egresado, carrera_profesional)
            
            # Convertir a bytes para descarga directa
            buf = io.BytesIO()
            imagen_tarjeta.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            # Mostrar interfaz limpia en dos columnas estables
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                st.image(imagen_tarjeta, use_container_width=True, caption=f"Vista previa de la Tarjeta Oficial de {nombre_egresado}")
                
                # --- BOTÓN DE DESCARGA DIRECTA DE LA IMAGEN EN .PNG ---
                st.download_button(
                    label=f"📥 Descargar Imagen PNG ({nombre_egresado})",
                    data=byte_im,
                    file_name=f"Tarjeta_{nombre_egresado.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"btn_png_{index}"
                )
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:15px;">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
