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
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1 { color: #1B365D; font-weight: 800; font-size: 2.2rem !important; margin-bottom: 0.1rem; }
    .subtitulo-app { color: #475569; font-size: 1.05rem; margin-bottom: 1.5rem; }
    
    /* Panel de Métricas Estilizado */
    .panel-metricas {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Caja contenedora para cada Egresado */
    .bloque-egresado {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    }
    
    /* Botón personalizado nativo HTML para abrir WhatsApp sin bloqueos */
    .btn-whatsapp-nativo {
        display: block;
        text-align: center;
        background-color: #25D366;
        color: white !important;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 16px;
        border-radius: 10px;
        text-decoration: none;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
        transition: all 0.2s ease;
        border: none;
        width: 100%;
        box-sizing: border-box;
    }
    .btn-whatsapp-nativo:hover {
        background-color: #20BA56;
        transform: translateY(-1px);
    }
    
    /* Botón de estado inactivo estilo Streamlit */
    .btn-deshabilitado {
        display: block;
        text-align: center;
        background-color: #F1F5F9;
        color: #94A3B8 !important;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 16px;
        border-radius: 10px;
        text-decoration: none;
        border: 1px solid #E2E8F0;
        width: 100%;
        box-sizing: border-box;
        cursor: not-allowed;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎓 Sistema de Cumpleaños UNAMAD</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo-app'>Registros de cumpleaños de egresados.</p>", unsafe_allow_html=True)

# ARCHIVO DE BASE DE DATOS LOCAL PARA PERSISTENCIA
DB_LOG_FILE = "registro_envios_ax.csv"

def cargar_log_permanente():
    if os.path.exists(DB_LOG_FILE):
        return set(pd.read_csv(DB_LOG_FILE)["id_unico"].tolist())
    return set()

def guardar_log_permanente(id_unico):
    saludados = cargar_log_permanente()
    saludados.add(id_unico)
    pd.DataFrame({"id_unico": list(saludados)}).to_csv(DB_LOG_FILE, index=False)

# Inicializar lista de saludados persistente en la sesión actual
if "egresados_saludados" not in st.session_state:
    st.session_state.egresados_saludados = cargar_log_permanente()

# Layout de barra de control principal
col_control1, col_control2 = st.columns([1, 2])
with col_control1:
    fecha_seleccionada = st.date_input("📅 Fecha de procesamiento:", datetime.now())
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
    nombre_archivo = "cumpleanos.png"
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded_string}"
    else:
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='110' height='110'><rect width='110' height='110' fill='%23cccccc'/></svg>"

def generar_tarjeta_html(nombre, carrera, index, jaguar_src, titulo_egresado, saludo_inicial, colores):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            html, body {{ margin: 0; padding: 0; background-color: #FFFFFF; font-family: 'Segoe UI', Arial, sans-serif; }}
            .tarjeta-contenedor {{
                background-color: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.08); 
                overflow: hidden; max-width: 440px; margin: 0 auto; border: 1px solid #E2E8F0;
            }}
            .banner-superior {{ background: {colores['banner']}; padding: 22px 16px; text-align: center; color: white; }}
            .banner-superior h2 {{ margin: 0; font-size: 19px; font-weight: 700; letter-spacing: -0.3px; }}
            .banner-superior p {{ margin: 6px 0 0 0; color: #E0F2FE; font-size: 11px; font-weight: 500; text-transform: uppercase; }}
            .cuerpo {{ padding: 18px; }}
            .saludo {{ color: #1E293B; font-weight: 700; font-size: 14.5px; margin-top: 0; margin-bottom: 12px; }}
            .contenido-flex {{ display: flex; gap: 14px; align-items: center; margin-bottom: 12px; }}
            .texto-mensaje-corto {{ color: #334155; font-size: 12.5px; line-height: 1.5; text-align: justify; flex: 1; }}
            .jaguar-contenedor {{ width: 100px; text-align: center; flex-shrink: 0; }}
            .jaguar-contenedor img {{ width: 100%; height: auto; border-radius: 8px; }}
            .texto-mensaje-largo {{ color: #334155; font-size: 12.5px; line-height: 1.5; text-align: justify; width: 100%; }}
            .eslogan {{ color: {colores['eslogan']}; text-align: center; margin: 16px 0 4px 0; font-size: 14.5px; font-weight: 700; }}
            .pie-pagina {{ background: {colores['pie_fondo']}; padding: 14px; text-align: center; color: white; font-size: 10px; line-height: 1.4; }}
            .btn-copiar {{
                display: block; width: 100%; max-width: 440px; margin: 10px auto 0 auto; background: #F1F5F9;
                color: #334155; border: 1px solid #CBD5E1; padding: 9px; font-weight: 600; font-size: 12.5px;
                border-radius: 8px; cursor: pointer; text-align: center; transition: all 0.2s;
            }}
            .btn-copiar:hover {{ background: #E2E8F0; color: #0F172A; }}
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
                <span style="color: {colores['atentamente']}; font-weight: bold; letter-spacing: 0.5px;">ATENTAMENTE,</span><br>
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
                            boton.innerText = "✅ ¡Tarjeta Copiada!";
                            boton.style.background = "#22C55E"; boton.style.color = "#FFFFFF";
                            setTimeout(() => {{
                                boton.innerText = "📋 Copiar Tarjeta como Imagen";
                                boton.style.background = "#F1F5F9"; boton.style.color = "#334155";
                            }}, 3000);
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
    jaguar_src = obtener_jaguar_base64()
    
    while df.shape[1] <= 50:
        df[df.shape[1]] = ""
        
    contador_cumpleanos_hoy = 0
    bloques_a_renderizar = []

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
            nombre_egresado = nombre_completo.split(",")[1].strip() if "," in nombre_completo else nombre_completo
            nombre_egresado = nombre_egresado.replace("da", "día").replace("Cumpleaos", "Cumpleaños")
            
            id_unico_egresado = f"{nombre_egresado}_{dia_buscado}_{index}"
            
            bloques_a_renderizar.append({
                'index': index, 'nombre': nombre_egresado, 'carrera': carrera_profesional,
                'sexo': sexo_celda, 'celular': celular_celda, 'id_unico': id_unico_egresado
            })
            
            if id_unico_egresado in st.session_state.egresados_saludados:
                contador_cumpleanos_hoy += 1

    st.markdown(f"""
        <div class="panel-metricas">
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <p style="margin:0; font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">📅 Fecha de Análisis</p>
                    <p style="margin:0; font-size: 1.8rem; color: #1B365D; font-weight: 800;">{dia_buscado}</p>
                </div>
                <div style="border-left: 1px solid #E2E8F0;"></div>
                <div>
                    <p style="margin:0; font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">📨 Columna AX: Envíos Registrados</p>
                    <p style="margin:0; font-size: 1.8rem; color: #22C55E; font-weight: 800;">{contador_cumpleanos_hoy} saludos enviados hoy</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 🎂 Lista de Cumpleañeros:")
    
    if len(bloques_a_renderizar) == 0:
        st.info(f"🎈 No se encontraron egresados registrados que cumplan años en la fecha seleccionada ({dia_buscado}).")
    else:
        for b in bloques_a_renderizar:
            colores_render = {}
            if b['sexo'] in ["M", "MASCULINO"]:
                titulo_egresado = "Egresado"
                saludo_inicial = "Estimado egresado"
                art_saludo = "nuestro profesional"
                colores_render = {'banner': 'linear-gradient(135deg, #1B365D 0%, #2A52BE 100%)', 'eslogan': '#1B365D', 'atentamente': '#38BDF8', 'pie_fondo': '#0B1D33'}
            elif b['sexo'] in ["F", "FEMENINO"]:
                titulo_egresado = "Egresada"
                saludo_inicial = "Estimada egresada"
                art_saludo = "nuestra profesional"
                colores_render = {'banner': 'linear-gradient(135deg, #800080 0%, #5A005A 100%)', 'eslogan': '#800080', 'atentamente': '#F472B6', 'pie_fondo': '#3B003B'}
            else:
                titulo_egresado = "Egresado(a)"
                saludo_inicial = "Estimado(a) egresado(a)"
                art_saludo = "nuestro(a) profesional"
                colores_render = {'banner': 'linear-gradient(135deg, #1B365D 0%, #0B1D33 100%)', 'eslogan': '#1B365D', 'atentamente': '#38BDF8', 'pie_fondo': '#0B1D33'}

            texto_whatsapp = f"¡HOY CELEBRAMOS TU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a {art_saludo} que festeja su onomástico hoy:\n\n*{b['nombre']}*\n🎓 {titulo_egresado} de {b['carrera']}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = b['celular']
            es_numero_valido = num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9")
            
            if es_numero_valido:
                num_limpio = "51" + num_limpio
                link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            else:
                link_wa = "#"
            
            st.markdown('<div class="bloque-egresado">', unsafe_allow_html=True)
            col1, col2 = st.columns([1.2, 1.0], gap="small")
            
            with col1:
                tarjeta_html = generar_tarjeta_html(b['nombre'], b['carrera'], b['index'], jaguar_src, titulo_egresado, saludo_inicial, colores_render)
                components.html(tarjeta_html, height=590, scrolling=False)
                
            with col2:
                st.markdown(f"<h3 style='margin-top:0; color:#1E293B;'>🥳 {b['nombre']}</h3>", unsafe_allow_html=True)
                st.info(texto_whatsapp)
                
                ya_saludado = b['id_unico'] in st.session_state.egresados_saludados
                
                if ya_saludado:
                    st.markdown(f'<a class="btn-deshabilitado">✅ Registrado en Columna AX para {b["nombre"]}</a>', unsafe_allow_html=True)
                else:
                    # IMPLEMENTACIÓN CRUCIAL: El botón de WhatsApp va FUERA del formulario
                    if es_numero_valido:
                        st.markdown(f'<a href="{link_wa}" target="_blank" class="btn-whatsapp-nativo">💬 Enviar por WhatsApp</a>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<a class="btn-deshabilitado">⚠️ Sin número de WhatsApp válido</a>', unsafe_allow_html=True)
                    
                    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                    
                    # El formulario ahora solo se encarga de guardar y confirmar el registro de manera aislada
                    with st.form(key=f"form_ax_{b['id_unico']}", border=False):
                        if st.form_submit_button("📌 Confirmar envío (Guardar en Columna AX)"):
                            guardar_log_permanente(b['id_unico'])
                            st.session_state.egresados_saludados.add(b['id_unico'])
                            st.success(f"¡Éxito! Registro guardado en la columna AX (Fila {b['index'] + 2})")
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error en el flujo principal del sistema: {e}")
