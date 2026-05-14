import tkinter as tk
from tkinter import ttk, messagebox
from esquemas.patient_view_schema import PatientViewSchema
from pydantic import ValidationError
from styles.styles import BG_DARK, BG_INPUT
from views.components.toast import show_toast


class PatientView(ttk.Frame):
    def __init__(self, parent, controller, on_back=None, on_show_tensions=None):
        super().__init__(parent)
        self.controller = controller
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
        ttk.Button(btn_frame, text="Dar de alta", command=self.add_patient, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Ver Historial", command=self.view_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Dar de baja", command=self.delete_patient, style='Danger.TButton').pack(side=tk.LEFT, padx=5)

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


class AddEditPatientDialog:
    def __init__(self, parent, controller, patient: dict | None):
        self.parent = parent
        self.controller = controller
        self.patient = patient  # dict con datos o None para alta
        self.top = tk.Toplevel(parent)
        self.top.title("Editar Paciente" if patient else "Dar de alta Paciente")
        self.top.configure(bg=BG_DARK)
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
            nombre = self.nombre_var.get().strip()
            apellido = self.apellido_var.get().strip()
            genero = self.genero_var.get()
            fechaNacimiento = self.fechaNacimiento_var.get().strip()

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
                    'nombre': nombre, 'apellido': apellido,
                    'genero': genero, 'fechaNacimiento': fechaNacimiento,
                })
            else:
                self.controller.create(nombre, apellido, genero, fechaNacimiento)

            self.parent.load_data()
            show_toast(self.parent.winfo_toplevel(), 
                       "Paciente guardado correctamente" if self.patient else "Paciente creado correctamente", 
                       type="success")
            self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Errores de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))