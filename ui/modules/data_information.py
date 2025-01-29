import io
import pandas as pd
import requests
import streamlit as st
from datetime import datetime
from modules.api_url import API_URL as API_BASE_URL

def calcular_tiempo(assigned:str,processed:str):
    timestamp_format = "%Y-%m-%d %H:%M:%S"  
    if processed and assigned:
        processed = datetime.strptime(processed.split('.')[0],timestamp_format)
        assigned = datetime.strptime(assigned.split('.')[0],timestamp_format)
        difference = processed - assigned
        return difference.total_seconds()
    else:
        return None

def run():
    if "auth_token" not in st.session_state or not st.session_state["auth_token"]:
        st.error("Debe iniciar sesión para tener acceso a esta pagina.")
        st.stop()
    else:
        def get_users_resumen(table_name):
            response = requests.get(f"{API_BASE_URL}/dataset_status_information/", params={"dataset": table_name})
            return response.json()
        
        st.title("Información de registros procesados")
        st.info("En esta sección podra ver que registros se encuntran en progreso, cuales están procesados y cuales están pendientes",icon="ℹ️")
        table_name_to_select = 'data_processing'
        if st.button("Actualizar y mostrar resultados"):
            response = get_users_resumen(table_name_to_select)
            df_resume = pd.DataFrame(response['results'])
            df_resume['Tiempo(segundos)'] = df_resume.apply(lambda row: calcular_tiempo(row['assigned_at'], row['processed_at']), axis=1)
            df_resume = df_resume[
                ['id', 'status', 'assigned_to', 'full_name', 'username', 'assigned_at', 'processed_at'] +
                list(df_resume.columns[7:-1])
            ]
            st.write(df_resume)
            # Crear el botón de descarga
            st.download_button(
                label="Descargar registros procesados por usuarios en Excel",
                data=resumen_data(df_resume),
                file_name="production.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        
        
def resumen_data(df):
    # Guardar el DataFrame en un buffer de bytes
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="data")
    output.seek(0)
    
    return output