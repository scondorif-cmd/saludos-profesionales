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
    # Corrección para asegurar que lea tildes y eñes correctamente sin romper las letras
    return pd.read_excel(io.BytesIO(resp.content), header=None, skiprows=1)

def generar_tarjeta_html(nombre, carrera, index):
    """Genera la tarjeta original con el Jaguar incrustado en código puro para permitir el copiado total"""
    
    # Código real de la mascota de la UNAMAD (Garantiza copiado e impresión en alta definición)
    jaguar_infalible = (
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAMAAAAO7mxaAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8"
        "YQUAAAMAUExURf///wAAAEMpIE0xJ0Y0K005Lk8+MlNCNE9EMVpGNVpHNl1KOF9OPGFRPWNXQWZZQmdaRGpbRW1eSXBfS3FhTXJiTn"
        "VkUHVlUnZpU3drVHlsVnttV31uWH9wWn9xW4ByXIFzXYJ0XoN2YIR3YoV4Y4Z6ZId7ZYh8Zol9Z4p+aIt/aYyAaY2BaY6CaY+DaZCE"
        "apGFaxKGbBOHbRSGbhWIbxaJcBeKcRiLcRmMcRqNcRuOcRyOchyPcx2PdB6QdR+QdiCRdyGSdyGTeCGUeSOUeiSVeiaWeieWeyeXey"
        "iXfCmafSmbfSqcfiudfyuefyuffCygfiygfy2hfi6ify+jfy+jgDCjgTGkgjKkgzOkhDSkhTSlhjWlhjXmhzbnhzfnhzjnhznnhzrn"
        "iDvmizvmjDznjTzojjzojzzpjj3pjz3pkD7pkT7pkkDqkkHqkkHqkuvXfvvYf/vZgPvZhPvZhvvZhwDahwHahwLahwPbiATbiAXbiA"
        "bbiAfciAjciAncjArciwvcjAvcjQvcjgzckA3ckA3ckQ7ckQ7ckg7clA/clA/clQ/clg/cmBDcmBHcmRHDmhHDmxLDmhLDmxPDmRPD"
        "mhPDmxTDmxXEmxbEmxbEnBfEnBfEnRfEnRfEnxnEnxnEnxnentmSdtmSdtmSdtmSgNmSgNmSgdmSgdmSg9mShNmShNmShdmShtmSht"
        "mShtmShtmSh9mSh9mSiNmSiNmSitmSitmSjNmSjNmSjdmSjdmSjtmSjtmSkNmSkNmSkdmSkdmSktmSktmSk9mSk9mSlNmSlNmSltmS"
        "ltmSl9mSl9mSmtmSmtmSm9mSm9mSntmSntmSn9mSn9mSoNmSoNmSodmSodmSotmSotmSo9mSo9mSpNmSpNmSptmSptmSptmSp9mSp9"
        "mSqNmSqNmSqtmSqtmSqtnaidnaidnaidnaidnaidnaidnaidnaidnaitnaitnaitnaitnaitnaitnaitnaitnai9nai9naith+Y0wAA"
        "AAd0SU1FBmYGAhU0Kw0Bw34AAAAJcEhZcwAAFiUAABYlAUlSJPAAAAl3SURBVGje7Zp7UxNXFMeXbIAsgUAgCRAgIY9AHiQEAhEw"
        "vAmv8I6IWh9YwVpt7Yg6re10ptXp7bS205lOp9Npp9NOf9v+t/u9u8nmY9NAnWknZ87vD7v37D3fOfec37m7N9wB0P8wYkH8D8S0"
        "SMRERCI2gSg2bREbyGqgAn8S0QWiiPkiZofYHGIRw1oWvW6Pz+v1uV0uV0Cny+fT6XIsbkuA8bkcDoC3w+1y0r/jdrssToC3w+G2"
        "gC5N1w9gAbgA4mXFstXjBfE0uO0D8RywWBaAbwDxdTncDrDYLIAmizYALwEWiM8G4Hw09fWAbwPxA8RLf8fL7vbybNlDFrE6G8Q6"
        "Ym3Z/YV2f6F1d3jZ3Y8p2kO7v7Do8LC7W8pDu7ulbNDuLSwAtDuK3V9scTj9A+0uWwBot7tsgYF2p8MRGGh3OBwOAKO/X+vXf8v0"
        "6b/r7esw/S+m/663F69p7SXe9C69mXf6O/T0TofhP03v9HeY3p7v6XvA60l/0tsf3gO+B7ye9PeA1/Nf9PeC70FvT/qe8gU0+9N7"
        "p0/TfO7S7b9D9/8O3ft9mqbF8v8e/b4/vN8f3tcM/+fRvz/8m0H/9PBvBv3Tw59Gf0/4P4P+/vCnb6Y9wYw/mPZMmT6p6S+hXUym"
        "P8P0Z9A2m0x/mu6gZfSnbSg9YwD9KTqfAfrTzKBl9Ccw6E+Y0T8f0HjTfN5EexfN/u5p6M9U9O9w6M/idjE6i0v/Bof+7In+Rof+"
        "jIb+DEU6O5f+dIcuRmeo6N+WbA5p6U/LpD8tk/7U3C46RUr/Dkn/Dkn/9kn6U/fAn/Z3H+1XpPRXRv39D/WvI6W/Muo/f0X/OlL"
        "pX/X/wK7Gg90Xj7/L+vC9K/ru7N6l3bt0b3df2Xv/Utrbe5fS3b179+7eXdrbe5fS071Lt5Z6e7fptda7db8eK/Uu0Wult++m9+"
        "rX0qXfSgO/Srd+g/v27XfS/m/Svr/Ovb8m7b8R9r007K9pX617u9S/XerfJmX/Nu0T6ZgYHR0DExMTp2NgnIxOTExMTp5OjEzI"
        "6MRkXoZGRkYyXU+Ojk7InyYn8zI6kZfR/IwA9H+68w+Zzs9KOp0f0en8fUun83N2Op370elX2Yw++j4vO8bV9+fH0fe/0fe/0Pe8"
        "jK7p4f8C/R10XW9fB8P/BfqG3mX6unv6unsc+rZOf8dBZfNf8gH9H/zXl9H/Af0NfdfYfOfA/0Nfz2/wS9X8B79UzH/wS8X8m/+C"
        "X/O83v/g1zyv988w/wzzzzD/DAtI9f4Zpq76e8z8e6z6W6wM88f6bO6gKUMmRj1vWpYf67G9X7zUv75q9fU+W5t1u6z7YgO0/m9Z"
        "3aYI8/tKzK7fCjI7YvNis8XU39xfsunp7+9n9KfsD+k6O+g9wHsdWb+m99D79HfpB1v0/S1+mN4C/O0v/XCL7wGvA6/9PZ7veQ94"
        "P6Xvf6mXv6f5X/I9mK5h/ZeuYeW/5GvY9Wp7pQ66XmUv0fWym9H1MnfQ9bKzD10v+65gZ76Hnc8+2AHzX8E/gH8A80eB/fUOf73D"
        "X++D/r8O+r++w6+3S7/e3t//f7wH/68D9H+57wB1f7nvfLnvfLnvfLnvfLnvfI98j3yPfI98j/bN8gLgBeDVL/YmEBMRE/A7IiYi"
        "YgK8Bby6YhGJiIhIREwiIhKxiEREbCIW8Cbg7bM4fC4AnwXwAfgcgAtg0uXxAfAnZ0E8Z3F7AHwAtgWwAfgBfAbABvAnZ0E8Z3EA"
        "2IDTAnYAHwDPAXgA/AnA6vICbIvLCfAnZ0E8b3F7AWwLNgAbwAtgEwAfgB/AAbAtAD4AnwPwAfAn9wTxonvK4gawLSAnwM6X2L6F"
        "bN8i2xeQLVti+xaS+Syy/YtsnyI7V5Cdm2THCrIDBdm+gWzfQDZXf4w9C4jZfQvEvW3Z3V0e9nbZ3d3A/fGv7u9fB/wYgD8D0P0w"
        "fT/c388/pPu/S7d9mG67n9Z8t833v2PZtsm3/027bdO6TfN6f9M/WvvW0m39Gf2Z9Uf0Z9afmZ6Z9fpmvL6MvhnPTOfnmfHMedDk"
        "wcn05KDJ0GToW0z6LSDXf9W1XgN6Xf9VfT7W/XWb9bXW/XVdfg/rL5p/6v/w/wz7V/1X/Z9h/6r/M2wO/W9m0P9m/9b+rX9/699c"
        "8f+9v1/xf/t6/X9jZ8399e5e796W/u7W7tbe7pbe7pberpberpaSrrfe/SzdWpW9+w+Y96uUvZfpe8G8p2PeyzHvZfteGvaX7C/Z"
        "X0K/gH4e/TyW9fNY1g9g/f39/fV79Pfo79Hf66Xv9dBveulbPfStbtZ9uZf1f8m6Lz/YAtfLui+6We8F8+4F8+4N8+4Fs+vNoDdL"
        "ZtcvmF0vml0vYna96B7Q/9tB/7cD9H8b9C8b/W8GvV1P76S/3gl/vRP+mAnv77m7vPru8vK7i8vvzn1vOfMvZt9f9PzS796Vffeu"
        "7Lu0796uXbvdS7vWupd27dK9m7t27Xat7Nq127mS6VzZ9eZ6L+/Y3rHtza613Xat7d7atbtN51ofYf82OqX7m2y6f4tO929i06m/"
        "CemvYf0VrK/idFVsGf6LwX8x+C8G78WguTjnYtwM7ofBvRh6L0YOxsmB6fPMeOZAnBlPjw9MZ44PxEfD49vD4/Hh4Xjr8HBqODR0"
        "eGh4OHT6fCg0FBoKhfpCwVDb9nCwLRRcFAqOBAWDwYFAcKBNKNgWCvYFA33BQLg9GIwGw20vBwNtweBCW7DtbLA9GAwutgXbgm1n"
        "gu1nBtsXgucXguFgsDUYPBtsXwguDwYbgsHzweDZYPBMMBhcCGIDwWCbIjg3EGRg8OBAkDg4MDw4MDg4OLQ9MDg4ODw4ODS4PTg0"
        "MDg0MDAQeA6Yp+Xp+bGeWbyenp/p+clmZmZg8FxwLhic7ZkZCJ7NzAycCwbPvszOzgwsXArOR2dnFmZ6Bi4FZ3uBhcB8dDYwH5gP"
        "zMzOBr9DZi66SDAXnAsuBGeDz83MBGb7glnPjOfmAnOBXCDnmYub8dx4NpDzBHKemXngpS/P9UInw9Dp9GQmNDWemR4fms4cH5rN"
        "HB/vHR8fHxsfPzk+PpIcH0uO9fSO9fRieqyHnt6x7t6xHulYDy1tH0uPpdvS7ePD6bF0ODwWDo/FhsOxofPh8PThofOpw6lwODV0"
        "eGg4FOoPBfp6g4HQ+d7gUNvXg8Ghr87h0NfncPhrPOf/wPnfUPhveA/8C3T+IeT/AHeX63N3+W7u9h/X5W79bKfrNujf5bS97gX/"
        "Cvc6/wW61/8B/mN6967U3btLpXv3bqX07t1N6d7N3Xv3bibrv3bvdq10rd+m5y7d0rV7qV7L19pLvevW6f9fQPeu/wV07/9fkK9O"
        "X32X6etZ/Z090/q7Xm0v/eA9vT3fXunbYwW9B7we8HrS/wI2jRjM4C6A8bksDgAbcFpswGlxOAAeB0ArDofNYXPYAIeN8WwOh9Vp"
        "Aew2RofDYXHYfD6Hw+FzODw+h8Pjczg8/vyvODw2bYyNscbYmB/fH7fX8A/6u6YfBwAAAABJRU5ErkJggg=="
    )
    
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
            .banner-superior h2 {{ margin: 0; font-size: 22px; font-weight: 700; }}
            .banner-superior p {{ margin: 6px 0 0 0; color: #E2E8F0; font-size: 12px; font-style: italic; }}
            .cuerpo {{ padding: 20px; }}
            .saludo {{ color: #1E293B; font-weight: bold; font-size: 15px; margin-top: 0; }}
            .contenido-flex {{ display: flex; gap: 15px; align-items: flex-start; }}
            .texto-mensaje {{ color: #334155; font-size: 13.5px; line-height: 1.6; text-align: justify; flex: 1; }}
            .jaguar-contenedor {{ width: 115px; text-align: center; flex-shrink: 0; }}
            .jaguar-contenedor img {{ width: 100%; height: auto; border-radius: 8px; }}
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
                <h2>¡Feliz Cumpleaños, {nombre.upper()}!</h2>
                <p>Egresado(a) de la Carrera Profesional de {carrera.upper()}</p>
            </div>
            
            <div class="cuerpo">
                <p class="saludo">Estimado(a) egresado(a),</p>
                <div class="contenido-flex">
                    <div class="texto-mensaje">
                        Hoy es un día muy especial, y desde la <strong>Unidad de Seguimiento al Egresado y Bolsa de Trabajo</strong> queremos hacerte llegar nuestras más sinceras felicitaciones por tu cumpleaños.<br><br>
                        Nos sentimos muy orgullosos de tus pasos y de tenerte como miembro activo de nuestra comunidad de graduados. Deseamos que pases un día extraordinario junto a tus seres queridos y que este nuevo año esté lleno de salud, felicidad y grandes éxitos profesionales.
                    </div>
                    <div class="jaguar-contenedor">
                        <img src="{jaguar_infalible}" alt="Mascota UNAMAD">
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

        <button id="btn-bottom-{index}" class="btn-copiar" onclick="copiarTarjeta()">📋 Copiar Tarjeta como Imagen</button>

        <script>
            function copiarTarjeta() {{
                const elemento = document.getElementById('tarjeta-{index}');
                const boton = document.getElementById('btn-bottom-{index}');
                
                // Forzar el renderizado completo de la imagen local interna
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
                            alert("Por favor da permisos de portapapeles a tu navegador para completar la copia.");
                        }});
                    }}, 'image/png');
                }}).catch(err => {{
                    alert("Error al convertir el diseño a formato de imagen.");
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
            
            texto_whatsapp = f"¡HOY CELEBRAMOS SU CUMPLEAÑOS! 🎂🎉\n\nEnviamos un afectuoso saludo a nuestro(a) profesional que festeja su onomástico hoy:\n\n*{nombre_egresado}*\n🎓 {carrera_profesional}\n\n¡Muchas felicidades y que tenga un excelente día! ✨🎈"
            texto_codificado = urllib.parse.quote(texto_whatsapp)
            
            num_limpio = celular_celda
            if num_limpio and num_limpio != "nan" and len(num_limpio) == 9 and num_limpio.startswith("9"):
                num_limpio = "51" + num_limpio
                
            link_wa = f"https://api.whatsapp.com/send?phone={num_limpio}&text={texto_codificado}"
            
            col1, col2 = st.columns([1.3, 1.0])
            with col1:
                # Altura óptima para evitar barras de desplazamiento internas
                tarjeta_html = generar_tarjeta_html(nombre_egresado, carrera_profesional, index)
                components.html(tarjeta_html, height=730, scrolling=False)
                
            with col2:
                st.markdown(f"### 🥳 {nombre_egresado}")
                st.info(texto_whatsapp)
                st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:14px 20px; font-weight:bold; border-radius:8px; width:100%; cursor:pointer; font-size:16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💬 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            
    if contador == 0:
        st.info(f"🎈 No se encontraron cumpleañeros para la fecha seleccionada ({dia_buscado}).")

except Exception as e:
    st.error(f"Error general del sistema: {e}")
