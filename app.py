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

def generar_imagen_tarjeta(nombre, carrera, es_varon):
    # Dimensiones exactas para el diseño HD original
    ancho, alto = 1200, 1050
    img = Image.new('RGB', (ancho, alto), color='#F8FAFC')
    draw = ImageDraw.Draw(img)
    
    # Paleta de colores exacta de tu diseño original
    color_cabecera = "#1B365D"
    color_pie = "#0B1D33"
    
    # Dibujar franjas (Cabecera y Pie)
    draw.rectangle([0, 0, ancho, 220], fill=color_cabecera)
    draw.rectangle([0, alto-160, ancho, alto], fill=color_pie)
    
    # Carga de fuentes segura y compatible con Linux Streamlit (Grande y Elegante)
    try:
        font_titulo = ImageFont.truetype("LiberationSans-Bold.ttf", 46)
        font_sub = ImageFont.truetype("LiberationSans-Regular.ttf", 26)
        font_cuerpo_bold = ImageFont.truetype("LiberationSans-Bold.ttf", 32)
        font_cuerpo_reg = ImageFont.truetype("LiberationSans-Regular.ttf", 30)
        font_pie_bold = ImageFont.truetype("LiberationSans-Bold.ttf", 24)
        font_pie_reg = ImageFont.truetype("LiberationSans-Regular.ttf", 22)
    except:
        font_titulo = font_sub = font_cuerpo_bold = font_cuerpo_reg = font_pie_bold = font_pie_reg = ImageFont.load_default()

    # --- TEXTOS DE LA CABECERA (Centrados perfectamente) ---
    texto_titulo = f"¡Feliz Cumpleaños, {nombre}! 🎂🎉"
    w_t = draw.textlength(texto_titulo, font=font_titulo)
    draw.text(((ancho - w_t) / 2, 50), texto_titulo, fill="#FFFFFF", font=font_titulo)
    
    texto_sub = f"Egresado(a) de la Carrera Profesional de {carrera.upper()}"
    w_s = draw.textlength(texto_sub, font=font_sub)
    draw.text(((ancho - w_s) / 2, 135), texto_sub, fill="#E2E8F0", font=font_sub)
    
    # --- TEXTO DEL CUERPO (Alineado a la izquierda con margen) ---
    draw.text((70, 290), "Estimado(a) egresado(a),", fill="#1E293B", font=font_cuerpo_bold)
    
    # Párrafo principal estructurado línea por línea
    draw.text((70, 370), "Hoy es un día muy especial, y desde la ", fill="#334155", font=font_cuerpo_reg)
    w_p1 = draw.textlength("Hoy es un día muy especial, y desde la ", font=font_cuerpo_reg)
    draw.text((70 + w_p1, 370), "Unidad de", fill="#1E293B", font=font_cuerpo_bold)
    
    draw.text((70, 420), "Seguimiento al Egresado y Bolsa de Trabajo", fill="#1E293B", font=font_cuerpo_bold)
    w_p2 = draw.textlength("Seguimiento al Egresado y Bolsa de Trabajo ", font=font_cuerpo_bold)
    draw.text((70 + w_p2, 420), "queremos", fill="#334155", font=font_cuerpo_reg)
    
    draw.text((70, 470), "hacerte llegar nuestras más sinceras felicitaciones por tu", fill="#334155", font=font_cuerpo_reg)
    draw.text((70, 520), "cumpleaños.", fill="#334155", font=font_cuerpo_reg)
    
    draw.text((70, 610), "Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de", fill="#334155", font=font_cuerpo_reg)
    draw.text((70, 660), "nuestra comunidad de graduados. Deseamos que pases un día extraordinario", fill="#334155", font=font_cuerpo_reg)
    draw.text((70, 710), "junto a tus seres queridos y que este nuevo año esté lleno de salud, felicidad y", fill="#334155", font=font_cuerpo_reg)
    draw.text((70, 760), "grandes éxitos profesionales.", fill="#334155", font=font_cuerpo_reg)
    
    # --- MENSAJE FINAL DESTACADO (Centrado) ---
    texto_disfruta = "¡Que disfrutes mucho de tu día!"
    w_d = draw.textlength(texto_disfruta, font=font_cuerpo_bold)
    draw.text(((ancho - w_d) / 2, 840), texto_disfruta, fill="#1B365D", font=font_cuerpo_bold)
    
    # --- PIE DE PÁGINA (Centrado) ---
    txt_atentamente = "ATENTAMENTE,"
    w_a = draw.textlength(txt_atentamente, font=font_pie_bold)
    draw.text(((ancho - w_a) / 2, alto - 130), txt_atentamente, fill="#38BDF8", font=font_pie_bold)
    
    txt_unidad = "Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA"
    w_u = draw.textlength(txt_unidad, font=font_pie_bold)
    draw.text(((ancho - w_u) / 2, alto - 95), txt_unidad, fill="#FFFFFF", font=font_pie_bold)
    
    txt_uni = "Universidad Nacional Amazónica de Madre de Dios"
    w_uni = draw.textlength(txt_uni, font=font_pie_reg)
    draw.text(((ancho - w_uni) / 2, alto - 55), txt_uni, fill="#CBD5E1", font=font_pie_reg)
    
    # --- INTENTAR CARGAR LA MASCOTA DESDE REPOSITORIO EXTERNO ---
    try:
        # Usamos la imagen oficial de tu jaguar cargada de manera segura
        url_mascota = "https://raw.githubusercontent.com/scondorif-cmd/saludos-profesionales/principal/mascota.png"
        res_mascota = requests.get(url_mascota, timeout=5)
        if res_mascota.status_code == 200:
            img_mascota = Image.open(io.BytesIO(res_mascota.content)).convert("RGBA")
            img_mascota = img_mascota.resize((260, 260))  # Tamaño proporcional original
            img.paste(img_mascota, (870, 270), img_mascota) # Posición lateral derecha exacta
    except:
        pass # Si no existe o no conecta, la tarjeta se genera limpia sin romperse
        
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
