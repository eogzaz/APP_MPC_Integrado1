import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import html, re
import pandas as pd
from astroquery.mpc import MPC
import numpy as np
from utils import Date_to_julian

def periodo_fecha_perihelio(asteroide):
    datos = MPC.query_object('asteroid',number=asteroide,return_fields='period,perihelion_date,perihelion_date_jd')[0]
    periodo = float(datos['period'])*365.25
    fecha_perihelio = float(datos['perihelion_date_jd'])
    return periodo, fecha_perihelio

# --- Función auxiliar para obsTime ---
def parse_obs_time(val):
    if val is None or pd.isna(val):
        return pd.NaT
    val = val.strip()
    # Caso ISO
    try:
        return pd.to_datetime(val, errors="raise", utc=True)
    except Exception:
        pass
    # Caso YYYY-MM-DD.frac (día fraccionario)
    try:
        if "." in val and "-" in val:
            base, frac = val.split(".")
            frac = "0." + frac
            frac_day = float(frac)
            base_date = datetime.strptime(base, "%Y-%m-%d")
            return base_date + timedelta(days=frac_day)
    except Exception:
        pass
    return pd.NaT

# --- Saneador de XML ---
def _sanitize_xml(xml_string: str) -> str:
    s = xml_string.lstrip("\ufeff")
    s = html.unescape(s)
    s = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', s)  # control chars ilegales
    s = re.sub(r'&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z][A-Za-z0-9]*;)', '&amp;', s)  # & sueltos
    return s

def observaciones_APIMPC(asteroide):
    url = "https://data.minorplanetcenter.net/api/get-obs"
    payload = {
        "desigs": [asteroide],
        "output_format": ["XML"]
    }

    response = requests.get(url, json=payload)
    if not response.ok:
        raise RuntimeError(f"Error {response.status_code}: {response.content.decode()}")

    # Aquí accedemos a la clave 'XML' del JSON de respuesta
    data = response.json()
    xml_string = data[0].get("XML", "")
    if not xml_string:
        raise RuntimeError(f"No se encontró contenido XML para '{asteroide}'")
   
    # --- Primer intento: versión simple (como tu original) ---
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError:
        # --- Si falla, aplicamos blindaje ---
        xml_string = _sanitize_xml(xml_string)
        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            fname = f"xml_error_{asteroide}.xml"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(xml_string)
            raise RuntimeError(f"XML inválido para {asteroide}: {e}. Guardado en {fname}")

    # Extraemos observaciones dentro del tag <optical>
    observaciones = []
    for obs in root.findall(".//optical"):
        datos = {child.tag: child.text for child in obs}
        observaciones.append(datos)

    df = pd.DataFrame(observaciones)

    # Manejo robusto de fechas
    if "obsTime" in df.columns:
        df["obsTime"] = df["obsTime"].apply(parse_obs_time)

    return df[['obsTime','mag','band']]

def efemerides_API(asteroide, fecha_inicial, fecha_final):
  url = "https://ssd.jpl.nasa.gov/api/horizons_file.api"

  # Comandos estilo archivo .api
  horizons_input = f"""
  !$$SOF
  COMMAND='{asteroide};'
  OBJ_DATA='YES'
  MAKE_EPHEM='YES'
  TABLE_TYPE='OBSERVER'
  CENTER='500@399'
  START_TIME='{fecha_inicial}'
  STOP_TIME='{fecha_final}'
  STEP_SIZE='1 d'
  QUANTITIES='1,19,20,43'
  !$$EOF
  """

  # Enviar como parámetro 'input'
  response = requests.post(url, data={'input': horizons_input})
  data = response.json()

  # Paso 3: Extraer el contenido plano del resultado
  raw_result = data["result"]
  start_idx = raw_result.find('$$SOE')+6
  end_idx = raw_result.find('$$EOE')
  lines = raw_result[start_idx:end_idx].splitlines()

  date, delta, r, alpha = [], [], [], []
  for line in lines:
    date  = np.append(date, line[1:12].strip())
    delta = np.append(delta, float(line[76:93].strip()))
    r     = np.append(r, float(line[48:63].strip()))
    alpha = np.append(alpha, float(line[108:115].strip()))

  efe = pd.DataFrame({'Date':date,'Date JD': [Date_to_julian(i) for i in date],'Delta':delta,'r':r,'Fase':alpha})

  return efe
