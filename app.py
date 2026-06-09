import streamlit as st
import pandas as pd
import requests
import io
import os
import base64
import smtplib
import urllib.parse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Sistema Integral UNAMAD", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; }
    h1 { color: #1B365D; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f1f5f9; border-radius: 8px 8px 0 0; padding: 10px 20px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #1B365D !important; color: white !important; }
    .bloque-personalizado {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px;
        padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .btn-whatsapp {
        display: block; text-align: center; background-color: #25D366; color: white !important;
        padding: 12px; font-weight: 700; border-radius: 10px; text-decoration: none; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Portal de Gestión Institucional UNAMAD")
st.markdown("Unidad de Seguimiento al Egresado y Bolsa de Trabajo")

# Crear las 3 pestañas principales
tab_cumple, tab_boletin, tab_invitaciones = st.tabs([
    "🎂 Control de Cumpleaños", 
    "📰 Boletín de Convocatorias", 
    "📧 Invitaciones del Encuentro"
])

# ==========================================
# 2. FUNCIONES COMPARTIDAS (DATA Y LOGS)
# ==========================================
DB_LOG_FILE = "registro_envios_ax.csv"
URL_BASE_DATOS = "https://docs.google.com/spreadsheets/d/1ScZqatCGsyBUAOQBTdwkTxfOoZNlRfuTD5bhy_iRCao/edit?usp=sharing"

def cargar_log_permanente():
    if os.path.exists(DB_LOG_FILE):
        return set(pd.read_csv(DB_LOG_FILE)["id_unico"].tolist())
    return set()

def guardar_log_permanente(id_unico):
    saludados = cargar_log_permanente()
    saludados.add(id_unico)
    pd.DataFrame({"id_unico": list(saludados)}).to_csv(DB_LOG_FILE, index=False)

def descargar_excel(url):
    url_descarga = url.split('/edit')[0] + '/export?format=xlsx'
    resp = requests.get(url_descarga)
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

def obtener_imagen_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return ""

if "egresados_saludados" not in st.session_state:
    st.session_state.egresados_saludados = cargar_log_permanente()

# ==========================================
# PESTAÑA 1: CONTROL DE CUMPLEAÑOS
# ==========================================
with tab_cumple:
    col_c1, _ = st.columns([1, 2])
    with col_c1:
        fecha_c = st.date_input("📅 Fecha de procesamiento:", datetime.now(), key="date_c")
        dia_b = fecha_c.strftime("%d/%m")

    try:
        df = descargar_excel(URL_BASE_DATOS)
        jaguar_base64 = obtener_imagen_base64("cumpleanos.png")
        
        cumpleaneros_hoy = []
        for idx, fila in df.iterrows():
            try:
                f_celda = str(fila[43]).strip()
                if dia_b in f_celda:
                    nombre = str(fila[3]).split(',')[1].strip() if ',' in str(fila[3]) else str(fila[3])
                    cumpleaneros_hoy.append({
                        'idx': idx, 'nombre': nombre, 'carrera': fila[4], 
                        'sexo': str(fila[42]).upper(), 'celular': str(fila[7]).replace(".0","").strip(),
                        'id_unico': f"{nombre}_{dia_b}_{idx}"
                    })
            except: continue

        if not cumpleaneros_hoy:
            st.info(f"No hay cumpleañeros para el {dia_b}")
        else:
            for b in cumpleaneros_hoy:
                st.markdown('<div class="bloque-personalizado">', unsafe_allow_html=True)
                col_i, col_d = st.columns([1.2, 1])
                
                with col_d:
                    st.subheader(f"🥳 {b['nombre']}")
                    # Lógica de sexo y colores
                    banner = "linear-gradient(135deg, #1B365D 0%, #2A52BE 100%)" if b['sexo'] == 'M' else "linear-gradient(135deg, #800080 0%, #5A005A 100%)"
                    
                    texto_wa = f"¡FELIZ CUMPLEAÑOS! 🎂\n\n*{b['nombre']}*\n🎓 Egresado de {b['carrera']}\n\nTe desea la Unidad de Seguimiento al Egresado UNAMAD. ✨"
                    st.info(texto_wa)
                    
                    if b['id_unico'] in st.session_state.egresados_saludados:
                        st.success("✅ Ya registrado en Columna AX")
                    else:
                        num = b['celular']
                        if len(num) == 9:
                            link = f"https://api.whatsapp.com/send?phone=51{num}&text={urllib.parse.quote(texto_wa)}"
                            st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">💬 Enviar WhatsApp</a>', unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"📌 Confirmar Envío AX (Fila {b['idx']+2})", key=f"btn_{b['id_unico']}"):
                            guardar_log_permanente(b['id_unico'])
                            st.session_state.egresados_saludados.add(b['id_unico'])
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error en cumple: {e}")

# ==========================================
# PESTAÑA 2: BOLETÍN LABORAL (IMAGEN)
# ==========================================
with tab_boletin:
    st.subheader("📰 Generador de Boletín para el Grupo de WhatsApp")
    if "cola_boletin" not in st.session_state: st.session_state.cola_boletin = []

    with st.form("f_boletin", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            carr = st.selectbox("Carrera:", ["SISTEMAS", "DERECHO", "ADMINISTRACIÓN", "CONTABILIDAD", "EDUCACIÓN", "ENFERMERÍA", "ECOTURISMO", "AGROINDUSTRIAL", "FORESTAL"])
            puesto = st.text_input("Puesto:")
        with c2:
            empresa = st.text_input("Empresa:")
            link = st.text_input("Link/Correo:")
        if st.form_submit_button("➕ Añadir a la lista"):
            st.session_state.cola_boletin.append({'carrera': carr, 'puesto': puesto, 'empresa': empresa, 'link': link})
            st.rerun()

    if st.session_state.cola_boletin:
        # Generar Imagen con Pillow
        ancho = 600
        img = Image.new("RGB", (ancho, 150 + len(st.session_state.cola_boletin)*100 + 70), "#1B365D")
        d = ImageDraw.Draw(img)
        d.text((40, 40), "BOLETÍN DE CONVOCATORIAS UNAMAD", fill="#FFFFFF")
        
        y = 120
        for i in st.session_state.cola_boletin:
            d.rectangle([20, y, ancho-20, y+85], fill="#FFFFFF")
            d.text((40, y+10), f"🎓 {i['carrera']}", fill="#F59E0B")
            d.text((40, y+35), f"PUESTO: {i['puesto'].upper()}", fill="#1E293B")
            d.text((40, y+55), f"EMPRESA: {i['empresa']}", fill="#475569")
            y += 100
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), width=450)
        st.download_button("📥 Descargar Imagen para WhatsApp", buf.getvalue(), "boletin.png", "image/png")
        if st.button("🗑️ Borrar Lista"):
            st.session_state.cola_boletin = []
            st.rerun()

# ==========================================
# PESTAÑA 3: INVITACIONES PERSONALIZADAS (CORREO)
# ==========================================
with tab_invitaciones:
    st.subheader("📧 Envío Masivo de Invitaciones Personalizadas")
    st.write("Esta herramienta pone el nombre en la invitación y la envía al correo del egresado.")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        admin_email = st.text_input("Tu Correo Institucional:", placeholder="ejemplo@unamad.edu.pe")
        admin_pass = st.text_input("Contraseña de Aplicación:", type="password", help="Genera una 'Contraseña de Aplicación' en tu cuenta de Google.")
    
    with col_e2:
        url_inscritos = st.text_input("URL Excel de Inscritos:", value=URL_BASE_DATOS)
        if st.button("🔍 Cargar Inscritos"):
            st.session_state.df_inv = descargar_excel(url_inscritos)
            st.success(f"Cargados {len(st.session_state.df_inv)} registros.")

    if "df_inv" in st.session_state:
        df_inv = st.session_state.df_inv
        # Identificar columnas: 1: Apellidos, 2: Nombres, 8: Correo (según tu imagen)
        if st.button("🚀 INICIAR ENVÍO MASIVO"):
            if not admin_email or not admin_pass:
                st.error("Configura tu correo y contraseña primero.")
            elif not os.path.exists("invitacion.png"):
                st.error("No se encuentra el archivo 'invitacion.png' en la carpeta.")
            else:
                try:
                    # Conexión al servidor de correo
                    smtp = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp.starttls()
                    smtp.login(admin_email, admin_pass)

                    prog = st.progress(0)
                    for i, r in df_inv.iterrows():
                        # Extraer datos de las columnas según tu captura
                        apellidos = str(r[1]).strip()
                        nombres = str(r[2]).strip()
                        correo = str(r[8]).strip()
                        nombre_full = f"{nombres} {apellidos}".upper()

                        # --- DIBUJAR NOMBRE EN INVITACIÓN ---
                        inv_img = Image.open("invitacion.png")
                        draw_inv = ImageDraw.Draw(inv_img)
                        # Coordenadas donde se pondrá el nombre (ajustar según tu imagen)
                        draw_inv.text((250, 850), f"PARA: {nombre_full}", fill="#1B365D")
                        
                        img_io = io.BytesIO()
                        inv_img.save(img_io, format="PNG")
                        
                        # --- CREAR CORREO ---
                        msg = MIMEMultipart()
                        msg['Subject'] = f"Invitación Especial: IV Encuentro de Graduados - {nombres}"
                        msg['From'] = admin_email
                        msg['To'] = correo
                        
                        html = f"<p>Hola <b>{nombres}</b>, adjuntamos tu invitación personalizada para el Encuentro de Graduados UNAMAD 2026. ¡Te esperamos!</p>"
                        msg.attach(MIMEText(html, 'html'))
                        
                        img_att = MIMEImage(img_io.getvalue(), name=f"Invitacion_{nombres}.png")
                        msg.attach(img_att)
                        
                        smtp.sendmail(admin_email, correo, msg.as_string())
                        prog.progress((i+1)/len(df_inv))
                    
                    smtp.quit()
                    st.success("✅ ¡Todas las invitaciones han sido enviadas!")
                except Exception as ex:
                    st.error(f"Error de envío: {ex}")
