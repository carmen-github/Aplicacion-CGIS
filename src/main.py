import os
import sys

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
from views.main_window import MainWindow
from styles.styles import apply_styles
import tkinter as tk

def main():
    db = DatabaseConnection()
    patient_ctrl = PatientController(db)
    tension_ctrl = TensionController(db)
    root = tk.Tk()
    apply_styles()  # debe llamarse DESPUÉS de crear tk.Tk()
    MainWindow(root, patient_ctrl, tension_ctrl)
    root.mainloop()

if __name__ == "__main__":
    main()