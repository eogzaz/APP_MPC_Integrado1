import pandas as pd
import numpy as np
from utils import Date_to_julian, Date_to_julian_N
from data_obtention import periodo_fecha_perihelio

# Ver el documento "C:\Users\Asus\Desktop\APP_MPC_agrupados_version3\Corrección a la banda V programa.docx"
def Correccion_Banda(df):
  Correcciones={'V':0,
                'R':0.4,
                'G':0.28,
                'C':0.4,
                'r':0.14,
                'g':-0.35,
                'c':-0.05,
                'o':0.33,
                'w':-0.13,
                'i':0.32,
                'v':0,
                'Vj':0,
                'Rc':0.4,
                'Sg':-0.35,
                'Sr':0.14,
                'Si':0.32,
                'Pg':-0.35,
                'Pr':0.14,
                'Pi':0.32,
                'Pw':-0.13,
                'Ao':0.33,
                'Ac':-0.05,
                ''  :np.nan, # -0.8,
                'U' :np.nan, # -1.3,
                'u' :np.nan, # 2.5,
                'B' :np.nan, # -0,
                'I' :np.nan, # 0.8,
                'J' :np.nan, # 1.2,
                'H' :np.nan, # 1.4,
                'K' :np.nan, # 1.7,
                'W' :np.nan, # 0.4,
                'Y' :np.nan, # 0.7,
                'z' :np.nan, # 0.26,
                'y' :np.nan, # 0.32,
                'Lu':np.nan, #2.5,
                'Lg':np.nan, #-0.35,
                'Lr':np.nan, #0.14,
                'Lz':np.nan, #0.26,
                'Ly':np.nan, #0.32,
                'VR':np.nan, #0,
                'Ic':np.nan, #0.8,
                'Bj':np.nan, #-0.8,
                'Uj':np.nan, #-1.3,
                'Sz':np.nan, #0.26,
                'Pz':np.nan, #0.26,
                'Py':np.nan, #0.32,
                'Gb':np.nan,
                'Gr':np.nan,
                'N':np.nan,
                'T':np.nan,
                }
  
  magn_con_Banda = df['mag'].copy()
  #Corrección estándar para convertir una magnitud en cualquier banda a banda V
  for i in range(len(df)):
    for j in range(len(Correcciones)):
      if df['band'].iloc[i]==list(Correcciones.keys())[j]:
        magn_con_Banda.iloc[i]=float(df['mag'].iloc[i])+list(Correcciones.values())[j]
    
    if pd.isna(df['band'].iloc[i]):
      magn_con_Banda.iloc[i]=np.nan


  df['Magn_obs'] = magn_con_Banda
  df=df.dropna().reset_index(drop=True)

  return df


def Distancia_Perihelio(df_obs,periodo,fecha_perihelio):
  def condicion(fecha,period=periodo):
    if (fecha_perihelio-fecha)%period >= period/2:
        distacia_al_perihelio=period-((fecha_perihelio-fecha)%period)
    else:
        distacia_al_perihelio=-((fecha_perihelio-fecha)%period)
    return round(distacia_al_perihelio)

  df_obs['t-Tq'] = df_obs['Julian Day'].apply(condicion)
  return df_obs

def limpieza_obsevaciones(asteroide,df_obs_sin_limpiar, fecha_inicial, fecha_final):
  #Eliminar filas con almenos un NaN en la columna Magn y seleccion de las columnas que se van a usar
  df_obs_sin_nan= df_obs_sin_limpiar.dropna(subset=['mag'])[['obsTime','mag','band']].reset_index(drop=True)

  #Seleccion de solo las observaciones en Filtro V y R, y cambio de formato de fecha
  df_obs = Correccion_Banda(df_obs_sin_nan)

  #Agrego columna con dia juliano
  df_obs['Julian Day']=df_obs['obsTime'].apply(Date_to_julian)
  df_obs['Julian Day N']=df_obs['obsTime'].apply(Date_to_julian_N)



  #Rango de fechas
  df_obs=df_obs[(df_obs['Julian Day']>=Date_to_julian(fecha_inicial)) & (df_obs['Julian Day']<=Date_to_julian(fecha_final))]

  df_obs=df_obs.reset_index(drop=True)
    
  periodo, fecha_al_perihelio = periodo_fecha_perihelio(asteroide)
  df_obs=Distancia_Perihelio(df_obs,periodo,fecha_al_perihelio)

  return df_obs


def organizacion_df(df):
  df.insert(1, 'Anio', df['obsTime'].apply(lambda x: x.year))
  df.insert(2, 'Mes', df['obsTime'].apply(lambda x: x.month))
  df.insert(3, 'Dia', df['obsTime'].apply(lambda d:  round(d.day + d.hour / 24.0 + d.minute / (24.0 * 60.0) + d.second / (24.0 * 60.0 * 60.0) + d.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0),2)))
  df.drop(columns=['obsTime'], inplace=True)

  df['Delta'] = df['Delta'].apply(lambda x: round(x,2))
  df['r'] = df['r'].apply(lambda x: round(x,2))
  df['Fase'] = df['Fase'].apply(lambda x: round(x,2))
  df['Magn_obs'] = df['Magn_obs'].apply(lambda x: round(float(x),2))
  df['Magn_redu'] = df['Magn_redu'].apply(lambda x: round(x,2))

  return df

