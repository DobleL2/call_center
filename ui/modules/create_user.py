import streamlit as st
import pandas as pd
import io
import requests
from modules.api_url import API_URL

def create_user(username, password, full_name,role):
    """
    Envía una solicitud POST al endpoint de FastAPI para crear un usuario.
    """
    payload = {
        "username": username,
        "password": password,
        "full_name": full_name,  # Cambiado a full_name
        "role":role
    }
    response = requests.post(f"{API_URL}/users/", json=payload)
    if response.status_code == 200:
        st.success(f"Usuario {username} agregado exitosamente al sistema.") 
        #return response.json()
    else:
        st.error(f"El usuario {username} ya se encuentra dentro de la base de datos.")
        #st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        return None

# Diseño de la página de Streamlit
def run():
    st.title("Crear nuevos usuarios")
    if "auth_token" not in st.session_state or not st.session_state["auth_token"]:
        st.error("Debe iniciar sesión para tener acceso a esta pagina.")
        st.stop()
    else:
        st.info("En esta sección podra ingresar uno o various usuarios en la aplicación",icon="ℹ️")
        cantidad = st.radio("Cantidad de usuarios a agregar",options=['Un usuario','Varios usuarios'],horizontal=True,label_visibility="hidden")
        
        if cantidad == 'Un usuario':
            # Inputs de usuario
            username = st.text_input("Username", placeholder="Enter a username")
            fullname = st.text_input("Full Name", placeholder="Enter the full name")
            password = st.text_input("Password", type="password", placeholder="Enter a secure password")
            if st.session_state["role"] == 'admin':
                role = "user"
            elif st.session_state["role"] == 'super_admin':
                role = st.selectbox("Tipo de usuario: ",options=['user','admin'])
            
            
            # Botón para crear usuario
            if st.button("Create User"):
                if username and password and fullname:
                    with st.spinner("Creating user..."):
                        response = create_user(username, password, fullname,role)
                        if response:
                            st.success(f"User '{response['username']}' created successfully!")
                else:
                    st.warning("Please fill out all fields before submitting.")
        elif cantidad == "Varios usuarios":
            # Configurar la aplicación Streamlit
            st.subheader("Descarga de Plantilla en Excel")

            # Crear el botón de descarga
            st.download_button(
                label="Descargar plantilla en Excel para agregar multiples usuarios",
                data=crear_plantilla(),
                file_name="plantilla.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
            uploaded_file = st.file_uploader('Agregar lista de usuarios a agregar al sistema',type=['xlsx'])
            if uploaded_file:
                users = pd.read_excel(uploaded_file)
                if users.columns.tolist() != ['Nombre de usuario','Nombre Completo','Contraseña']:
                    st.warning('Formato de archivo subido incorrecto (Revisar plantilla)')
                else:    
                    st.subheader('Usuarios que se ingresaran al sistema')
                    st.write(users)
                    
                    usuarios_ok = []
                    repeated_users = []
                    if st.button('Confirmar ingreso de nuevos usuarios'):
                        for _,row in users.iterrows():
                            create_user(str(row['Nombre de usuario']), str(row['Contraseña']),str(row['Nombre Completo']),'user')

    
def crear_plantilla():
    # Crear un DataFrame de ejemplo
    data = {
        "Nombre de usuario": ["user_1", "user_2"],
        "Nombre Completo": ["Usuario 1",'Usuario 2'],
        "Contraseña": ["contra1", "contra2"],
    }
    df = pd.DataFrame(data)
    
    # Guardar el DataFrame en un buffer de bytes
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Plantilla")
    output.seek(0)
    
    return output