import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_obtention import observaciones_APIMPC, efemerides_API
from data_cleansing import limpieza_obsevaciones, organizacion_df
import streamlit as st

@st.cache_data(show_spinner=False)
def obtencion_dataframe(asteroide, fecha_inicial='1980 01 01', fecha_final='2025 07 12'):
  #Obtencion de datos obsrvacionales MPC
  df_obs = limpieza_obsevaciones(asteroide,observaciones_APIMPC(asteroide),fecha_inicial,fecha_final)

  #Obtención efemerides
  df_efeme = efemerides_API(asteroide,fecha_inicial,fecha_final)

  #dataframe total
  df_total=pd.merge(df_obs, df_efeme, left_on='Julian Day N', right_on='Date JD', how='inner')[['obsTime','t-Tq','Delta','r','Fase','Magn_obs']]
  #df_total = df_total.rename(columns={'Magn corregiada a banda V': 'Magn'})
  df_total['Magn_redu'] = df_total['Magn_obs'].astype(float) - 5*np.log10(df_total['r']*df_total['Delta'])

  return organizacion_df(df_total)

# Función de filtrado
def fase_menor_5(data_sin_editar):
  data = data_sin_editar.copy()
  fase = data['Fase'].to_numpy()
  data['Fase'] = np.where(fase < 5, np.nan, fase)
  
  return data.dropna().reset_index(drop=True)

