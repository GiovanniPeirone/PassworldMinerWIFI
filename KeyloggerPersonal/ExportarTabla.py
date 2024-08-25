import mysql.connector

# Configuración de la conexión a la base de datos MySQL
db_config = {
    'user': 'root',            # Reemplaza con tu usuario de MySQL
    'password': 'proalafalda',      # Reemplaza con tu contraseña de MySQL
    'host': '127.0.0.1',              # O la IP de tu servidor MySQL
    'database': 'keylogger_db'        # El nombre de la base de datos que creaste
}

def is_printable_key(key):
    """Determina si la tecla es un carácter imprimible o un espacio."""
    return key.isalnum() or key in {' ', '.', ',', '!', '?', '-', '_', '(', ')', ':', ';', '"', "'", '/'}

def export_data_to_text_file():
    # Conectar a la base de datos
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Consultar todos los datos de la tabla
    cursor.execute("SELECT `key` FROM keystrokes")

    # Obtener todos los registros
    records = cursor.fetchall()

    # Nombre del archivo de salida
    output_file = 'KeyloggerPersonal\keystrokes_output.txt'

    # Procesar los datos y añadir espacios cuando sea necesario
    text_data = ''
    for record in records:
        key = record[0]
        if key == 'Key.space':
            text_data += ' '
        elif is_printable_key(key):
            text_data += key
        else:
            print(f"Entrada No Anotada {key}")

    # Escribir los datos en el archivo de texto
    with open(output_file, 'w') as file:
        file.write(text_data)

    print(f'Datos exportados a {output_file}')

    # Cerrar la conexión a la base de datos
    cursor.close()
    conn.close()

# Ejecutar la función para exportar los datos
export_data_to_text_file()

#'KeyloggerPersonal\keystrokes_output.txt'