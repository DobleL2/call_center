import requests
import streamlit as st
from modules.api_url import API_URL as API_BASE_URL
st.set_page_config(page_title='Sistema Registros',layout='wide')


def login(username, password):
    url = f"{API_BASE_URL}/login/"
    response = requests.post(url, data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()  # {"access_token": ..., "token_type": "bearer", "role": ...}
    else:
        return None

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None
    st.session_state["role"] = None
    st.session_state["username"] = None
    st.session_state['record_id'] = None

if not st.session_state["auth_token"]:
    st.title("Login")

if "auth_token" in st.session_state and st.session_state["auth_token"]:
    if st.sidebar.button("Logout"):
        st.session_state["auth_token"] = None
        st.rerun()

if st.session_state["auth_token"]:
    st.sidebar.info(f"Bienvenido {st.session_state['fullname']}.")
else:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = login(username, password)
        if token:
            st.session_state["auth_token"] = token["access_token"]
            st.session_state["role"] = token["role"]
            st.session_state["username"] = token["username"]
            st.session_state["fullname"] = token["fullname"]
            st.session_state["id"] = token["id"]
            st.success("Login successful!")
            st.session_state['record_id'] = None
            st.rerun()
        else:
            st.error("Invalid username or password")

import streamlit as st
from modules import *

ROLE_PAGES = {
    "super_admin": ["Crear Usuarios"], #"Cargar Datos", "Borrar Datos",,"Modificar datos usuario","Seleccionar Datos","Resumen de usuarios","Estado de Procesamiento","Buscar Registros"
    "admin": ["Crear Usuarios"],#"Cargar Datos",,"Modificar datos usuario","Seleccionar Datos","Resumen de usuarios","Estado de Procesamiento","Buscar Registros"
    "user": ["Procesar Registros"],
    "guest": []
}

st.sidebar.title("Menu")

if "auth_token" in st.session_state and st.session_state["auth_token"]:
    user_role = st.session_state["role"]
    available_pages = ROLE_PAGES.get(user_role, [])

    selected_page = st.sidebar.radio("Select a page:", available_pages)

    if selected_page == "Procesar Registros":
        import modules.process_records as process_records
        process_records.run()
    elif selected_page == "Crear Usuarios":
        import modules.create_user as create_user
        create_user.run()
        
    # if selected_page == "Cargar Datos":
    #     import modules.upload_and_create_table as upload_page
    #     upload_page.run()
    # elif selected_page == "Procesar Registros":
    #     import modules.process_records as process_page
    #     process_page.run()
    # elif selected_page == "Borrar Datos":
    #     import modules.delete_table as delete_page
    #     delete_page.run()
    # elif selected_page == "Crear Usuarios":
    #     import modules.create_user as create_user
    #     create_user.run()
    # elif selected_page == "Seleccionar Datos":
    #     import modules.select_table as select_table
    #     select_table.run()
    # elif selected_page == "Resumen de usuarios":
    #     import modules.users_resumen as users_resumen
    #     users_resumen.run()
    # elif selected_page == "Estado de Procesamiento":
    #     import modules.data_information as data_information
    #     data_information.run()
    # elif selected_page == "Buscar Registros":
    #     import modules.search_reigister as search_reigister
    #     search_reigister.run()
    # elif selected_page == "Modificar datos usuario":
    #     import modules.update_user as update_user
    #     update_user.run()
        
else:
    st.sidebar.info("Please log in to access the application.")
