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

def update_status(cod_junta, estado, observaciones):
    url = f"{API_BASE_URL}/update_status"
    response = requests.post(
        url,
        json={
            "cod_junta": str(cod_junta),
            "estado": str(estado),
            "observaciones": str(observaciones)
        }
    )
    return response.json()
def run():
    if "auth_token" not in st.session_state or not st.session_state["auth_token"]:
        st.error("Debe iniciar sesión para tener acceso a esta pagina.")
        st.stop()
    else:
        def unprocess_junta(cod_junta):
            response = requests.post(f"{API_BASE_URL}/change_processing_rows/", json={"cod_junta": str(cod_junta)})
            return response.json()
        
        st.title("Información de registros procesados")
        st.info("Poner un registro como no procesado",icon="ℹ️")
        cod_junta = st.text_input('Numero de junta')
        if st.button("Poner junta como no procesada"):
            response = unprocess_junta(cod_junta)
            st.write(response)
            #if response.status_code ==200:
            #    st.success(response['message'])
            #else:
            #    st.write("Avisar a soporte")
        
        def unprocess_no_contestaron():
            response = requests.post(f"{API_BASE_URL}/change_processing_rows_no_contestaron/")
            if response.status_code == 200:
                st.success("Todos los registros que estaban marcados como no contestaron volvieron a la cola")  
            else:
                st.warning("No se pudo volver a la cola a registros que no contestaron")
            return response.json()
        st.header("Regresar todos los registros que no contestaron a la cola")
        if st.button("Poner todos los que no contestaron como no procesados"):
            response = unprocess_no_contestaron()

        
def resumen_data(df):
    # Guardar el DataFrame en un buffer de bytes
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="data")
    output.seek(0)
    
    return output