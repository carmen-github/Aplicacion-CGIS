import tkinter as tk
from tkinter import ttk, messagebox
from esquemas.tension_view_schema import TensionViewSchema
from pydantic import ValidationError
from styles.styles import BG_DARK, BG_INPUT
from views.components.toast import show_toast


class TensionView(ttk.Frame):
    def __init__(self, parent, controller, patient_controller, on_back=None):
        super().__init__(parent)
        self.controller = controller
        self.patient_controller = patient_controller
        self.on_back = on_back  # This will be updated dynamically by MainWindow
        self.all_data = []
        self.filter_patient_id = None
        self.sort_state = {'col': None, 'reverse': False}
        self.create_widgets()
        self.load_data(fetch=True)

    def create_widgets(self):
        # Top bar with Back button and Search
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Usamos una lambda para capturar el valor actual de self.on_back
        ttk.Button(top_frame, text="← Volver", command=lambda: self.on_back(), style='Secondary.TButton').pack(side=tk.LEFT)

        # 1. Create Tree first so it exists when trace triggers load_data
        self.tree = ttk.Treeview(self, columns=('paciente', 'estado', 'fecha', 'valoracion', 'valor_en_rango'), show='headings')
        
        # Headers with sorting
        headers = {
            'paciente': 'Paciente',
            'estado': 'Estado',
            'fecha': 'Fecha',
            'valoracion': 'Valoración',
            'valor_en_rango': 'En Rango'
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
        ttk.Button(btn_frame, text="Dar de alta", command=self.add_tension, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_tension).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Dar de baja", command=self.delete_tension, style='Danger.TButton').pack(side=tk.LEFT, padx=5)

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

    def load_data(self, fetch=True, patient_id=None):
        if fetch:
            self.all_data = self.controller.read_all()
        
        if patient_id is not None:
            self.filter_patient_id = patient_id
        
        # Mapeo de pacientes para mostrar nombres en lugar de IDs
        patients = self.patient_controller.read_all()
        patient_map = {str(p['_id']): f"{p.get('nombre', '')} {p.get('apellido', '')}" for p in patients}

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter
        query = self.search_var.get().lower()
        if query == "buscar...": query = ""
        
        filtered_data = []
        for t in self.all_data:
            p_id = str(t.get('id_paciente', ''))
            p_name = patient_map.get(p_id, p_id)
            
            # Filtro por paciente específico (vínculo desde Pacientes)
            if self.filter_patient_id and p_id != self.filter_patient_id:
                continue

            searchable_text = f"{p_name} {t.get('estado', '')} {t.get('fecha', '')} {t.get('valoracion', '')}".lower()
            if query in searchable_text:
                # Añadimos el nombre al dict para facilitar el insert y sort
                t['_p_name'] = p_name 
                filtered_data.append(t)

        # Sort
        if self.sort_state['col']:
            col = self.sort_state['col']
            reverse = self.sort_state['reverse']
            
            # Map column to the key in dict
            sort_key = '_p_name' if col == 'paciente' else col
            
            # Si es fecha, queremos más reciente por defecto (reverse=True)
            if col == 'fecha' and not reverse:
                filtered_data.sort(key=lambda x: str(x.get(sort_key, '')), reverse=True)
            else:
                filtered_data.sort(key=lambda x: str(x.get(sort_key, '')).lower(), reverse=reverse)

        # Insert
        for t in filtered_data:
            self.tree.insert('', tk.END, values=(
                t.get('_p_name', ''),
                t.get('estado', ''),
                str(t.get('fecha', ''))[:10],
                t.get('valoracion', ''),
                '✓' if t.get('valor_en_rango') else '✗',
            ), tags=(str(t['_id']),))

    def add_tension(self):
        AddEditTensionDialog(self, self.controller, None)

    def edit_tension(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una tensión para editar.")
            return
        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        tension = self.controller.read_by_id(id_str)
        if tension:
            AddEditTensionDialog(self, self.controller, tension)
        else:
            messagebox.showerror("Error", f"No se pudo encontrar la tensión con ID {id_str}")

    def delete_tension(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una tensión para eliminar.")
            return
        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar tensión?"):
            self.controller.delete(id_str)
            self.load_data()
            show_toast(self.winfo_toplevel(), "Registro de tensión eliminado", type="success")


class AddEditTensionDialog:
    def __init__(self, parent, controller, tension: dict | None):
        self.parent = parent
        self.controller = controller
        self.tension = tension  # dict con datos o None para alta
        self.top = tk.Toplevel(parent)
        self.top.title("Editar Tensión" if tension else "Dar de alta Tensión")
        self.top.configure(bg=BG_DARK)
        self.top.resizable(False, False)
        self.create_form()
        if tension:
            self.prefill()

    def create_form(self):
        ttk.Label(self.top, text="ID Paciente:").grid(row=0, column=0, padx=5, pady=5)
        self.id_paciente_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.id_paciente_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Estado:").grid(row=1, column=0, padx=5, pady=5)
        self.estado_var = tk.StringVar()
        estado_combo = ttk.Combobox(self.top, textvariable=self.estado_var,
                                    values=['preliminar', 'final', 'corregido'], state='readonly')
        estado_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Fecha (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.fecha_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.fecha_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Valoración:").grid(row=3, column=0, padx=5, pady=5)
        self.valoracion_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.valoracion_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Valor en Rango:").grid(row=4, column=0, padx=5, pady=5)
        self.valor_en_rango_var = tk.BooleanVar()
        ttk.Checkbutton(self.top, variable=self.valor_en_rango_var).grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(self.top, text="Guardar", command=self.save).grid(row=5, column=0, columnspan=2, pady=10)

    def prefill(self):
        """Rellena el formulario con los datos de la tensión a editar."""
        self.id_paciente_var.set(self.tension.get('id_paciente', ''))
        self.estado_var.set(self.tension.get('estado', ''))
        self.fecha_var.set(str(self.tension.get('fecha', ''))[:10])
        self.valoracion_var.set(self.tension.get('valoracion', ''))
        self.valor_en_rango_var.set(self.tension.get('valor_en_rango', False))

    def save(self):
        try:
            id_paciente = self.id_paciente_var.get().strip()
            estado = self.estado_var.get().strip()
            fecha = self.fecha_var.get().strip()
            valoracion = self.valoracion_var.get().strip()
            valor_en_rango = self.valor_en_rango_var.get()

            # 1ª validación: formulario (campos presentes, formato básico)
            try:
                TensionViewSchema(
                    id_paciente=id_paciente, estado=estado,
                    fecha=fecha, valoracion=valoracion,
                    valor_en_rango=valor_en_rango
                )
            except ValidationError as ve:
                msgs = [e['msg'].replace('Value error, ', '') for e in ve.errors()]
                messagebox.showerror("Campos incompletos", "\n".join(msgs))
                return

            # 2ª validación: reglas de negocio (a través del servicio/schema de alta)
            if self.tension:
                self.controller.update(str(self.tension['_id']), {
                    'id_paciente': id_paciente, 'estado': estado,
                    'fecha': fecha, 'valoracion': valoracion,
                    'valor_en_rango': valor_en_rango,
                    'valores': self.tension.get('valores', {}),
                })
            else:
                self.controller.create(id_paciente, estado, fecha, valoracion, valor_en_rango)

            self.parent.load_data()
            show_toast(self.parent.winfo_toplevel(), 
                       "Medición actualizada" if self.tension else "Medición registrada", 
                       type="success")
            self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Errores de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))