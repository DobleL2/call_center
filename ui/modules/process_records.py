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

def update_status(cod_junta,estado, observaciones):
    response = requests.post(
        f"{API_BASE_URL}/update_status/",
        json={"cod_junta": str(cod_junta), "estado": str(estado),"observaciones": str(observaciones)}
    )
    return response.json()


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

        if st.button("Obtener Registro"):
            if st.session_state['record_id'] != None:
                mark_as_processed(int(st.session_state['record_id']), str(user_id))
            record = get_record(user_id)
            if record and 'data' in record:
                st.session_state['record_id'] = record['record_id']
                datos_demograficos, datos_respuestas = dividir_datos(record['data'])

                # Mostrar datos demográficos en 3 columnas
                st.subheader("Datos")
                columnas_demo = st.columns(3)
                for i, (clave, valor) in enumerate(datos_demograficos.items()):
                    with columnas_demo[i % 3]:
                        html_content = f"""
                        <span style='font-size:18px; font-weight:bold; color:orange'>{clave}:</span>
                        <span style='font-size:16px;'>{valor}</span>
                        """
                        st.markdown(html_content, unsafe_allow_html=True)

                st.divider()  # Línea divisoria
                # Mostrar datos de respuestas en una tabla de 5 columnas
                st.subheader("Contesto la llamada?")
                # CSS para estilizar la tabla
                st.markdown(
                    """
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
                    """,
                    unsafe_allow_html=True
                )
                with st.form("mi_formulario"):
                    # Agregar un selectbox
                    respuesta = st.selectbox('¿Contestó la llamada?', ['SI', 'NO', 'NO CONTESTA'])
                    # Agregar un campo de texto para observaciones
                    observaciones = st.text_input('Observaciones')
                    
                    # Botón para enviar el formulario
                    submit = st.form_submit_button("Enviar")

                # Llamar a la API si se envía el formulario
                if submit:
                    try:
                        update_status(datos_demograficos['cod_junta'],respuesta,observaciones)
                    except Exception as e:
                        st.error("Error al conectar con la API.")
                        st.write(e)
                
            else:
                st.error("No hay registros disponibles.")
        if st.session_state['record_id'] != None:
            st.divider()
            st.divider()
            st.info('Utilizar este boton unicamente cuando se quiera guardar el registro y cerrar sesión al mismo tiempo')
            if st.button('Terminar Jornada'):
                mark_as_processed(int(st.session_state['record_id']), str(user_id))
                st.session_state["auth_token"] = None
                st.rerun()

import re

# Función para dividir los datos en demográficos y respuestas
def dividir_datos(datos):
    datos_demograficos = {}
    datos_respuestas = {}
    for clave, valor in datos.items():
        if re.match(r'^ppppP', clave):  # Claves que comienzan con 'P'
            datos_respuestas[clave] = valor
        else:
            datos_demograficos[clave] = valor
    return datos_demograficos, datos_respuestas