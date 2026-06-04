def conseguir_fuente_servidor(es_bold, tamano):
    """Descarga dinámicamente fuentes de Google con soporte UTF-8 completo para evitar cajas vacías"""
    import os
    
    # Nombres de archivos temporales locales
    nombre_archivo = "fuente_bold.ttf" if es_bold else "fuente_regular.ttf"
    
    # URLs de Google Fonts (Garantizan soporte de Ñ, tildes y signos ¡ ¿)
    url_font = (
        "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Bold.ttf"
        if es_bold else
        "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Regular.ttf"
    )
    
    # Si la fuente no existe localmente en el contenedor, se descarga una sola vez
    if not os.path.exists(nombre_archivo):
        try:
            r = requests.get(url_font, timeout=5)
            with open(nombre_archivo, "wb") as f:
                f.write(r.content)
        except Exception as e:
            # Si falla la red, recurrimos al plan de contingencia del sistema
            pass

    # Intentar cargar la fuente descargada con soporte latino total
    if os.path.exists(nombre_archivo):
        try:
            return ImageFont.truetype(nombre_archivo, tamano)
        except:
            pass
            
    # --- PLAN DE RESPALDO SI FALLA LA DESCARGA ---
    rutas_fuentes = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if es_bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if es_bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    
    for ruta in rutas_fuentes:
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, tamano)
            except:
                continue
                
    return ImageFont.load_default()
