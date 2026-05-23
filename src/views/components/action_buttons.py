import tkinter as tk
from tkinter import ttk

class ActionButtons(ttk.Frame):
    """Componente reutilizable para los botones de acción estándar."""
    
    def __init__(self, parent, on_add=None, on_edit=None, on_delete=None, on_history=None, on_study=None):
        super().__init__(parent)
        
        if on_add:
            ttk.Button(self, text="Dar de alta", command=on_add, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        if on_edit:
            ttk.Button(self, text="Editar", command=on_edit).pack(side=tk.LEFT, padx=5)
            
        if on_history:
            ttk.Button(self, text="Ver Historial", command=on_history).pack(side=tk.LEFT, padx=5)

        if on_study:
            ttk.Button(self, text="Estudio", command=on_study).pack(side=tk.LEFT, padx=5)
            
        if on_delete:
            ttk.Button(self, text="Dar de baja", command=on_delete, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
