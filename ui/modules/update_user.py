import pandas as pd
import requests
import streamlit as st
from modules.api_url import API_URL as API_BASE_URL

def run():
    if "auth_token" not in st.session_state or not st.session_state["auth_token"]:
        st.error("Debe iniciar sesión para tener acceso a esta pagina.")
        st.stop()
    else:
        st.title('Actualizar los datos de un usuario')
        st.subheader('Usuario a actualizar: ')
        usuario = st.text_input('Ingresar usuario')
        st.subheader('Datos: ')
        fullname = st.text_input('Ingresar nombre completo')
        password = st.text_input('Ingresar contraseña')
        if fullname or password:
            if st.button('Actualizar usuario'):
                update_user(usuario,fullname,password)

# Function to update a user
def update_user(username, fullname=None, password=None):
    # Construct the payload with optional values
    payload = {}
    if fullname:
        payload["fullname"] = fullname
    if password:
        payload["password"] = password
    
    if not payload:
        raise ValueError("At least one of 'fullname' or 'password' must be provided.")

    # Send the PUT request
    try:
        response = requests.put(
            f"{API_BASE_URL}/users/{username}/update",
            json=payload
        )
        # Check for successful response
        if response.status_code == 200:
            st.success("User updated successfully!")
            #st(response.json())
        else:
            st.error(f"Failed to update user: {response.status_code}")
            #st(response.json())
    except Exception as e:
        st.error(f"An error occurred: {e}")