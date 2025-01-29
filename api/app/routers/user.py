from datetime import datetime
import pytz
from app.configs.token import create_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserRead, Token
from fastapi import APIRouter,Depends ,HTTPException
from app.crud.user import get_user_by_username, create_user
from app.configs.database import get_sql_connection, update_local_database,upload_excel_to_sqlite,get_db
from app.configs.security import hash_password, verify_password
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.users import User

router = APIRouter()

@router.get("/user")
def read_user():
    return {"username": "fakeuser"}

@router.get("/")
def home():
    return {"holi": "fakeuser"}

class UpdateUserRequest(BaseModel):
    fullname: str = None
    password: str = None

@router.put("/users/{username}/update")
def update_user(username: str, request: UpdateUserRequest, db: Session = Depends(get_db)):
    """
    Endpoint para actualizar el fullname y/o contraseña de un usuario.
    
    Args:
        username (int): ID del usuario que se desea actualizar.
        request (UpdateUserRequest): Datos opcionales a actualizar (fullname, password).
        db (Session): Sesión de la base de datos.
        
    Returns:
        dict: Confirmación de la operación.
    """
    # Obtener al usuario de la base de datos
    user = db.query(User).filter(User.username == username,User.role!='super_admin',User.role!='admin').first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Verificar qué campos se enviaron en la solicitud y actualizarlos
    if request.fullname is not None:
        user.full_name = request.fullname
    if request.password is not None:
        user.hashed_password = hash_password(request.password)
    
    # Si no se enviaron datos, lanzar una excepción
    if request.fullname is None and request.password is None:
        raise HTTPException(status_code=400, detail="No data provided to update.")
    
    # Guardar los cambios
    try:
        db.commit()
        return {"message": f"User {username} updated successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")

@router.get("/update_db")
def update_db():
    try:
        update_local_database()
        return {"response": "db updated"}
    except Exception as e:
        return {"response": f"An error occurred: {e}"}


@router.get("/dataset_status_information/")
def get_dataset_status_information(dataset:str,db:Session= Depends(get_db)):
    query = text(f"""
                SELECT full_name,username,d.*
                FROM {dataset} d
                LEFT JOIN users u ON u.id = d.assigned_to
                 """)
    existing_record = db.execute(query).mappings().fetchall()
    return {
        "results": existing_record
    }

@router.get("/dataset_general_information/")
def get_dataset_status_information(db:Session= Depends(get_db)):
    query = text(f"""
                WITH cte AS (
                    SELECT COD_JUNTA, ESTADO,OBSERVACION
                    FROM mi_tabla_desde_excel
                )
                SELECT *
                FROM data_estrategas d
                JOIN cte AS c ON c.COD_JUNTA = d.cod_junta
                 """)
    existing_record = db.execute(query).mappings().fetchall()
    return {
        "results": existing_record
    }

@router.get("/update_table_excel")
def update_table_excel():
    try:
        # Ruta del archivo Excel
        excel_path = "app/data/data.xlsx"

        # Ruta de la base de datos SQLite
        sqlite_path = "local_database.sqlite"

        # Nombre de la tabla
        sqlite_table = "mi_tabla_desde_excel"

        # Subir los datos del Excel a SQLite
        upload_excel_to_sqlite(excel_path, sqlite_path, sqlite_table)
        return {"response": "Excel uploaded to SQLite"}
    except Exception as e:
        return {"response": f"An error occurred: {e}"}

@router.get("/check_connection")
def check_connection():
    """
    Endpoint to check the database connection.

    Returns:
        JSONResponse: Response indicating connection status.
    """
    try:
        connection = get_sql_connection()
        if connection:
            connection.close()  # Close the connection after checking
            return JSONResponse(
                status_code=200,
                content={"message": "Database connection successful."}
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"message": "Failed to connect to the database."}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {e}"}
        )
        
class UpdateUserRequest(BaseModel):
    fullname: str = None
    password: str = None

