import tkinter as tk
from tkinter import ttk, messagebox
from styles.styles import apply_window_style
from views.components.toast import show_toast
from views.components.action_buttons import ActionButtons
from views.list_dialog import AddEditListDialog
from views.tension_view import AddEditTensionDialog


class ListView(ttk.Frame):
    def __init__(self, parent, list_controller, patient_controller, tension_controller,on_back=None):
        super().__init__(parent)
        self.controller = list_controller
        self.patient_controller = patient_controller
        self.tension_controller = tension_controller
        self.on_back = on_back
        self.all_data = []
        self.patient_map = {}
        self.sort_state = {'col': None, 'reverse': False}
        self.create_widgets()
        self.load_data(fetch=True)


    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=10, padx=10)

        ttk.Button(top_frame, text="← Volver", command=self.on_back, style='Secondary.TButton').pack(side=tk.LEFT)

        filter_frame = ttk.Frame(top_frame)
        filter_frame.pack(side=tk.RIGHT)

        ttk.Label(filter_frame, text="🔍", font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.load_data(fetch=False))
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT)
        search_entry.insert(0, 'Buscar...')
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if self.search_var.get() == 'Buscar...' else None)

        ttk.Label(filter_frame, text="Servicio:").pack(side=tk.LEFT, padx=(10, 5))
        self.service_var = tk.StringVar(value='todos')
        ttk.Combobox(filter_frame, textvariable=self.service_var, values=['todos', 'consulta', 'enfermeria'], state='readonly', width=12).pack(side=tk.LEFT)
        self.service_var.trace_add('write', lambda *args: self.load_data(fetch=False))

        ttk.Label(filter_frame, text="Estado:").pack(side=tk.LEFT, padx=(10, 5))
        self.state_var = tk.StringVar(value='todos')
        ttk.Combobox(filter_frame, textvariable=self.state_var, values=['todos', 'pendiente', 'atendido', 'anulado'], state='readonly', width=12).pack(side=tk.LEFT)
        self.state_var.trace_add('write', lambda *args: self.load_data(fetch=False))

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.tree = ttk.Treeview(tree_frame, columns=('paciente', 'servicio', 'fechaHora', 'estado'), show='headings')
        self.tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        headers = {
            'paciente': 'Paciente',
            'servicio': 'Servicio',
            'fechaHora': 'Fecha y Hora',
            'estado': 'Estado',
        }
        for col, text in headers.items():
            self.tree.heading(col, text=text, command=lambda c=col: self._on_header_click(c))
            self.tree.column(col, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)

        ActionButtons(
            btn_frame,
            on_add=self.add_item,
            on_edit=self.edit_item,
            on_delete=self.delete_item
        ).pack(side=tk.LEFT)

        ttk.Button(btn_frame, text="Registrar toma", command=self.register_tension).pack(side=tk.LEFT, padx=5)

    def _on_header_click(self, col):
        if self.sort_state['col'] == col:
            if not self.sort_state['reverse']:
                self.sort_state['reverse'] = True
            else:
                self.sort_state['col'] = None
                self.sort_state['reverse'] = False
        else:
            self.sort_state['col'] = col
            self.sort_state['reverse'] = False
        self.load_data(fetch=False)

    def load_data(self, fetch=True):
        if fetch:
            self.all_data = self.controller.read_all()

        patients = self.patient_controller.read_all()
        self.patient_map = {str(p['_id']): f"{p.get('nombre', '')} {p.get('apellido', '')}" for p in patients}

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().lower()
        if query == 'buscar...':
            query = ''

        filtered_data = []
        for record in self.all_data:
            patient_name = self.patient_map.get(str(record.get('id_paciente')), '')
            text = f"{patient_name} {record.get('servicio', '')} {record.get('estado', '')} {record.get('fechaHora', '')}".lower()
            if query in text:
                if self.service_var.get() != 'todos' and record.get('servicio') != self.service_var.get():
                    continue
                if self.state_var.get() != 'todos' and record.get('estado') != self.state_var.get():
                    continue
                filtered_data.append(record)

        if self.sort_state['col']:
            col = self.sort_state['col']
            reverse = self.sort_state['reverse']
            filtered_data.sort(key=lambda x: str(x.get(col, '')).lower(), reverse=reverse)

        for record in filtered_data:
            patient_name = self.patient_map.get(str(record.get('id_paciente')), record.get('id_paciente', ''))
            self.tree.insert('', tk.END, values=(
                patient_name,
                record.get('servicio', ''),
                str(record.get('fechaHora', ''))[:16],
                record.get('estado', ''),
            ), tags=(str(record['_id']),))

    def add_item(self):
        AddEditListDialog(self, self.controller, self.patient_controller, None, on_saved=self.load_data)

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un elemento de la lista para editar.")
            return
        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        record = self.controller.read_by_id(id_str)
        if record:
            AddEditListDialog(self, self.controller, self.patient_controller, record, on_saved=self.load_data)
        else:
            messagebox.showerror("Error", "No se pudo encontrar el elemento seleccionado.")

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un elemento de la lista para eliminar.")
            return
        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar elemento de la lista?"):
            self.controller.delete(id_str)
            self.load_data()
            show_toast(self.winfo_toplevel(), "Elemento eliminado", type='success')

    def register_tension(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una solicitud de enfermería para registrar la toma.")
            return
        item = selected[0]
        id_str = self.tree.item(item, 'tags')[0]
        record = self.controller.read_by_id(id_str)
        if not record:
            messagebox.showerror("Error", "No se pudo encontrar el elemento seleccionado.")
            return
        if record.get('servicio') != 'enfermeria':
            messagebox.showwarning("Acción no válida", "Solo se pueden registrar tomas sobre solicitudes de enfermería.")
            return
        if record.get('estado') != 'pendiente':
            messagebox.showwarning("Acción no válida", "Solo las solicitudes pendientes pueden registrar una toma.")
            return

        def on_tension_saved():
            try:
                self.controller.update(record['_id'], {'estado': 'atendido'})
                self.load_data()
                show_toast(self.winfo_toplevel(), "Toma registrada y solicitud atendida", type='success')
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        AddEditTensionDialog(self, self.tension_controller, {'id_paciente': record.get('id_paciente')}, on_saved=on_tension_saved)


class AddEditListDialog:
    def __init__(self, parent, controller, patient_controller, record: dict | None, on_saved=None):
        self.parent = parent
        self.controller = controller
        self.patient_controller = patient_controller
        self.record = record
        self.on_saved = on_saved
        self.top = tk.Toplevel(parent)
        self.top.title("Editar solicitud" if record else "Nueva solicitud")
        apply_window_style(self.top)
        self.top.resizable(False, False)
        self.create_form()
        if record:
            self.prefill()

    def create_form(self):
        ttk.Label(self.top, text="Paciente:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.patient_var = tk.StringVar()
        patient_ids = [str(p['_id']) for p in self.patient_controller.read_all()]
        self.patient_combo = ttk.Combobox(self.top, textvariable=self.patient_var, values=patient_ids, state='readonly')
        self.patient_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Fecha y Hora (YYYY-MM-DDTHH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.fecha_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.fecha_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Servicio:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.servicio_var = tk.StringVar()
        ttk.Combobox(self.top, textvariable=self.servicio_var, values=['consulta', 'enfermeria'], state='readonly').grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Estado:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.estado_var = tk.StringVar(value='pendiente')
        ttk.Combobox(self.top, textvariable=self.estado_var, values=['pendiente', 'atendido', 'anulado'], state='readonly').grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Patrón:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.patron_var = tk.StringVar(value='unico')
        ttk.Combobox(self.top, textvariable=self.patron_var, values=['unico', 'diario', 'semanal'], state='readonly').grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Repeticiones:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.repeticiones_var = tk.IntVar(value=1)
        ttk.Entry(self.top, textvariable=self.repeticiones_var, width=8).grid(row=5, column=1, padx=5, pady=5, sticky='w')

        ttk.Button(self.top, text="Guardar", command=self.save).grid(row=6, column=0, columnspan=2, pady=10)

    def prefill(self):
        self.patient_var.set(str(self.record.get('id_paciente', '')))
        self.fecha_var.set(str(self.record.get('fechaHora', '')))
        self.servicio_var.set(self.record.get('servicio', ''))
        self.estado_var.set(self.record.get('estado', 'pendiente'))
        self.patron_var.set(self.record.get('patron', 'unico'))
        self.repeticiones_var.set(self.record.get('repeticiones', 1))

    def save(self):
        try:
            data = {
                'id_paciente': self.patient_var.get().strip(),
                'fechaHora': self.fecha_var.get().strip(),
                'servicio': self.servicio_var.get().strip(),
                'estado': self.estado_var.get().strip(),
                'patron': self.patron_var.get().strip(),
                'repeticiones': int(self.repeticiones_var.get()),
            }
            if self.record:
                self.controller.update(str(self.record['_id']), data)
                show_toast(self.parent.winfo_toplevel(), "Solicitud actualizada", type='success')
            else:
                created = self.controller.create(**data)
                count = 1 if isinstance(created, dict) else len(created)
                show_toast(self.parent.winfo_toplevel(), f"{count} solicitud(es) creada(s)", type='success')
            if self.on_saved:
                self.on_saved()
            self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))
