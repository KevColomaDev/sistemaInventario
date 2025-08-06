import sys
import os
from cx_Freeze import setup, Executable

# Directorio base
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, 'src')

# Archivos y directorios adicionales a incluir
include_files = [
    # Aquí puedes agregar archivos adicionales como imágenes, iconos, etc.
]

# Dependencias
build_exe_options = {
    'packages': [
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'sqlite3',
    ],
    'excludes': [],
    'include_files': include_files,
    'include_msvcr': True,  # Incluir runtime de Visual C++
    'optimize': 2,
}

# Configuración para Windows
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'  # Para aplicación sin consola

# Configuración del ejecutable
executables = [
    Executable(
        script=os.path.join(src_dir, 'main.py'),
        base=base,
        target_name='SistemaInventario',
        icon=os.path.join('resources', 'app_icon.ico') if os.path.exists(os.path.join('resources', 'app_icon.ico')) else None,
    )
]

# Configuración del setup
setup(
    name='Sistema de Inventario',
    version='1.0.0',
    description='Sistema de gestión de inventario',
    options={'build_exe': build_exe_options},
    executables=executables
)