@router.put("/users/{username}/update")
def update_user(username: str, request: UpdateUserRequest, db: Session = Depends(get_db)):
    """
    Endpoint para actualizar el fullname y/o contraseña de un usuario.
    
    Args:
        username (int): ID del usuario que se desea actualizar.
        request (UpdateUserRequest): Datos opcionales a actualizar (fullname, password).
        db (Session): Sesión de la base de datos.
        
    Returns:
        dict: Confirmación de la operación.
    """
    # Obtener al usuario de la base de datos
    user = db.query(User).filter(User.username == username,User.role!='super_admin',User.role!='admin').first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Verificar qué campos se enviaron en la solicitud y actualizarlos
    if request.fullname is not None:
        user.full_name = request.fullname
    if request.password is not None:
        user.hashed_password = hash_password(request.password)
    
    # Si no se enviaron datos, lanzar una excepción
    if request.fullname is None and request.password is None:
        raise HTTPException(status_code=400, detail="No data provided to update.")
    
    # Guardar los cambios
    try:
        db.commit()
        return {"message": f"User {username} updated successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")


@router.post("/users/", response_model=UserRead)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(user.password)
    return create_user(db, user, hashed_password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


@router.post("/login/", response_model=Token)
def login_endpoint(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # Generar el token de acceso
    access_token = create_access_token(data={"sub": user.username})
    
    # Retornar el token junto con los datos adicionales del usuario
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "fullname": user.full_name,
        "role": user.role,
        "id": user.id
    }
    
from app.models.users import Base
from app.configs.database import engine
import pandas as pd
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.sql import text

@router.get("/create_tables")
def create_tables():
    Base.metadata.create_all(bind=engine)
    return {"message": "Tables created successfully."}
from sqlalchemy import inspect

@router.post("/add_table_from_query/")
def add_table_from_query(db: Session = Depends(get_db)):
    """
    Endpoint para crear una nueva tabla en la base de datos a partir de los resultados de una consulta SQL,
    agregando columnas adicionales de control.
    """
    # Validar nombre de tabla
    table_name = 'data_processing'
    query = """
            SELECT * 
            FROM data_estrategas
            WHERE cedula IS NOT NULL 
                AND num_celular IS NOT NULL
                AND cod_junta NOT IN (
                    SELECT COD_JUNTA 
                    FROM mi_tabla_desde_excel 
                    WHERE COD_JUNTA IS NOT NULL
                        AND ESTADO IS NOT NULL
            );
    """

    if not table_name.isidentifier():
        raise HTTPException(
            status_code=400,
            detail="Invalid table name. The table name must be a valid Python identifier."
        )

    # Ejecutar la consulta SQL para obtener los datos
    try:
        result = db.execute(text(query))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="The query returned no data.")

    # Verificar si la tabla ya existe y eliminarla si es necesario
    inspector = inspect(db.get_bind())
    if table_name in inspector.get_table_names():
        try:
            db.execute(text(f"DROP TABLE {table_name}"))
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error dropping existing table: {e}")

    # Crear la nueva tabla
    metadata = MetaData()
    columns = [
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("status", String, default="unprocessed"),
        Column("assigned_to", String, nullable=True),
        Column("assigned_at", String, nullable=True),
        Column("processed_at", String, nullable=True),
    ]

    # Agregar dinámicamente columnas basadas en las claves del DataFrame
    for col in df.columns:
        columns.append(Column(col, String))  # Ajustar tipos según los datos reales

    table = Table(table_name, metadata, *columns)
    try:
        metadata.create_all(db.get_bind())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating table: {e}")

    # Insertar datos en la nueva tabla
    try:
        records = df.to_dict(orient="records")
        for record in records:
            record["status"] = "unprocessed"  # Configurar estado inicial
        db.execute(table.insert(), records)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error inserting data: {e}")

    return {"message": f"Table '{table_name}' recreated successfully with {len(df)} records."}




