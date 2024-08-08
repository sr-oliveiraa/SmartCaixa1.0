from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Coleta submódulos e dados necessários para Flask
hiddenimports = collect_submodules('flask')
datas = collect_data_files('flask')
