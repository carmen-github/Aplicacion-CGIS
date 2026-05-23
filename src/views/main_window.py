import tkinter as tk
from tkinter import ttk

from views.list_view import ListView

class MainWindow:
    """Ventana principal. Gestiona el contenedor y la navegación entre pantallas."""

    def __init__(self, root, patient_ctrl, tension_ctrl, lista_ctrl):
        self.root = root
        self.patient_ctrl = patient_ctrl
        self.tension_ctrl = tension_ctrl
        self.lista_ctrl = lista_ctrl

        self._configure_root()
        self._center_window()
        self._build_container()
        self._build_frames()
        self.show_frame('menu')

    # ── Configuración de la ventana ────────────────────────────────────────
    def _configure_root(self):
        self.root.title("Gestión Médica")
        self.root.geometry("960x620")
        self.root.resizable(True, True)
        self.root.minsize(800, 520)

    def _center_window(self):
        """Centra la ventana en la pantalla al arrancar."""
        self.root.update_idletasks()
        w = self.root.winfo_width() or 960
        h = self.root.winfo_height() or 620
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"960x620+{x}+{y}")

    # ── Construcción del contenedor principal ──────────────────────────────
    def _build_container(self):
        """Crea el contenedor raíz donde se apilan todas las pantallas."""
        self.container = ttk.Frame(self.root, style='TFrame')
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def _build_frames(self):
        """Instancia todos los frames/pantallas y los registra."""
        from views.main_menu_frame import MainMenuFrame
        from views.patient_view import PatientView
        from views.tension_view import TensionView

        self.frames = {}

        menu_frame = MainMenuFrame(
            self.container,
            on_patients=lambda: self._show_patients(),
            on_tensions=lambda: self._show_tensions(),
            on_lists=lambda: self._show_lists()
        )
        menu_frame.grid(row=0, column=0, sticky='nsew')
        self.frames['menu'] = menu_frame

        patient_frame = PatientView(
            self.container,
            self.patient_ctrl,
            self.tension_ctrl,
            self.lista_ctrl,
            on_back=lambda: self.show_frame('menu'),
            on_show_tensions=lambda p_id: self._show_tensions_for_patient(p_id)
        )
        patient_frame.grid(row=0, column=0, sticky='nsew')
        self.frames['patients'] = patient_frame

        tension_frame = TensionView(
            self.container,
            self.tension_ctrl,
            self.patient_ctrl,
            self.lista_ctrl,
            on_back=lambda: self.show_frame('menu'),
        )
        tension_frame.grid(row=0, column=0, sticky='nsew')
        self.frames['tensions'] = tension_frame

        lista_frame = ListView(
            self.container,
            self.lista_ctrl,
            on_back=lambda: self.show_frame('menu'),
        )
        lista_frame.grid(row=0, column=0, sticky='nsew')
        self.frames['lists'] = lista_frame

    # ── Navegación ─────────────────────────────────────────────────────────
    def show_frame(self, name: str):
        """Muestra la pantalla indicada y oculta las demás (sin Toplevel)."""
        frame = self.frames[name]
        frame.tkraise()

    def _show_patients(self):
        self.frames['patients'].load_data()
        self.show_frame('patients')

    def _show_tensions(self):
        # Limpiar filtro si venimos del menú general
        self.frames['tensions'].filter_patient_id = None
        self.frames['tensions'].load_data()
        # Al venir del menú, "Volver" lleva al menú
        self.frames['tensions'].on_back = lambda: self.show_frame('menu')
        self.show_frame('tensions')

    def _show_lists(self):
        self.frames['lists'].load_data()
        self.show_frame('lists')


    def _show_tensions_for_patient(self, patient_id):
        """Muestra las tensiones filtradas por un paciente específico."""
        self.frames['tensions'].load_data(patient_id=patient_id)
        # Al venir de pacientes, "Volver" lleva a pacientes
        self.frames['tensions'].on_back = lambda: self._show_patients()
        self.show_frame('tensions')