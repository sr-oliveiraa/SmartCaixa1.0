import subprocess
import webbrowser
import time
import os

# Caminho para o script do servidor Flask
flask_script = 'app.py'

# Inicie o servidor Flask em um subprocesso
process = subprocess.Popen(['python3', flask_script])

# Aguarde um momento para garantir que o servidor Flask inicie
time.sleep(5)  # Ajuste o tempo conforme necessário

# Abra o navegador no endereço do servidor Flask
webbrowser.open('http://127.0.0.1:13400')

# Opcional: aguarde o processo Flask terminar (não necessário, mas pode ser útil)
process.wait()
import subprocess
import webbrowser
import time
import os

# Caminho para o script do servidor Flask
flask_script = 'app.py'

# Inicie o servidor Flask em um subprocesso
process = subprocess.Popen(['python3', flask_script])

# Aguarde um momento para garantir que o servidor Flask inicie
time.sleep(5)  # Ajuste o tempo conforme necessário

# Abra o navegador no endereço do servidor Flask
webbrowser.open('http://127.0.0.1:13400')

# Opcional: aguarde o processo Flask terminar (não necessário, mas pode ser útil)
process.wait()
