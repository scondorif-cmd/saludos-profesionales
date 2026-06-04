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
            
            # Conversión de tu enlace de Google Drive a descarga directa e idónea para HTML
            id_drive = "10fW68y7oiTcr-VcPoEW1V-OQ4O3psxup"
            url_mascota_directa = f"https://lh3.googleusercontent.com/d/{id_drive}"
            
            # --- ESTRUCTURA DE TABLA FIJA (Mantiene las proporciones exactas de Tarjeta_SHANIRA.png) ---
            html_tarjeta = f"""
            <div style="display: flex; justify-content: center; background-color: #F8FAFC; padding: 10px;">
                <table width="550" cellspacing="0" cellpadding="0" style="background-color: #FFFFFF; font-family: 'Arial', sans-serif; border: 1px solid #CBD5E1; border-collapse: collapse; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    
                    <tr>
                        <td bgcolor="#1B365D" align="center" style="padding: 25px 20px; border-bottom: 3px solid #1E3A8A;">
                            <h2 style="color: #FFFFFF; margin: 0; font-size: 24px; font-weight: bold; line-height: 1.3; font-family: 'Arial', sans-serif;">¡Feliz Cumpleaños, {nombre_egresado}! 🎂🎉</h2>
                            <p style="color: #E2E8F0; margin: 6px 0 0 0; font-size: 13px; font-weight: normal; font-family: 'Arial', sans-serif;">Egresado(a) de la Carrera Profesional de {carrera_profesional.upper()}</p>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding: 25px 25px 15px 25px; bgcolor: #FFFFFF;">
                            <table width="100%" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td valign="top" style="color: #334155; font-size: 14px; line-height: 1.6; text-align: justify; font-family: 'Arial', sans-serif;">
                                        <p style="color: #1E293B; font-weight: bold; font-size: 16px; margin: 0 0 12px 0;">Estimado(a) egresado(a),</p>
                                        <p style="margin: 0 0 12px 0;">Hoy es un día muy especial, y desde la <strong>Unidad de Seguimiento al Egresado y Bolsa de Trabajo</strong> queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños.</p>
                                        <p style="margin: 0 0 15px 0;">Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra comunidad de graduados. Deseamos que pases un día extraordinario junto a tus seres queridos y que este nuevo año esté lleno de salud, felicidad y grandes éxitos profesionales.</p>
                                    </td>
                                    
                                    <td width="140" valign="top" align="right" style="padding-left: 15px;">
                                        <img src="{url_mascota_directa}" width="130" style="display: block; min-height: 150px;" alt="Mascota UNAMAD">
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <tr>
                        <td align="center" style="padding: 10px 20px 25px 20px; bgcolor: #FFFFFF;">
                            <h4 style="color: #1B365D; margin: 0; font-size: 18px; font-weight: bold; font-family: 'Arial', sans-serif;">¡Que disfrutes mucho de tu día!</h4>
                        </td>
                    </tr>
                    
                    <tr>
                        <td bgcolor="#0B1D33" align="center" style="padding: 20px 15px; color: #FFFFFF; font-size: 11px; line-height: 1.5; font-family: 'Arial', sans-serif;">
                            <span style="color: #38BDF8; font-weight: bold; letter-spacing: 0.5px; display: block; margin-bottom: 4px;">ATENTAMENTE,</span>
                            <strong style="display: block; font-size: 13px; color: #FFFFFF;">Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA</strong>
                            <span style="color: #94A3B8; display: block; margin-top: 2px;">Universidad Nacional Amazónica de Madre de Dios</span>
                        </td>
                    </tr>
                </table>
            </div>
            """
            
            # Mostrar la interfaz organizada de Streamlit
            col1, col2 = st.columns([1.3, 1.0])
            with col1:
                # Renderizador HTML con dimensiones bloqueadas
                st.components.v1.html(html_tarjeta, height=560, scrolling=False)
                st.caption("📸 *Toma una captura de pantalla a la tarjeta para enviarla nítida y con las proporciones correctas.*")
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
