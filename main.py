from data_obtention import periodo_fecha_perihelio
from data_processing import *
from graficas import *
import streamlit as st
import datetime

st.set_page_config(layout="wide")
st.set_page_config(page_title="MPC down Rápido")
#st.title('Obtención de datos del MPC')
st.markdown("<h1 style='text-align: center'>(BETA) Datos para diagrama de fase y SLC Rápido</h2>", unsafe_allow_html=True)

asteroide = st.sidebar.text_input('Ingrese el número de algún asteroide que desea estudiar: ', value=None, 
                              placeholder='Ej: 1036',help='''
             _**Nota:** La cantidad de asteroides que tienen designado un
             número es *811552*, esto a la fecha 2025/07/11 
             (ultima actualizacion de esta app)_
             ''') #probar con st.number_input
    
#periodo y fecha del perihelio
col1,col2 = st.sidebar.columns(2)
with col1:
    fecha_inicial = str(st.date_input('Ingrese fecha de inicio', 
                                  value=datetime.date(1993, 1, 1),
                                  min_value=datetime.date(1800, 1, 1),
                                  max_value="today",
                                  help='''Desde esta fecha se tomaran las observaciones 
                                  del asteroide registradas en el MPC''')).replace('-',' ')
with col2:
    fecha_final = str(st.date_input('Ingrese fecha final',
                                        value="today",
                                        min_value=datetime.date(1800, 1, 1),
                                        max_value="today",
                                        help='''Hasta esta fecha se tomaran las observaciones
                                          del asteroide registradas en el MPC''')).replace('-',' ')

df_inicial = pd.DataFrame()

if asteroide == None :
   a=0