@router.get("/get_record/")
def get_record(user_id: str, db: Session = Depends(get_db)):
    """
    Endpoint para obtener un registro no procesado y asignarlo a un usuario.
    Si el usuario tiene un registro en 'in_progress', se le asigna ese mismo registro nuevamente.
    """
    table_name = 'data_processing'
    if table_name:
        existing_query = text(f"""
            SELECT * 
            FROM {table_name}
            WHERE status = 'in_progress' AND assigned_to = :user_id
            LIMIT 1
        """)
        existing_record = db.execute(existing_query, {"user_id": user_id}).mappings().fetchone()

        if existing_record:
            # Actualizar la hora de asignación del registro existente
            update_existing_query = text(f"""
                UPDATE {table_name}
                SET assigned_at = :assigned_at
                WHERE id = :record_id
            """)
            
            # Convertir el tiempo actual en UTC a UTC-5
            utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
            utc_minus_5 = pytz.timezone('America/Lima')  # Ejemplo para una región en UTC-5
            assigned_at = utc_now.astimezone(utc_minus_5)        
            db.execute(
                update_existing_query,
                {
                    "assigned_at": assigned_at,
                    "record_id": existing_record["id"],
                }
            )
            db.commit()

            # Retornar el registro existente
            return {
                "record_id": existing_record["id"],
                "data": {col: existing_record[col] for col in existing_record.keys() if col not in ["id", "status", "assigned_to", "assigned_at", "processed_at"]},
                "assigned_to": user_id,
                "assigned_at": assigned_at.isoformat(),
            }

        # Si no tiene un registro en progreso, buscar un nuevo registro no procesado
        new_query = text(f"""
            SELECT * 
            FROM {table_name}
            WHERE status = 'unprocessed'
            LIMIT 1
        """)
        new_record = db.execute(new_query).mappings().fetchone()

        if not new_record:
            raise HTTPException(status_code=404, detail="No unprocessed records available.")

        # Asignar el nuevo registro al usuario
        assign_query = text(f"""
            UPDATE {table_name}
            SET status = 'in_progress', assigned_to = :user_id, assigned_at = :assigned_at
            WHERE id = :record_id
        """)
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_minus_5 = pytz.timezone('America/Lima')  # Ejemplo para una región en UTC-5
        assigned_at = utc_now.astimezone(utc_minus_5)   
        
        db.execute(
            assign_query,
            {
                "user_id": user_id,
                "assigned_at": assigned_at,
                "record_id": new_record["id"],
            }
        )
        db.commit()

        # Retornar el nuevo registro asignado
        return {
            "record_id": new_record["id"],
            "data": {col: new_record[col] for col in new_record.keys() if col not in ["id", "status", "assigned_to", "assigned_at", "processed_at"]},
            "assigned_to": user_id,
            "assigned_at": assigned_at.isoformat(),
        }
    else:
        return None


class MarkAsProcessedRequest(BaseModel):
    record_id: int
    user_id: str

class UpdateStatus(BaseModel):
    cod_junta: str
    estado: str
    observaciones: str


@router.post("/update_status")
def update_status( request: UpdateStatus,db:Session = Depends(get_db)):
    # Marcar el registro como procesado
    cod_junta = request.cod_junta
    estado = request.estado
    observaciones = request.observaciones
    update_query = text(f"""
        UPDATE mi_tabla_desde_excel
        SET ESTADO = "{estado}",OBSERVACION = "{observaciones}"
        WHERE COD_JUNTA = {cod_junta}
    """)
    db.execute(update_query)
    db.commit()
    
    update_query_2 = text(f"""
        UPDATE tabla_observaciones
        SET ESTADO = "{estado}", observaciones = "{observaciones}"
        WHERE COD_JUNTA = {cod_junta}
    """)
    db.execute(update_query_2)
    db.commit()
    return {"message": f"Record {cod_junta} marked as processed successfully."}

class Change(BaseModel):
    cod_junta: str
    

@router.post("/change_processing_rows")
def change_processing_rows(request: Change,db:Session = Depends(get_db)):
    # Marcar el registro como procesado
    cod_junta = request.cod_junta
    update_query = text(f"""
        UPDATE data_processing
        SET status = "unprocessed", assigned_to = NULL, assigned_at = NULL, processed_at = NULL
        WHERE COD_JUNTA = {cod_junta}
    """)
    db.execute(update_query)
    db.commit()
    update_query = text(f"""
        UPDATE mi_tabla_desde_excel
        SET ESTADO = NULL ,OBSERVACION = NULL
        WHERE COD_JUNTA = {cod_junta}
    """)
    db.execute(update_query)
    db.commit()
    return {"message": f"Record {cod_junta} marked as processed successfully."}


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import MetaData, Table, Column, String, Integer, text
from sqlalchemy.orm import Session
from app.configs.database import get_db
import pandas as pd

