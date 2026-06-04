import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
import io
import base64
import os
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
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

def obtener_jaguar_base64():
    """Busca el archivo cumpleanos.png en tu GitHub y lo convierte automáticamente en código real"""
    nombre_archivo = "cumpleanos.png"
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded_string}"
    else:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='110' height='110'><rect width='110' height='110' fill='%23cccccc'/></svg>"

def generar_tarjeta_html(nombre, carrera, index, jaguar_src, titulo_egresado, saludo_inicial):
    """Genera la tarjeta con personalización de género y estructura optimizada"""
    
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
            .banner-superior h2 {{ margin: 0; font-size: 21px; font-weight: 700; }}
            .banner-superior p {{ margin: 6px 0 0 0; color: #E2E8F0; font-size: 12px; font-style: italic; }}
            .cuerpo {{ padding: 20px; }}
            .saludo {{ color: #1E293B; font-weight: bold; font-size: 15px; margin-top: 0; }}
            
            .contenido-flex {{ display: flex; gap: 15px; align-items: center; margin-bottom: 15px; }}
            .texto-mensaje-corto {{ color: #334155; font-size: 13.5px; line-height: 1.6; text-align: justify; flex: 1; }}
            .jaguar-contenedor {{ width: 115px; text-align: center; flex-shrink: 0; }}
            .jaguar-contenedor img {{ width: 100%; height: auto; border-radius: 8px; }}
            
            .texto-mensaje-largo {{ color: #334155; font-size: 13.5px; line-height: 1.6; text-align: justify; width: 100%; clear: both; }}
            
            .eslogan {{ color: #1B365D; text-align: center; margin: 20px 0 5px 0; font-size: 16px; font-weight: 700; }}
            .pie-pagina {{
                background-color: #0B1D33; 
                padding: 15px; 
                text-align: center; 
                color: white; 
                font-size: 11px; 
                line-height: 1.4;
            }}
            .btn-copiar {{
                display: block;
                width: 100%;
                max-width: 480px;
                margin: 10px auto;
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
                <h2>&iexcl;Feliz Cumplea&ntilde;os, {nombre.upper()}! &#129395;</h2>
                <p>{titulo_egresado} de la Carrera Profesional de {carrera.upper()}</p>
            </div>
            
            <div class="cuerpo">
                <p class="saludo">{saludo_inicial},</p>
                
                <div class="contenido-flex">
                    <div class="texto-mensaje-corto">
                        Hoy es un d&iacute;a muy especial, y desde la <strong>Unidad de Seguimiento al Egresado y Bolsa de Trabajo</strong> queremos hacerte llegar nuestras m&aacute;s sinceras felicitaciones por tu cumpleaños.
                    </div>
                    <div class="jaguar-contenedor">
                        <img src="{jaguar_src}" alt="Mascota UNAMAD">
                    </div>
                </div>
                
                <div class="texto-mensaje-largo">
                    Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra comunidad de graduados. Deseamos que pases un d&iacute;a extraordinario junto a tus seres queridos y que este nuevo a&ntilde;o est&eacute; lleno de salud, felicidad y grandes &eacute;xitos profesionales.
                </div>
                
                <div class="eslogan">&iexcl;Que disfrutes mucho de tu d&iacute;a!</div>
            </div>
            
            <div class="pie-pagina">
                <span style="color: #38BDF8; font-weight: bold; letter-spacing: 0.5px;">ATENTAMENTE,</span><br>
                <span style="color: #FFFFFF; font-weight: 600;">Unidad de Seguimiento al Egresado y Bolsa de Trabajo - DAA</span><br>
                <span style="color: #94A3B8;">Universidad Nacional Amazónica de Madre de Dios</span>
            </div>
        </div>

        <button id="btn-bottom-{index}" class="btn-copiar" onclick="copiarTarjeta()">📋 Copiar Tarjeta como Imagen</button>

        <script>
            function copiarTarjeta() {{
                const elemento = document.getElementById('tarjeta-{index}');
                const boton = document.getElementById('btn-bottom-{index}');
                
                html2canvas(elemento, {{ scale: 2, logging: false, useCORS: true }}).then(canvas => {{
                    canvas.toBlob(blob => {{
                        if(!blob) return;
                        const item = new ClipboardItem({{ "image/png": blob }});
                        navigator.clipboard.write([item]).then(() => {{
                            boton.innerText = "✅ ¡Tarjeta Copiada! Pégala en WhatsApp (Ctrl+V)";
                            boton.style.background = "#22C55E";
                            
                            setTimeout(() => {{
                                boton.innerText = "📋 Copiar Tarjeta como Imagen";
                                boton.style.background = "linear-gradient(135deg, #1B365D 0%, #0B1D33 100%)";
                            }}, 3000);
                        }}).catch(err => {{
                            alert("Por favor otorga permisos de portapapeles a tu navegador.");
                        }});
                    }}, 'image/png');
                }}).catch(err => {{
                    alert("Error al procesar el lienzo de la tarjeta.");
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
    
    jaguar_src = obtener_jaguar_base64()
    
    st.subheader(f"🎂 Cumpleañeros del día {dia_buscado}:")
    contador = 0
    
    for index, fila in df.iterrows():
        try:
            nombre_completo = str(fila[3]).strip()       
            carrera_profesional = str(fila[4]).strip()   
            sexo_celda = str(fila[42]).strip().upper()  # <-- Columna AQ mapeada (Índice 42)
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
            
            nombre_egresado = nombre_egresado.replace("da", "día").replace("Cumpleaos", "Cumpleaños")
            carrera_profesional = carrera_profesional.strip()

            # Lógica adaptada según el género de la columna AQ
            if sexo_celda == "M" or sexo_celda == "MASCULINO":
                titulo_egresado = "Egresado"
                saludo_inicial = "Estimado egresado"
                art_saludo = "nuestro profesional"
            elif sexo_celda == "F" or sexo_celda == "FEMENINO":
                titulo_egresado = "Egresada"
                saludo_inicial = "Estimada egresada"
                art_saludo = "nuestra profesional"
            else:
                titulo_egresado = "Egresado(a)"
                saludo_inicial = "Estimado(a) egresado(a)"
                art_saludo = "nuestro(a) profesional"

            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a {art_saludo} que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {titulo_egresado} de {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            col1, col2 = st.columns([1.3, 1.0])
            with col1:
                tarjeta_html = generar_tarjeta_html(nombre_egresado, carrera_profesional, index, jaguar_src, titulo_egresado, saludo_inicial)
                components.html(tarjeta_html, height=720, scrolling=False)
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:14px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
