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
            
            # --- DISEÑO DIGITAL MAQUETADO EN HTML INYECTADO ---
            html_tarjeta = f"""
            <div style="background-color: #F8FAFC; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 100%; max-width: 600px; font-family: 'Segoe UI', Arial, sans-serif; overflow: hidden; margin: 15px auto; border: 1px solid #E2E8F0;">
                <div style="background-color: #1B365D; padding: 30px 20px; text-align: center;">
                    <h2 style="color: #FFFFFF; margin: 0; font-size: 26px; font-weight: 700; line-height: 1.3;">¡Feliz Cumpleaños, {nombre_egresado}! 🎂🎉</h2>
                    <p style="color: #E2E8F0; margin: 10px 0 0 0; font-size: 15px; font-weight: 400;">Egresado(a) de la Carrera Profesional de {carrera_profesional.upper()}</p>
                </div>
                
                <div style="padding: 30px 25px; background-color: #FFFFFF; position: relative;">
                    <div style="float: right; margin-left: 20px; margin-bottom: 10px; width: 140px;">
                        <img src="https://raw.githubusercontent.com/scondorif-cmd/saludos-profesionales/principal/mascota.png" style="width: 100%; height: auto; display: block;" alt="Mascota">
                    </div>
                    
                    <p style="color: #1E293B; font-weight: 700; font-size: 17px; margin: 0 0 16px 0;">Estimado(a) egresado(a),</p>
                    
                    <p style="color: #334155; font-size: 15px; line-height: 1.6; margin: 0 0 16px 0; text-align: justify;">
                        Hoy es un día muy especial, y desde la <strong style="color: #1E293B;">Unidad de Seguimiento al Egresado y Bolsa de Trabajo</strong> queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños.
                    </p>
                    
                    <p style="color: #334155; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0; text-align: justify;">
                        Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra comunidad de graduados. Deseamos que pases un día extraordinario junto a tus seres queridos y que este nuevo año esté lleno de salud, felicidad y grandes éxitos profesionales.
                    </p>
                    
                    <div style="clear: both;"></div>
                    
                    <h4 style="color: #1B365D; text-align: center; font-size: 19px; font-weight: 700; margin: 25px 0 5px 0;">¡Que disfrutes mucho de tu día!</h4>
                </div>
                
                <div style="background-color: #0B1D33; padding: 22px 20px; text-align: center; color: #FFFFFF; font-size: 13px; line-height: 1.5;">
                    <span style="color: #38BDF8; font-weight: 700; letter-spacing: 1px; display: block; margin-bottom: 5px;">ATENTAMENTE,</span>
                    <strong style="display: block; font-size: 14px; color: #FFFFFF;">Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA</strong>
                    <span style="color: #CBD5E1; display: block; margin-top: 3px; font-size: 12px;">Universidad Nacional Amazónica de Madre de Dios</span>
                </div>
            </div>
            """
            
            with st.container():
                # Desplegar la tarjeta de forma directa y limpia en la interfaz
                st.components.v1.html(html_tarjeta, height=580, scrolling=False)
                
                # Botón de envío directo
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; max-width:600px; margin:10px auto; display:block; cursor:pointer; font-size:16px;">💬 Enviar por WhatsApp a {nombre_egresado}</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
