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
            
            # Texto oficial para el Portapapeles/WhatsApp (¡Con ortografía perfecta!)
            texto_saludo_oficial = (
                f"¡FELIZ CUMPLEAÑOS, {nombre_egresado.upper()}! 🎂🎉\n"
                f"Egresado(a) de la Carrera Profesional de {carrera_profesional.upper()}\n\n"
                f"Estimado(a) egresado(a),\n\n"
                f"Hoy es un día muy especial, y desde la Unidad de Seguimiento al Egresado y "
                f"Bolsa de Trabajo queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños.\n\n"
                f"Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra "
                f"comunidad de graduados. Deseamos que pases un día extraordinario junto a tus seres "
                f"queridos y que este nuevo año esté lleno de salud, felicidad y grandes éxitos profesionales.\n\n"
                f"¡Que disfrutes mucho de tu día! ✨🎈\n\n"
                f"ATENTAMENTE,\n"
                f"Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA\n"
                f"Universidad Nacional Amazónica de Madre de Dios"
            )
            
            texto_codificado = urllib.parse.quote(texto_saludo_oficial)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            # Interfaz dividida limpia y ejecutada nativamente por Streamlit
            col1, col2 = st.columns([1.2, 1.0])
            
            with col1:
                # Cuadro de diseño visual simulado con Markdown nativo (Soporta tildes y eñes al 100%)
                st.markdown(
                    f"""
                    <div style="background-color: #1B365D; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; color: white;">
                        <h3 style="margin:0; font-size: 20px;">¡Feliz Cumpleaños, {nombre_egresado.upper()}!</h3>
                        <p style="margin:5px 0 0 0; font-size: 12px; color: #E2E8F0;">{carrera_profesional}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Cuerpo intermedio que incluye la mascota de Google Drive de manera directa
                subcol_txt, subcol_img = st.columns([2, 1])
                with subcol_txt:
                    st.write("")
                    st.markdown("**Estimado(a) egresado(a),**")
                    st.caption("Hoy es un día muy especial, y desde la Unidad de Seguimiento al Egresado y Bolsa de Trabajo queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños.")
                with subcol_img:
                    url_mascota = "https://docs.google.com/uc?export=download&id=10fW68y7oiTcr-VcPoEW1V-OQ4O3psxup"
                    st.image(url_mascota, width=110)
                
                st.markdown("<p style='text-align:center; color:#1B365D; font-weight:bold; margin:10px 0;'>¡Que disfrutes mucho de tu día!</p>", unsafe_allow_html=True)
                
                # Bloque inferior del diseño
                st.markdown(
                    """
                    <div style="background-color: #0B1D33; padding: 10px; border-radius: 0 0 10px 10px; text-align: center; color: #94A3B8; font-size: 11px;">
                        <span style="color: #38BDF8; font-weight: bold;">ATENTAMENTE</span><br>
                        Unidad de Seguimiento al Egresado y Bolsa de Trabajo<br>
                        <span style="font-size: 9px;">Universidad Nacional Amazónica de Madre de Dios</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # BLOQUE CLAVE: Cuadro con el texto oficial y el botón nativo "Copy" de Streamlit
                st.write("")
                st.subheader("📋 Texto de la Tarjeta Oficial:")
                st.code(texto_saludo_oficial, language="text")
                st.caption("💡 Haz clic en el icono de copiar del recuadro gris de arriba antes de ir a WhatsApp.")
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(f"📱 **Celular:** {celular_celda}\n\nEl saludo se abrirá con el formato institucional completo en WhatsApp.")
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:15px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💬 Abrir Chat y Pegar Saludo</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
