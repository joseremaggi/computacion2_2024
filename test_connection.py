import mysql.connector

try:
    print("Iniciando la conexión a la base de datos...")

    # Intenta conectarte a MySQL sin la base de datos
    db_conn = mysql.connector.connect(
        host='localhost',
        user='root',  # Cambia por tu nombre de usuario
        password=''  # Deja esto vacío si no hay contraseña
    )
    print("Conexión exitosa a MySQL")

    # Cierra la conexión
    db_conn.close()

except mysql.connector.Error as err:
    print(f"Error de conexión: {err}")
