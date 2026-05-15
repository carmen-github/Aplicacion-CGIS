import tkinter as tk
from tkinter import ttk

class MainMenuFrame(ttk.Frame):
    """Menú principal con botones grandes y centrados."""

    def __init__(self, parent, on_patients, on_tensions):
        super().__init__(parent, style='TFrame')
        self.on_patients = on_patients
        self.on_tensions = on_tensions
        self._create_ui()

    def _create_ui(self):
        # Contenedor central para todo el contenido
        center_container = ttk.Frame(self, style='TFrame')
        center_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Título principal
        title = ttk.Label(
            center_container,
            text="🏥  GESTIÓN MÉDICA",
            style='MainMenuTitle.TLabel',
            anchor='center'
        )
        title.pack(pady=(0, 60))

        # Contenedor de "tarjetas"
        buttons_container = ttk.Frame(center_container, style='TFrame')
        buttons_container.pack()

        # Botón Pacientes
        btn_patients = self._make_card(buttons_container, "👤", "PACIENTES", self.on_patients)
        btn_patients.pack(side=tk.LEFT, padx=50)

        # Botón Tensiones
        btn_tensions = self._make_card(buttons_container, "📈", "TENSIONES", self.on_tensions)
        btn_tensions.pack(side=tk.LEFT, padx=50)

    def _make_card(self, parent, icon, label, command):
        """Crea un botón grande con icono y texto."""
        btn_frame = ttk.Frame(parent, style='TFrame', cursor='hand2')
        
        icon_lbl = ttk.Label(btn_frame, text=icon, style='MainMenuIcon.TLabel')
        icon_lbl.pack(pady=10)
        
        title_lbl = ttk.Label(btn_frame, text=label, style='MainMenuText.TLabel')
        title_lbl.pack()

        # Binds para todo el frame y sus hijos
        for widget in (btn_frame, icon_lbl, title_lbl):
            widget.bind("<Button-1>", lambda e: command())
            widget.bind("<Enter>", lambda e, l=title_lbl, i=icon_lbl: self._on_hover(l, i, True))
            widget.bind("<Leave>", lambda e, l=title_lbl, i=icon_lbl: self._on_hover(l, i, False))

        return btn_frame

    def _on_hover(self, label, icon, entering):
        if entering:
            label.configure(style='MainMenuTextHover.TLabel')
            icon.configure(style='MainMenuIconHover.TLabel')
        else:
            label.configure(style='MainMenuText.TLabel')
            icon.configure(style='MainMenuIcon.TLabel')
