import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
import io

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

def generar_tarjeta_html(nombre, carrera):
    """Genera una tarjeta corporativa perfecta usando HTML/CSS libre de errores de codificación"""
    url_mascota = "https://docs.google.com/uc?export=download&id=10fW68y7oiTcr-VcPoEW1V-OQ4O3psxup"
    
    html_content = f"""
    <div style="
        background-color: #FFFFFF; 
        border-radius: 12px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.15); 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        overflow: hidden; 
        max-width: 550px; 
        margin: 10px auto; 
        border: 1px solid #E2E8F0;
    ">
        <div style="background: linear-gradient(135deg, #1B365D 0%, #0B1D33 100%); padding: 30px 20px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 0.5px;">¡Feliz Cumpleaños, {nombre.upper()}!</h2>
            <p style="margin: 8px 0 0 0; color: #E2E8F0; font-size: 13px; font-style: italic;">Egresado(a) de la Carrera Profesional de {carrera.upper()}</p>
        </div>
        
        <div style="padding: 25px; position: relative;">
            <p style="color: #1E293B; font-weight: bold; font-size: 16px; margin-top: 0;">Estimado(a) egresado(a),</p>
            
            <div style="display: flex; gap: 15px; align-items: flex-start;">
                <div style="color: #334155; font-size: 14px; line-height: 1.6; text-align: justify; flex: 1;">
                    Hoy es un día muy especial, y desde la <strong>Unidad de Seguimiento al Egresado y Bolsa de Trabajo</strong> queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños.<br><br>
                    Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra comunidad de graduados. Deseamos que pases un día extraordinario junto a tus seres queridos y que este nuevo año esté lleno de salud, felicidad y grandes éxitos profesionales.
                </div>
                <div style="width: 110px; text-align: center; flex-shrink: 0;">
                    <img src="{url_mascota}" style="width: 100%; height: auto; border-radius: 8px;" alt="Mascota UNAMAD">
                </div>
            </div>
            
            <h3 style="color: #1B365D; text-align: center; margin: 25px 0 5px 0; font-size: 18px; font-weight: 700;">¡Que disfrutes mucho de tu día!</h3>
        </div>
        
        <div style="background-color: #0B1D33; padding: 15px 20px; text-align: center; color: white; font-size: 11px; line-height: 1.4;">
            <span style="color: #38BDF8; font-weight: bold; letter-spacing: 1px;">ATENTAMENTE,</span><br>
            <span style="color: #FFFFFF; font-weight: 600;">Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA</span><br>
            <span style="color: #94A3B8;">Universidad Nacional Amazónica de Madre de Dios</span>
        </div>
    </div>
    """
    return html_content

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
            
            # Despliegue en columnas de Streamlit
            col1, col2 = st.columns([1.3, 1.0])
            with col1:
                # Renderizar la tarjeta impecable usando el motor HTML seguro de Streamlit
                tarjeta_html = generar_tarjeta_html(nombre_egresado, carrera_profesional)
                st.markdown(tarjeta_html, unsafe_allow_html=True)
                st.caption(f"Visualización de Tarjeta Oficial para {nombre_egresado}")
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:14px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;">💬 Enviar Saludo y Tarjeta por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