@router.post("/create_table_with_multiple_columns/")
def create_table_with_multiple_columns(
    source_table: str, 
    source_columns: list[str], 
    new_table_name: str, 
    db: Session = Depends(get_db)
):
    """
    Endpoint para crear una nueva tabla basada en múltiples columnas de otra tabla
    y añadir una columna adicional llamada 'observaciones'.

    Args:
        source_table (str): Nombre de la tabla fuente.
        source_columns (list[str]): Lista de nombres de columnas de la tabla fuente.
        new_table_name (str): Nombre de la nueva tabla.
        db (Session): Sesión de la base de datos.

    Returns:
        dict: Mensaje de confirmación.
    """
    if not new_table_name.isidentifier():
        raise HTTPException(status_code=400, detail="Invalid table name.")
    
    if not source_columns:
        raise HTTPException(status_code=400, detail="No columns specified.")

    # Validar los nombres de las columnas
    source_columns_str = ", ".join(source_columns)

    try:
        # Extraer datos de las columnas seleccionadas de la tabla fuente
        query = text(f"SELECT DISTINCT {source_columns_str} FROM {source_table}")
        result = db.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=source_columns)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading source table: {e}")

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found in the source table.")

    # Crear la nueva tabla con las columnas seleccionadas y 'observaciones'
    metadata = MetaData()
    columns = [
        Column("id", Integer, primary_key=True, autoincrement=True),
        *[Column(col, String, nullable=True) for col in source_columns],
        Column("observaciones", String, nullable=True)
    ]
    new_table = Table(new_table_name, metadata, *columns)

    try:
        # Verificar si la tabla ya existe y eliminarla si es necesario
        inspector = inspect(db.get_bind())
        if new_table_name in inspector.get_table_names():
            db.execute(text(f"DROP TABLE {new_table_name}"))
            db.commit()

        # Crear la tabla
        metadata.create_all(db.get_bind())

        # Insertar los datos
        df["observaciones"] = None  # Añadir columna 'observaciones' con valores nulos
        records = df.to_dict(orient="records")
        db.execute(new_table.insert(), records)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating or inserting data into the table: {e}")

    return {"message": f"Table '{new_table_name}' created successfully with {len(df)} records."}

@router.post("/mark_as_processed/")
def mark_as_processed(request: MarkAsProcessedRequest, db: Session = Depends(get_db)):
    """
    Endpoint para marcar un registro como 'processed'.

    Args:
        record_id (int): ID del registro que se procesará.
        user_id (str): ID del usuario que marca el registro como procesado.
        db (Session): Sesión de la base de datos.

    Returns:
        dict: Confirmación de la operación.
    """
    table_name = 'data_processing'
    record_id = request.record_id
    user_id = request.user_id
    # Verificar si el registro existe y está en progreso
    query = text(f"""
        SELECT * 
        FROM {table_name}
        WHERE id = :record_id AND status = 'in_progress' AND assigned_to = :user_id
    """)
    record = db.execute(query, {"record_id": record_id, "user_id": user_id}).mappings().fetchone()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Record not found or not in progress."
        )

    # Marcar el registro como procesado
    update_query = text(f"""
        UPDATE {table_name}
        SET status = 'processed', processed_at = :processed_at
        WHERE id = :record_id
    """)
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    utc_minus_5 = pytz.timezone('America/Lima')  # Ejemplo para una región en UTC-5
    processed_at = utc_now.astimezone(utc_minus_5)   
    db.execute(
        update_query,
        {
            "processed_at": processed_at,
            "record_id": record_id,
        }
    )
    db.commit()

    return {"message": f"Record {record_id} marked as processed successfully by user {user_id}."}