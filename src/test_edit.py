import os
import sys

_base = sys.base_prefix
_tcl  = os.path.join(_base, 'tcl', 'tcl8.6')
_tk   = os.path.join(_base, 'tcl', 'tk8.6')
if os.path.isdir(_tcl):
    os.environ.setdefault('TCL_LIBRARY', _tcl)
if os.path.isdir(_tk):
    os.environ.setdefault('TK_LIBRARY', _tk)

from database.connection import DatabaseConnection
from controllers.patient_controller import PatientController
from views.patient_view import PatientView
import tkinter as tk

db = DatabaseConnection()
patient_ctrl = PatientController(db)
root = tk.Tk()
view = PatientView(root, patient_ctrl)

for item in view.tree.get_children():
    view.tree.selection_set(item)
    
    tags = view.tree.item(item, 'tags')
    print("Item tags:", tags, "Type:", type(tags))
    id_str = tags[0]
    print("id_str extracted:", id_str, "Type:", type(id_str))
    patient = view.controller.read_by_id(id_str)
    print("Found patient?", patient is not None)
    break
