import requests
import streamlit as st
from modules.api_url import API_URL as API_BASE_URL

def get_record(user_id):
    response = requests.get(f"{API_BASE_URL}/get_record/", params={"user_id": user_id})
    return response.json()

def mark_as_processed(record_id, user_id):
    response = requests.post(
        f"{API_BASE_URL}/mark_as_processed/",
        json={"record_id": int(record_id), "user_id": str(user_id)}
    )
    return response.json()

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

def get_next_record(user_id, current_record_id=None, current_cod_junta=None, respuesta=None, observaciones=None):
    if current_record_id is not None:
        if respuesta is not None:
            update_status(
                str(current_cod_junta),
                str(respuesta),
                str(observaciones or "")
            )
        mark_as_processed(current_record_id, user_id)
    
    record = get_record(user_id)
    if record and 'data' in record:
        return record
    return None



def increment_form_key():
    st.session_state["form_key"] += 1

def run():
    # Inicializar variables en session_state
    if "cod_junta" not in st.session_state:
        st.session_state["cod_junta"] = None
        
    if "respuesta" not in st.session_state:
        st.session_state["respuesta"] = None    

    if "observaciones" not in st.session_state:
        st.session_state["observaciones"] = None

    if "current_record" not in st.session_state:
        st.session_state["current_record"] = None

    if "record_id" not in st.session_state:
        st.session_state["record_id"] = None

    if "form_key" not in st.session_state:
        st.session_state["form_key"] = 0
    if "auth_token" not in st.session_state or not st.session_state["auth_token"]:
        st.error("Debe iniciar sesión para tener acceso a esta pagina.")
        st.stop()
    else:
        st.title("Obtención de datos Call Center")
        st.divider()
        st.header("Obtener un registro")
        st.info('Para empezar a realizar llamadas aplaste el boton Obtener Registro')

        user_id = st.session_state['id']

        if st.session_state["current_record"] is None and st.button("Obtener Registro"):
            record = get_next_record(user_id)
            if record:
                st.session_state["record_id"] = record['record_id']
                datos_demograficos, datos_respuestas = dividir_datos(record['data'])
                st.session_state["cod_junta"] = datos_demograficos['cod_junta']
                st.session_state["current_record"] = datos_demograficos
                increment_form_key()
                st.rerun()

        if st.session_state["current_record"] is not None:
            st.subheader("Datos")
            columnas_demo = st.columns(3)
            for i, (clave, valor) in enumerate(st.session_state["current_record"].items()):
                with columnas_demo[i % 3]:
                    html_content = f"""
                    <span style='font-size:18px; font-weight:bold; color:orange'>{clave}:</span>
                    <span style='font-size:16px;'>{valor}</span>
                    """
                    st.markdown(html_content, unsafe_allow_html=True)

            st.divider()

            # Usar form_key para crear un nuevo formulario cada vez
            with st.form(key=f'response_form_{st.session_state["form_key"]}'):
                st.subheader("Contesto la llamada?")
                respuesta = st.selectbox(
                    '¿Contestó la llamada?',
                    ['SI', 'NO', 'NO CONTESTA']
                )
                
                observaciones = st.text_input('Observaciones')
                
                if st.form_submit_button("Guardar y Siguiente"):
                    next_record = get_next_record(
                        user_id,
                        st.session_state["record_id"],
                        st.session_state["cod_junta"],
                        respuesta,
                        observaciones
                    )
                    
                    if next_record:
                        st.session_state["record_id"] = next_record['record_id']
                        datos_demograficos, datos_respuestas = dividir_datos(next_record['data'])
                        st.session_state["cod_junta"] = datos_demograficos['cod_junta']
                        st.session_state["current_record"] = datos_demograficos
                        increment_form_key()  # Incrementar la clave del formulario
                        st.success("Respuesta guardada y nuevo registro obtenido")
                        st.rerun()
                    else:
                        st.error("No hay más registros disponibles")

            st.markdown("""
                <style>
                .styled-table {
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 18px;
                    text-align: left;
                    width: 100%;
                }
                .styled-table th, .styled-table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }
                .styled-table th {
                    background-color: #009879;
                    color: white;
                    font-weight: bold;
                }
                .styled-table tr:nth-child(even) {
                    background-color: #f3f3f3;
                }
                .styled-table td {
                    background-color: #f9f9f9;
                }
                </style>
            """, unsafe_allow_html=True)

import re
def dividir_datos(datos):
    datos_demograficos = {}
    datos_respuestas = {}
    for clave, valor in datos.items():
        if re.match(r'^ppppP', clave):
            datos_respuestas[clave] = valor
        else:
            datos_demograficos[clave] = valor
    return datos_demograficos, datos_respuestas