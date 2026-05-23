import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from esquemas.patient_view_schema import PatientViewSchema
from pydantic import ValidationError
from styles.styles import apply_window_style
from views.components.toast import show_toast
from views.components.action_buttons import ActionButtons
from views.list_dialog import AddEditListDialog as AddEditListRequestDialog


class PatientView(ttk.Frame):
    def __init__(self, parent, controller, tension_controller, list_controller, on_back=None, on_show_tensions=None):
        super().__init__(parent)
        self.controller = controller
        self.tension_controller = tension_controller
        self.list_controller = list_controller
        self.on_back = on_back
        self.on_show_tensions = on_show_tensions
        self.all_data = []
        self.sort_state = {'col': None, 'reverse': False}
        self.create_widgets()
        self.load_data(fetch=True)

    def create_widgets(self):
        # Top bar with Back button and Search
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(top_frame, text="← Volver", command=self.on_back, style='Secondary.TButton').pack(side=tk.LEFT)

        # 1. Create Tree first so it exists when trace triggers load_data
        self.tree = ttk.Treeview(self, columns=('nombre', 'apellido', 'genero', 'fechaNacimiento'), show='headings')
        
        # Headers with sorting
        headers = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'genero': 'Género',
            'fechaNacimiento': 'Fecha Nacimiento'
        }
        for col, text in headers.items():
            self.tree.heading(col, text=text, command=lambda c=col: self._on_header_click(c))
            self.tree.column(col, anchor=tk.CENTER)

        # 2. Search container
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="🔍", font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        # The trace might trigger when we insert "Buscar..."
        self.search_var.trace_add("write", lambda *args: self.load_data(fetch=False))
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        search_entry.insert(0, "Buscar...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if self.search_var.get() == "Buscar..." else None)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10)

        # Actions
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        
        ActionButtons(
            btn_frame,
            on_add=self.add_patient,
            on_edit=self.edit_patient,
            on_history=self.view_history,
            on_delete=self.delete_patient
        ).pack(side=tk.LEFT)

        ttk.Button(btn_frame, text="Solicitar toma de tensión", command=self.request_tension_service).pack(side=tk.LEFT, padx=5)

    def view_history(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un paciente para ver su historial.")
            return
        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        if self.on_show_tensions:
            self.on_show_tensions(id_str)

    def _on_header_click(self, col):
        """Gestiona la ordenación al hacer clic en las cabeceras."""
        if self.sort_state['col'] == col:
            if not self.sort_state['reverse']:
                self.sort_state['reverse'] = True
            else:
                # Tercer clic: reset
                self.sort_state['col'] = None
                self.sort_state['reverse'] = False
        else:
            self.sort_state['col'] = col
            self.sort_state['reverse'] = False
        
        self.load_data(fetch=False)

    def load_data(self, fetch=True):
        if fetch:
            self.all_data = self.controller.read_all()

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter
        query = self.search_var.get().lower()
        if query == "buscar...": query = ""
        
        filtered_data = []
        for p in self.all_data:
            searchable_text = f"{p.get('nombre', '')} {p.get('apellido', '')} {p.get('genero', '')} {p.get('fechaNacimiento', '')}".lower()
            if query in searchable_text:
                filtered_data.append(p)

        # Sort
        if self.sort_state['col']:
            col = self.sort_state['col']
            reverse = self.sort_state['reverse']
            
            # Si es fecha, queremos más reciente por defecto (reverse=True)
            if col == 'fechaNacimiento' and not reverse:
                # Ajuste para que el primer clic en fecha sea descendente (más reciente)
                filtered_data.sort(key=lambda x: str(x.get(col, '')), reverse=True)
            else:
                filtered_data.sort(key=lambda x: str(x.get(col, '')).lower(), reverse=reverse)

        # Insert
        for p in filtered_data:
            self.tree.insert('', tk.END, values=(
                p.get('nombre', ''),
                p.get('apellido', ''),
                p.get('genero', p.get('género', '')),
                str(p.get('fechaNacimiento', ''))[:10],
            ), tags=(str(p['_id']),))

    def add_patient(self):
        AddEditPatientDialog(self, self.controller, None)

    def edit_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un paciente para editar.")
            return
        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        patient = self.controller.read_by_id(id_str)
        if patient:
            AddEditPatientDialog(self, self.controller, patient)
        else:
            messagebox.showerror("Error", f"No se pudo encontrar el paciente con ID {id_str}")

    def delete_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un paciente para eliminar.")
            return
        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar paciente?"):
            self.controller.delete(id_str)
            self.load_data()
            show_toast(self.winfo_toplevel(), "Paciente eliminado correctamente", type="success")

    def request_tension_service(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un paciente para solicitar una toma de tensión.")
            return

        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        patient = self.controller.read_by_id(id_str)
        if not patient:
            messagebox.showerror("Error", f"No se pudo encontrar el paciente con ID {id_str}")
            return

        now = datetime.now().replace(second=0, microsecond=0).isoformat(timespec='minutes')
        record = {
            'id_paciente': id_str,
            'fechaHora': now,
            'servicio': 'enfermeria',
            'estado': 'pendiente',
            'patron': 'unico',
            'repeticiones': 1,
        }
        AddEditListRequestDialog(
            self,
            self.list_controller,
            self.controller,
            record,
            patient_id=id_str,
            patient_name=f"{patient.get('nombre', '')} {patient.get('apellido', '')}",
            on_saved=self.load_data,
        )


class EstudioTensionDialog:
    def __init__(self, parent, tension_controller, patient_id, patient_name):
        self.parent = parent
        self.tension_controller = tension_controller
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.top = tk.Toplevel(parent)
        self.top.title(f"Estudio de tensiones - {patient_name}")
        apply_window_style(self.top)
        self.top.resizable(False, False)
        self.create_widgets()
        self.update_metrics()

    def create_widgets(self):
        ttk.Label(self.top, text=f"Paciente: {self.patient_name}", font=('Segoe UI', 11, 'bold')).pack(padx=10, pady=(10, 0))

        form_frame = ttk.Frame(self.top)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(form_frame, text="Últimas n tomas (vacío = todas):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.ultimas_n_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ultimas_n_var, width=10).grid(row=0, column=1, sticky='w', padx=5, pady=5)

        ttk.Button(form_frame, text="Calcular", command=self.update_metrics).grid(row=0, column=2, padx=5, pady=5)

        self.result_frame = ttk.LabelFrame(self.top, text="Resultados del estudio")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.labels = {}
        for idx, label_text in enumerate([
            "Total de tomas registradas:",
            "Tomas utilizadas en el cálculo:",
            "Media sistólica:",
            "Media diastólica:",
            "Última toma:",
        ]):
            ttk.Label(self.result_frame, text=label_text).grid(row=idx, column=0, sticky='w', padx=5, pady=5)
            self.labels[label_text] = ttk.Label(self.result_frame, text="-")
            self.labels[label_text].grid(row=idx, column=1, sticky='w', padx=5, pady=5)

        ttk.Button(self.top, text="Cerrar", command=self.top.destroy).pack(pady=(0, 10))

    def update_metrics(self):
        raw_n = self.ultimas_n_var.get().strip()
        ultimas_n = None
        if raw_n:
            try:
                ultimas_n = int(raw_n)
                if ultimas_n <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Entrada inválida", "Introduce un número positivo para las últimas tomas.")
                return

        estudio = self.tension_controller.study_by_patient(self.patient_id, ultimas_n)
        ultima = estudio.get('ultima_toma')
        ultima_text = "No hay tomas" if not ultima else (
            f"{str(ultima.get('fecha', ''))[:10]} - {ultima.get('valoracion', '')} "
            f"(S:{ultima.get('valores', {}).get('sistolica', '-')}, D:{ultima.get('valores', {}).get('diastolica', '-')})"
        )

        self.labels["Total de tomas registradas:"].config(text=str(estudio.get('total_tomas', 0)))
        self.labels["Tomas utilizadas en el cálculo:"].config(text=str(estudio.get('tomas_utilizadas', 0)))
        self.labels["Media sistólica:"].config(text=f"{estudio.get('media_sistolica'):.1f}" if estudio.get('media_sistolica') is not None else "-")
        self.labels["Media diastólica:"].config(text=f"{estudio.get('media_diastolica'):.1f}" if estudio.get('media_diastolica') is not None else "-")
        self.labels["Última toma:"].config(text=ultima_text)


class AddEditPatientDialog:
    def __init__(self, parent, controller, patient: dict | None):
        self.parent = parent
        self.controller = controller
        self.patient = patient  # dict con datos o None para alta
        self.top = tk.Toplevel(parent)
        self.top.title("Editar Paciente" if patient else "Dar de alta Paciente")
        apply_window_style(self.top)
        self.top.resizable(False, False)
        self.create_form()
        if patient:
            self.prefill()

    def create_form(self):
        ttk.Label(self.top, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.nombre_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Apellido:").grid(row=1, column=0, padx=5, pady=5)
        self.apellido_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.apellido_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Género:").grid(row=2, column=0, padx=5, pady=5)
        self.genero_var = tk.StringVar()
        genero_combo = ttk.Combobox(self.top, textvariable=self.genero_var,
                                    values=['masculino', 'femenino', 'otro'], state='readonly')
        genero_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Fecha Nacimiento (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
        self.fechaNacimiento_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.fechaNacimiento_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(self.top, text="Guardar", command=self.save).grid(row=4, column=0, columnspan=2, pady=10)

    def prefill(self):
        """Rellena el formulario con los datos del paciente a editar."""
        self.nombre_var.set(self.patient.get('nombre', ''))
        self.apellido_var.set(self.patient.get('apellido', ''))
        self.genero_var.set(self.patient.get('genero', self.patient.get('género', '')))
        self.fechaNacimiento_var.set(str(self.patient.get('fechaNacimiento', ''))[:10])

    def save(self):
        try:
            nombre = self.nombre_var.get()
            apellido = self.apellido_var.get()
            genero = self.genero_var.get()
            fechaNacimiento = self.fechaNacimiento_var.get()

            # 1ª validación: formulario (campos presentes, formato básico)
            try:
                PatientViewSchema(
                    nombre=nombre, apellido=apellido,
                    genero=genero, fechaNacimiento=fechaNacimiento
                )
            except ValidationError as ve:
                msgs = [e['msg'].replace('Value error, ', '') for e in ve.errors()]
                messagebox.showerror("Campos incompletos", "\n".join(msgs))
                return

            # 2ª validación: reglas de negocio (a través del servicio/schema de alta)
            if self.patient:
                self.controller.update(str(self.patient['_id']), {
                    'nombre': nombre.strip(), 'apellido': apellido.strip(),
                    'genero': genero.strip(), 'fechaNacimiento': fechaNacimiento.strip(),
                })
            else:
                self.controller.create(nombre.strip(), apellido.strip(), genero.strip(), fechaNacimiento.strip())

            self.parent.load_data()
            show_toast(self.parent.winfo_toplevel(), 
                       "Paciente guardado correctamente" if self.patient else "Paciente creado correctamente", 
                       type="success")
            self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Errores de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))