else:
    try:
        
        num = int(asteroide)
        
        if num<1 or num>826864:
           
           st.error("Por favor, ingresa un número entre 1 y 826864") 
        
        else:
            
            periodo, perihelio = periodo_fecha_perihelio(str(num))

            col3, col4, col5 = st.columns([1/3,1/3,1/3])
            with col3:
                st.subheader('Información')
                st.write(f"Asteroide ID: {num}")
                st.write(f"Nombre:")#pendiente
                st.write(f'Periodo: {periodo/365.25}')
                st.write(f'fecha del perihelio JD: {perihelio}')

    except ValueError:
        st.error("Por favor, ingresa un número válido.")
    
    else:
        asteroide=str(asteroide)
    

        with col4:
            st.subheader('Obtencion de datos')
            st.write(f'Desde {fecha_inicial.replace(' ','/')} hasta {fecha_final.replace(' ','/')}')
            #a=0
            col10, col11= st.columns(2)
            with col10:
                #a=0
                #if st.button("Obtener datos"):
                 #   a=1
                with st.spinner("_Procesando..._"):
                    df_inicial = obtencion_dataframe(asteroide, fecha_inicial, fecha_final)

                st.write('Filtros admitidos: ')
                Total_obs = len(df_inicial)
                st.write(f'Total observaciones: {Total_obs}')
            #with col11:
                #st.button("Reset", type="primary")

        def convert_for_download(df):
            return df.to_csv(sep='\t', index=False, header=False).encode("utf-8")
        txt = convert_for_download(df_inicial)
        with col5:
            st.subheader('Descarga de datos:')
            st.download_button(
                                    label="Descargar datos (.txt)",
                                    data=txt,
                                    file_name=asteroide + ".txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore"
                                )
                        
            df_sin_opo = fase_menor_5(df_inicial)
            txt1 = convert_for_download(df_sin_opo)
            st.download_button(
                                    label="Descargar datos sin incluir fases menores a 5° (.txt)",
                                    data=txt1,
                                    file_name=asteroide + ".txt",
                                    mime="text/csv",
                                    icon=":material/download:",
                                    on_click="ignore"
                                )
            
                

        if not df_inicial.empty:
            st.sidebar.divider()
            #Efecto de oposicion
            on_oposicion = st.sidebar.toggle("**Quitar efecto de oposición**",value=False)
            if on_oposicion:
                desde = float(st.sidebar.text_input('Quitar hasta: [°]',value=5))
                df = fase_menor_5(df_inicial,desde)
            else:
                df = df_inicial

            #Recta envolvente
            on_recta = st.sidebar.toggle("**Recta envolvente**",value=False)
            params_recta = calc_envolvente(df,bin_width=.1)
            pendiente_inicial = params_recta[0]
            intercepto_inicial = params_recta[1]
            alpha_max=  params_recta[2]
            magn_max= params_recta[3]

            col11,col12 = st.sidebar.columns(2)
            with col11:
                pendiente = float(st.text_input('Pendiente',value=round(pendiente_inicial,3)))
            with col12:
                intercepto = float(st.text_input('Intercepto',value=round(intercepto_inicial,2)))

            #Corrección por fase
            on_corrfase = st.sidebar.toggle("**Correción por fase**",value=False)
            df['Magn_Corr_Fase'] = df['Magn_redu']-pendiente*df['Fase']

            #Clasificacion por periodos
            on_colores = st.sidebar.toggle("**Colores periodos orbitales**",value=False)
            clasificacion, lim_peri = clasificacion_periodos(df,periodo,perihelio)
            if on_colores:
                fechas_periodos = [st.sidebar.checkbox(f'{julian_to_date(lim_peri[i+1])} - {julian_to_date(lim_peri[i])}',value=True) for i in range(len(lim_peri)-1)]
                #clasificacion_final=clasificacion.copy()
                for i in range(len(clasificacion)):
                    if fechas_periodos[i]==False:
                        clasificacion[i]=pd.DataFrame({'Anio':[],'Mes':[],'Dia':[],'t-Tq':[],'Delta':[],'r':[],'Fase':[],'Magn_obs':[],'Magn_redu':[],'Magn_Corr_Fase':[],'Date':[],'JD':[]})
                
            st.divider()
            # --- VISUALIZACIÓN DE GRÁFICOS ---
            col1, col2 = st.columns(2)

            #-------Curva de fase--------------------
            with col1:
                st.subheader("Curva de Fase")

                #Configuracion de grafico
                with st.sidebar.expander("⚙️ Configuración grafico de curva de fase"):
                    col3, col4, col5 = st.columns([0.2,0.4,0.4])
                    with col3:
                        st.write('**Eje X:**')
                    with col4:
                        xmin = st.text_input('X_Min',value=0)
                    with col5:
                        xmax = st.text_input('X_Max',value=int(max(df['Fase'])+2))
                    st.divider()
                    col6, col7, col8 = st.columns([0.2,0.4,0.4])
                    with col6:
                        st.write('**Eje Y:**')
                    with col7:
                        ymin = st.text_input('Y_Min',value=int(max(df['Magn_redu']))+1)
                    with col8:
                        ymax = st.text_input('Y_Max',value=int( min(df['Magn_redu'])-1))        
                
                limites_ejes = np.array([float(xmin),float(xmax),float(ymin),float(ymax)])
                params_recta = [pendiente,intercepto]
            
                #Graficos
                if on_recta:
                    intercepto1 = intercepto
                    if on_colores:
                        st.pyplot(grafica_fase_colores(clasificacion, title=asteroide,recta_pendiente=True, pendiente_param = params_recta, limites=limites_ejes))
                    else:
                        st.pyplot(grafica_fase(df, alpha_max, magn_max,title=asteroide,recta_pendiente=True, pendiente_param = params_recta, limites=limites_ejes))
                else:
                    intercepto1 = 1
                    if on_colores:
                        st.pyplot(grafica_fase_colores(clasificacion, title=asteroide, limites=limites_ejes))
                    else:
                        st.pyplot(grafica_fase(df, alpha_max, magn_max, title=asteroide,limites=limites_ejes))

            #-----------SLC----------------------------
            with col2:
                st.subheader(f'Curva de Luz Secular')
                
                #Configuración grafico
                with st.sidebar.expander("⚙️ Configuración grafico de SLC"):
                    col13, col14, col15 = st.columns([0.2,0.4,0.4])
                    with col13:
                        st.write('**Eje X:**')
                    with col14:
                        xmin_slc = st.text_input('X_Min',value=-max(abs(min(df['t-Tq'])),abs(max(df['t-Tq'])))-20)
                    with col15:
                        xmax_slc = st.text_input('X_Max',value= max(abs(min(df['t-Tq'])),abs(max(df['t-Tq'])))+20)
                    st.divider()
                    col16, col17, col18 = st.columns([0.2,0.4,0.4])
                    with col16:
                        st.write('**Eje Y:**')
                    with col17:
                        ymin_slc = st.text_input('Y_Min',value=int(max(df['Magn_redu']))+1,key=1)
                    with col18:
                        ymax_slc = st.text_input('Y_Max',value=int( min(df['Magn_redu'])-1),key=2)
                        
                limites_ejes_slc = np.array([float(xmin_slc),float(xmax_slc),float(ymin_slc),float(ymax_slc)])    

                #graficos
                if on_corrfase:
                    if on_colores:
                        st.pyplot(SLC_colores_corr(clasificacion, title=asteroide,familia=None,intercepto=intercepto1,limites=limites_ejes_slc))
                    else:
                        st.pyplot(grafica_SLC_corr(df, title=asteroide,familia=None,intercepto=intercepto1,limites=limites_ejes_slc))
                
                else:
                    if on_colores:
                        st.pyplot(SLC_colores(clasificacion, title=asteroide,familia=None,intercepto=intercepto1,limites=limites_ejes_slc))
                    else:
                        st.pyplot(grafica_SLC(df, title=asteroide,familia=None,intercepto=intercepto1,limites=limites_ejes_slc))



