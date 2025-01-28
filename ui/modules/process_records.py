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
    # Remover el slash final de la URL
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
    
def run():
    if "auth_token" not in st.session_state or not st.session_state["auth_token"]:
        st.error("Debe iniciar sesión para tener acceso a esta pagina.")
        st.stop()
    else:
        st.title("Obtención de datos Call Center")
        st.divider()
        st.header("Obtener un registro")
        st.info('Para empezar a realizar llamadas aplaste el boton Obtener Registro')

        user_id = st.session_state['id']

        # Formulario para respuestas si hay un registro activo
        if st.session_state["current_record"] is not None:
            with st.form(key='response_form'):
                st.subheader("Contesto la llamada?")
                respuesta = st.selectbox(
                    '¿Contestó la llamada?',
                    ['SI', 'NO', 'NO CONTESTA']
                )
                
                observaciones = st.text_input('Observaciones')
                
                if st.form_submit_button("Guardar Respuesta"):
                    if st.session_state["cod_junta"]:
                        # Actualizar estado
                        update_result = update_status(
                            st.session_state["cod_junta"],
                            respuesta,
                            observaciones
                        )
                        if update_result:
                            st.session_state["respuesta"] = respuesta
                            st.session_state["observaciones"] = observaciones
                            st.success("Respuesta guardada exitosamente")
                        else:
                            st.error("Error al guardar la respuesta")

        if st.button("Obtener Registro"):
            # Si hay un registro previo, procesar antes de obtener uno nuevo
            if st.session_state["record_id"] is not None:
                if st.session_state.get("respuesta"):
                    # Asegurarse de que el último estado se guarde
                    update_status(
                        str(st.session_state["cod_junta"]),
                        str(st.session_state["respuesta"]),
                        str(st.session_state.get("observaciones", ""))
                    )
                # Marcar como procesado
                mark_as_processed(st.session_state["record_id"], user_id)
            
            # Obtener nuevo registro
            record = get_record(user_id)
            if record and 'data' in record:
                st.session_state["record_id"] = record['record_id']
                datos_demograficos, datos_respuestas = dividir_datos(record['data'])
                st.session_state["cod_junta"] = datos_demograficos['cod_junta']
                st.session_state["current_record"] = datos_demograficos
                st.session_state["respuesta"] = None
                st.session_state["observaciones"] = None
                
                # Mostrar datos demográficos
                st.subheader("Datos")
                columnas_demo = st.columns(3)
                for i, (clave, valor) in enumerate(datos_demograficos.items()):
                    with columnas_demo[i % 3]:
                        html_content = f"""
                        <span style='font-size:18px; font-weight:bold; color:orange'>{clave}:</span>
                        <span style='font-size:16px;'>{valor}</span>
                        """
                        st.markdown(html_content, unsafe_allow_html=True)

                st.divider()
                
                # Aplicar estilos CSS
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
                
            else:
                st.error("No hay registros disponibles.")

        if st.session_state["record_id"] is not None:
            st.divider()
            st.divider()
            st.info('Utilizar este boton unicamente cuando se quiera guardar el registro y cerrar sesión al mismo tiempo')
            if st.button('Terminar Jornada'):
                if st.session_state.get("respuesta"):
                    update_status(
                        str(st.session_state["cod_junta"]),
                        str(st.session_state["respuesta"]),
                        str(st.session_state.get("observaciones", ""))
                    )
                mark_as_processed(st.session_state["record_id"], user_id)
                st.session_state["auth_token"] = None
                st.rerun()

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