import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
import io
import streamlit.components.v1 as components

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
    # Forzar la lectura limpia del binario de Excel para evitar conflictos de caracteres heredados
    oficina_df = pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)
    return oficina_df

def generar_tarjeta_html(nombre, carrera, index):
    """Genera la tarjeta con un diseño institucional optimizado usando un emblema CSS nativo"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            body {{ margin: 0; padding: 5px; font-family: 'Segoe UI', Arial, sans-serif; background-color: #F8FAFC; }}
            .tarjeta-contenedor {{
                background-color: #FFFFFF; 
                border-radius: 12px; 
                box-shadow: 0 8px 20px rgba(0,0,0,0.15); 
                overflow: hidden; 
                max-width: 480px; 
                margin: 0 auto; 
                border: 1px solid #E2E8F0;
            }}
            .banner-superior {{
                background: linear-gradient(135deg, #1B365D 0%, #0B1D33 100%); 
                padding: 25px 15px; 
                text-align: center; 
                color: white;
            }}
            .banner-superior h2 {{ margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }}
            .banner-superior p {{ margin: 8px 0 0 0; color: #38BDF8; font-size: 13px; font-weight: 600; text-transform: uppercase; }}
            .cuerpo {{ padding: 22px; }}
            .saludo {{ color: #1E293B; font-weight: bold; font-size: 15px; margin-top: 0; }}
            .contenido-flex {{ display: flex; gap: 15px; align-items: center; }}
            .texto-mensaje {{ color: #334155; font-size: 13.5px; line-height: 1.6; text-align: justify; flex: 1; }}
            
            /* Emblema Académico geométrico sustituto de la imagen */
            .insignia-academica {{
                width: 90px;
                height: 90px;
                background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
                border: 3px solid #1B365D;
                flex-shrink: 0;
            }}
            .insignia-icono {{ font-size: 32px; margin: 0; padding: 0; line-height: 1; }}
            .insignia-texto {{ color: #1B365D; font-size: 9px; font-weight: 800; margin-top: 2px; font-family: Arial, sans-serif; }}
            
            .eslogan {{ color: #1B365D; text-align: center; margin: 22px 0 5px 0; font-size: 16px; font-weight: 700; font-style: italic; }}
            .pie-pagina {{
                background-color: #0B1D33; 
                padding: 15px; 
                text-align: center; 
                color: white; 
                font-size: 11px; 
                line-height: 1.4;
                border-top: 2px solid #FFD700;
            }}
            .btn-copiar {{
                display: block;
                width: 100%;
                max-width: 480px;
                margin: 12px auto;
                background: linear-gradient(135deg, #1B365D 0%, #0B1D33 100%);
                color: white;
                border: 1px solid #38BDF8;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
                cursor: pointer;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>

        <div id="tarjeta-{index}" class="tarjeta-contenedor">
            <div class="banner-superior">
                <h2>¡Feliz Cumpleaños, {nombre.upper()}!</h2>
                <p>Carrera de {carrera.upper()}</p>
            </div>
            
            <div class="cuerpo">
                <p class="saludo">Estimado(a) egresado(a),</p>
                <div class="contenido-flex">
                    <div class="texto-mensaje">
                        Hoy es un día muy especial, y desde la <strong>Unidad de Seguimiento al Egresado y Bolsa de Trabajo</strong> queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños.<br><br>
                        Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra comunidad de graduados. Deseamos que este nuevo año esté lleno de salud, felicidad y grandes éxitos profesionales.
                    </div>
                    
                    <div class="insignia-academica">
                        <div class="insignia-icono">🎓</div>
                        <div class="insignia-texto">UNAMAD</div>
                    </div>
                </div>
                <div class="eslogan">¡Que disfrutes mucho de tu día!</div>
            </div>
            
            <div class="pie-pagina">
                <span style="color: #38BDF8; font-weight: bold; letter-spacing: 0.5px;">ATENTAMENTE,</span><br>
                <span style="color: #FFFFFF; font-weight: 600;">Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA</span><br>
                <span style="color: #94A3B8;">Universidad Nacional Amazónica de Madre de Dios</span>
            </div>
        </div>

        <button id="btn-copy-{index}" class="btn-copiar" onclick="copiarTarjeta()">📋 Descargar Tarjeta PNG</button>

        <script>
            function copiarTarjeta() {{
                const elemento = document.getElementById('tarjeta-{index}');
                const boton = document.getElementById('btn-copy-{index}');
                
                html2canvas(elemento, {{ scale: 2, logging: false }}).then(canvas => {{
                    canvas.toBlob(blob => {{
                        if(!blob) return;
                        const item = new ClipboardItem({{ "image/png": blob }});
                        navigator.clipboard.write([item]).then(() => {{
                            boton.innerText = "✅ ¡Tarjeta Copiada! Pégala en WhatsApp (Ctrl+V)";
                            boton.style.background = "#22C55E";
                            
                            setTimeout(() => {{
                                boton.innerText = "📋 Descargar Tarjeta PNG";
                                boton.style.background = "linear-gradient(135deg, #1B365D 0%, #0B1D33 100%)";
                            }}, 3000);
                        }}).catch(err => {{
                            alert("Permite el acceso al portapapeles si tu navegador lo solicita.");
                        }});
                    }}, 'image/png');
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_content

try:
    df = descargar_datos()
    st.success("✅ Conexión con la base de datos exitosa.")
    
    st.subheader(f"🎂 Cumpleañeros del día {dia_buscado}:")
    contador = 0
    
    for index, fila in df.iterrows():
        try:
            # Re-codificación manual preventiva para limpiar tildes y caracteres extraños de las celdas
            nombre_completo = str(fila[3]).encode('latin1', errors='ignore').decode('utf-8', errors='ignore').strip()       
            carrera_profesional = str(fila[4]).encode('latin1', errors='ignore').decode('utf-8', errors='ignore').strip()   
            fecha_celda = str(fila[43]).strip()          
            celular_celda = str(fila[7]).strip().replace(".0", "").replace(" ", "")
        except:
            # Si falla la codificación fina, procedemos con el string estándar limpio
            nombre_completo = str(fila[3]).strip()
            carrera_profesional = str(fila[4]).strip()
            fecha_celda = str(fila[43]).strip()
            celular_celda = str(fila[7]).strip().replace(".0", "").replace(" ", "")
            
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
            
            # Formateo de texto plano para WhatsApp sin caracteres corruptos
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                tarjeta_html = generar_tarjeta_html(nombre_egresado, carrera_profesional, index)
                components.html(tarjeta_html, height=690, scrolling=False)
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:14px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
