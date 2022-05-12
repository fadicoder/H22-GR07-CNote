from cx_Freeze import setup, Executable
base = None
executables = [Executable("src/main.py", base=base)]
packages = ["idna", "PyQt6", "ctypes", "sortedcontainers", "dotenv", "easygui", "bs4", "htmldocx",
            "mysql", "mysql.connector"]
options = {
    'build_exe': {
        'packages': packages,
    },
}
setup(
    name="C-Notes",
    options=options,
    version="1.0",
    description='Programme de prise de notes',
    executables=executables
)
