import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
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
            
            # Formatear texto para WhatsApp
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}" if num_limpio and num_limpio != "nan" else f"https://api.whatsapp.com/send?text={texto_codificado}"
            
            # --- CARD MAQUETADA CON COLOR IGUALADO A LA IMAGEN (Fondo #F0F4F8) ---
            html_tarjeta = f"""
            <div style="background-color: #F0F4F8; border-radius: 4px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); width: 100%; max-width: 600px; font-family: 'Segoe UI', Arial, sans-serif; overflow: hidden; margin: 10px auto; border: 1px solid #D1D5DB;">
                <div style="background-color: #1B365D; padding: 25px 20px; text-align: center;">
                    <h2 style="color: #FFFFFF; margin: 0; font-size: 25px; font-weight: 700; line-height: 1.3;">¡Feliz Cumpleaños, {nombre_egresado}! 🎂🎉</h2>
                    <p style="color: #E2E8F0; margin: 8px 0 0 0; font-size: 14px; font-weight: 400;">Egresado(a) de la Carrera Profesional de {carrera_profesional.upper()}</p>
                </div>
                
                <div style="padding: 30px 25px; background-color: #F0F4F8; position: relative;">
                    <div style="float: right; margin-left: 15px; margin-bottom: 10px; width: 135px;">
                        <img src="https://lh3.googleusercontent.com/d/10fW68y7oiTcr-VcPoEW1V-OQ4O3psxup" style="width: 100%; height: auto; display: block;" alt="Mascota">
                    </div>
                    
                    <p style="color: #1E293B; font-weight: 700; font-size: 16px; margin: 0 0 14px 0;">Estimado(a) egresado(a),</p>
                    
                    <p style="color: #334155; font-size: 15px; line-height: 1.6; margin: 0 0 14px 0; text-align: justify;">
                        Hoy es un día muy especial, y desde la <strong>Unidad de Seguimiento al Egresado y Bolsa de Trabajo</strong> queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños.
                    </p>
                    
                    <p style="color: #334155; font-size: 15px; line-height: 1.6; margin: 0 0 15px 0; text-align: justify;">
                        Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra comunidad de graduados. Deseamos que pases un día extraordinario junto a tus seres queridos y que este nuevo año esté lleno de salud, felicidad y grandes éxitos profesionales.
                    </p>
                    
                    <div style="clear: both;"></div>
                    
                    <h4 style="color: #1B365D; text-align: center; font-size: 18px; font-weight: 700; margin: 25px 0 5px 0;">¡Que disfrutes mucho de tu día!</h4>
                </div>
                
                <div style="background-color: #0B1D33; padding: 20px; text-align: center; color: #FFFFFF; font-size: 12px; line-height: 1.5;">
                    <span style="color: #38BDF8; font-weight: 700; letter-spacing: 1px; display: block; margin-bottom: 5px;">ATENTAMENTE,</span>
                    <strong style="display: block; font-size: 13px; color: #FFFFFF;">Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA</strong>
                    <span style="color: #CBD5E1; display: block; margin-top: 3px;">Universidad Nacional Amazónica de Madre de Dios</span>
                </div>
            </div>
            """
            
            with st.container():
                col1, col2 = st.columns([1.3, 1.0])
                with col1:
                    # Desplegar tarjeta impecable
                    st.components.v1.html(html_tarjeta, height=560, scrolling=False)
                    
                    # --- BOTÓN DE GUARDAR IMAGEN / ACCIÓN ---
                    st.markdown('''
                        <button onclick="window.print();" style="background-color:#6366F1; color:white; border:none; padding:10px 18px; font-weight:bold; border-radius:6px; width:100%; max-width:600px; margin-top:5px; cursor:pointer; font-size:14px; display:flex; align-items:center; justify-content:center; gap:8px;">
                            💾 Guardar / Capturar Tarjeta
                        </button>
                    ''', unsafe_allow_html=True)
                    
                with col2:
                    st.markdown(f"### 🥳 {nombre_egresado}")
                    st.info(texto_whatsapp)
                    st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:15px;">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
