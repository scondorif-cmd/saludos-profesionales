import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
import io
import base64
import os
import streamlit.components.v1 as components

# Configuración premium de la plataforma
st.set_page_config(page_title="Control de Cumpleaños UNAMAD", page_icon="🎓", layout="wide")

# Estilos CSS globales inyectados para refinar la UI de Streamlit
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1B365D; font-weight: 800; font-size: 2.2rem !important; margin-bottom: 0.2rem; }
    .subtitulo-app { color: #475569; font-size: 1.05rem; margin-bottom: 2rem; }
    
    /* Panel de Métricas Estilizado */
    .panel-metricas {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Caja contenedora para cada Egresado */
    .bloque-egresado {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    }
    
    /* Estilos personalizados para los botones nativos de Streamlit */
    div.stButton > button:first-child {
        background-color: #25D366;
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 16px;
        border-radius: 10px;
        width: 100%;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #20BA56;
        border: none;
        color: white;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎓 Sistema de Cumpleaños UNAMAD</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo-app'>Gestión institucional y envío automatizado de saludos para la comunidad de egresados.</p>", unsafe_allow_html=True)

# Inicializar el contador de envíos y la lista de control de IDs en la sesión
if "registro_envios" not in st.session_state:
    st.session_state.registro_envios = {}
if "egresados_saludados" not in st.session_state:
    st.session_state.egresados_saludados = set()

# Layout de barra de control principal
col_control1, col_control2 = st.columns([1, 2])
with col_control1:
    fecha_seleccionada = st.date_input("📅 Fecha de procesamiento:", datetime.now())
    dia_buscado = fecha_seleccionada.strftime("%d/%m")

# Inicializar el contador específico para el día seleccionado
if dia_buscado not in st.session_state.registro_envios:
    st.session_state.registro_envios[dia_buscado] = 0

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
    nombre_archivo = "cumpleanos.png"
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded_string}"
    else:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='110' height='110'><rect width='110' height='110' fill='%23cccccc'/></svg>"

def generar_tarjeta_html(nombre, carrera, index, jaguar_src, titulo_egresado, saludo_inicial, degradado_color):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            body {{ margin: 0; padding: 5px; font-family: 'Segoe UI', Arial, sans-serif; background-color: #FFFFFF; }}
            .tarjeta-contenedor {{
                background-color: #FFFFFF; 
                border-radius: 12px; 
                box-shadow: 0 8px 24px rgba(0,0,0,0.12); 
                overflow: hidden; 
                max-width: 450px; 
                margin: 0 auto; 
                border: 1px solid #E2E8F0;
            }}
            .banner-superior {{
                background: {degradado_color}; 
                padding: 24px 16px; 
                text-align: center; 
                color: white;
            }}
            .banner-superior h2 {{ margin: 0; font-size: 20px; font-weight: 700; letter-spacing: -0.3px; }}
            .banner-superior p {{ margin: 6px 0 0 0; color: #E0F2FE; font-size: 11.5px; font-weight: 500; text-transform: uppercase; }}
            .cuerpo {{ padding: 20px; }}
            .saludo {{ color: #1E293B; font-weight: 700; font-size: 15px; margin-top: 0; margin-bottom: 12px; }}
            
            .contenido-flex {{ display: flex; gap: 15px; align-items: center; margin-bottom: 12px; }}
            .texto-mensaje-corto {{ color: #334155; font-size: 13px; line-height: 1.5; text-align: justify; flex: 1; }}
            .jaguar-contenedor {{ width: 105px; text-align: center; flex-shrink: 0; }}
            .jaguar-contenedor img {{ width: 100%; height: auto; border-radius: 8px; }}
            
            .texto-mensaje-largo {{ color: #334155; font-size: 13px; line-height: 1.5; text-align: justify; width: 100%; }}
            
            .eslogan {{ color: #1B365D; text-align: center; margin: 18px 0 4px 0; font-size: 15px; font-weight: 700; }}
            .pie-pagina {{
                background-color: #0B1D33; 
                padding: 14px; 
                text-align: center; 
                color: white; 
                font-size: 10.5px; 
                line-height: 1.4;
            }}
            .btn-copiar {{
                display: block;
                width: 100%;
                max-width: 450px;
                margin: 12px auto 0 auto;
                background: #F1F5F9;
                color: #334155;
                border: 1px solid #CBD5E1;
                padding: 10px;
                font-weight: 600;
                font-size: 13px;
                border-radius: 8px;
                cursor: pointer;
                text-align: center;
                transition: all 0.2s;
            }}
            .btn-copiar:hover {{
                background: #E2E8F0;
                color: #0F172A;
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
                            boton.style.color = "#FFFFFF";
                            boton.style.border = "1px solid #22C55E";
                            
                            setTimeout(() => {{
                                boton.innerText = "📋 Copiar Tarjeta como Imagen";
                                boton.style.background = "#F1F5F9";
                                boton.style.color = "#334155";
                                boton.style.border = "1px solid #CBD5E1";
                            }}, 3000);
                        }}).catch(err => {{
                            alert("Por favor otorga permisos de portapapeles.");
                        }});
                    }}, 'image/png');
                }}).catch(err => {{
                    alert("Error al procesar la tarjeta.");
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_content

try:
    df = descargar_datos()
    jaguar_src = obtener_jaguar_base64()
    
    # Renderizado estético del cuadro superior de estadísticas
    st.markdown(f"""
        <div class="panel-metricas">
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <p style="margin:0; font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">📅 Fecha de Análisis</p>
                    <p style="margin:0; font-size: 1.8rem; color: #1B365D; font-weight: 800;">{dia_buscado}</p>
                </div>
                <div style="border-left: 1px solid #E2E8F0;"></div>
                <div>
                    <p style="margin:0; font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">📨 Control de Envíos Realizados</p>
                    <p style="margin:0; font-size: 1.8rem; color: #22C55E; font-weight: 800;">{st.session_state.registro_envios[dia_buscado]} saludos</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 🎂 Lista de Cumpleañeros:")
    contador = 0
    
    for index, fila in df.iterrows():
        try:
            nombre_completo = str(fila[3]).strip()       
            carrera_profesional = str(fila[4]).strip()   
            sexo_celda = str(fila[42]).strip().upper()  # Columna AQ
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

            # Identificador único para el control estricto del egresado
            id_unico_egresado = f"{nombre_egresado}_{dia_buscado}"

            # Lógica adaptada según el género de la columna AQ para Textos y Colores Corporativos
            if sexo_celda == "M" or sexo_celda == "MASCULINO":
                titulo_egresado = "Egresado"
                saludo_inicial = "Estimado egresado"
                art_saludo = "nuestro profesional"
                # Degradado institucional azul ejecutivo
                degradado_color = "linear-gradient(135deg, #1B365D 0%, #2A52BE 100%)"
            elif sexo_celda == "F" or sexo_celda == "FEMENINO":
                titulo_egresado = "Egresada"
                saludo_inicial = "Estimada egresada"
                art_saludo = "nuestra profesional"
                # Degradado institucional púrpura guinda (Fiel a la imagen original)
                degradado_color = "linear-gradient(135deg, #7D1D7F 0%, #521454 100%)"
            else:
                titulo_egresado = "Egresado(a)"
                saludo_inicial = "Estimado(a) egresado(a)"
                art_saludo = "nuestro(a) profesional"
                degradado_color = "linear-gradient(135deg, #1B365D 0%, #0B1D33 100%)"

            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a {art_saludo} que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {titulo_egresado} de {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            # Apertura del bloque estilizado individual
            st.markdown('<div class="bloque-egresado">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1.2, 1.0])
            with col1:
                tarjeta_html = generar_tarjeta_html(nombre_egresado, carrera_profesional, index, jaguar_src, titulo_egresado, saludo_inicial, degradado_color)
                components.html(tarjeta_html, height=660, scrolling=False)
                
            with col2:
                st.markdown(f"<h3 style='margin-top:0; color:#1E293B;'>🥳 {nombre_egresado}</h3>", unsafe_allow_html=True)
                st.info(texto_whatsapp)
                
                # Comprobar si este cumpleañero ya fue procesado hoy
                ya_enviado = id_unico_egresado in st.session_state.egresados_saludados
                
                if ya_enviado:
                    # El botón cambia visualmente indicando éxito y se desactiva para evitar reconteos
                    st.button(f"✅ Saludo registrado para {nombre_egresado}", key=f"btn_success_{index}", disabled=True)
                else:
                    # Botón unificado que ejecuta la suma única y abre WhatsApp
                    if st.button(f"💬 Enviar por WhatsApp", key=f"btn_action_{index}"):
                        st.session_state.egresados_saludados.add(id_unico_egresado)
                        st.session_state.registro_envios[dia_buscado] += 1
                        
                        # Inyección segura de JS para saltarse bloqueos pop-up
                        components.html(f"""
                            <script>
                                window.open("{link_wa}", "_blank");
                            </script>
                        """, height=0)
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
            
    if contador == 0:
        st.info(f"🎈 No se encontraron egresados registrados que cumplan años en la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error en el flujo principal del sistema: {e}")
