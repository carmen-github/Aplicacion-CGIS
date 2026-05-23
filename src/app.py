import os
import sys
import tkinter as tk

# Fix: Tkinter no encuentra Tcl/Tk cuando se ejecuta desde un venv en Windows
_base = sys.base_prefix
_tcl  = os.path.join(_base, 'tcl', 'tcl8.6')
_tk   = os.path.join(_base, 'tcl', 'tk8.6')
if os.path.isdir(_tcl):
    os.environ.setdefault('TCL_LIBRARY', _tcl)
if os.path.isdir(_tk):
    os.environ.setdefault('TK_LIBRARY', _tk)

from database.connection import DatabaseConnection
from controllers.patient_controller import PatientController
from controllers.tension_controller import TensionController
from controllers.lista_controller import ListaController
from views.main_window import MainWindow
from styles.styles import apply_styles, apply_window_style

class App:
    def __init__(self):
        self.db = DatabaseConnection()
        self.patient_ctrl = PatientController(self.db)
        self.tension_ctrl = TensionController(self.db)
        self.lista_ctrl = ListaController(self.db)
        
        self.root = tk.Tk()
        apply_styles()  # debe llamarse DESPUÉS de crear tk.Tk()
        apply_window_style(self.root)
        
        self.main_window = MainWindow(self.root, self.patient_ctrl, self.tension_ctrl, self.lista_ctrl)

    def run(self):
        self.root.mainloop()

def create_app():
    return App()
