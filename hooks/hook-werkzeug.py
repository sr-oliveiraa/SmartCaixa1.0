from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Coleta submódulos e dados necessários para Werkzeug
hiddenimports = collect_submodules('werkzeug')
datas = collect_data_files('werkzeug')
