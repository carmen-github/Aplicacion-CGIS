import tkinter as tk
from tkinter import ttk, messagebox
from pydantic import ValidationError
from esquemas.tension_view_schema import TensionViewSchema
from styles.styles import apply_window_style, BG_DARK
from views.components.toast import show_toast
from views.components.action_buttons import ActionButtons


class TensionView(ttk.Frame):
    def __init__(self, parent, controller, patient_controller, list_controller, on_back=None):
        super().__init__(parent)
        self.controller = controller
        self.patient_controller = patient_controller
        self.list_controller = list_controller
        self.on_back = on_back
        self.all_data = []
        self.filter_patient_id = None
        self.sort_state = {'col': None, 'reverse': False}
        self.create_widgets()
        self.load_data(fetch=True)

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(top_frame, text="← Volver", command=lambda: self.on_back(), style='Secondary.TButton').pack(side=tk.LEFT)

        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="🔍", font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_data(fetch=False))
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        search_entry.insert(0, "Buscar...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if self.search_var.get() == "Buscar..." else None)

        scroll_container = ttk.Frame(self)
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        self.history_canvas = tk.Canvas(scroll_container, background=BG_DARK, highlightthickness=0)
        self.history_scrollbar = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=self.history_canvas.yview)
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)

        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_container = ttk.Frame(self.history_canvas, style='Card.TFrame')
        self.history_window = self.history_canvas.create_window((0, 0), window=self.history_container, anchor='nw')

        self.history_container.bind(
            '<Configure>',
            lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox('all'))
        )
        self.history_canvas.bind(
            '<Configure>',
            lambda e: self.history_canvas.itemconfig(self.history_window, width=e.width)
        )

        self.history_frame = ttk.LabelFrame(self.history_container, text="Historial de tensiones", style='TLabelframe')
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.study_frame = ttk.LabelFrame(self.history_frame, text="Estudio de tensiones por paciente", style='TLabelframe')
        self.study_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        self.study_labels = {}
        for idx, label_text in enumerate([
            "Paciente:",
            "Total de tomas:",
            "Tomas calculadas:",
            "Media sistólica:",
            "Media diastólica:",
            "Última toma:",
            "Solicitud programada:",
        ]):
            ttk.Label(self.study_frame, text=label_text, style='Card.TLabel').grid(row=idx, column=0, sticky='w', padx=5, pady=3)
            self.study_labels[label_text] = ttk.Label(self.study_frame, text='-', style='Card.TLabel')
            self.study_labels[label_text].grid(row=idx, column=1, sticky='w', padx=5, pady=3)
        self.study_frame.pack_forget()

        tree_frame = ttk.Frame(self.history_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(tree_frame, columns=('paciente', 'estado', 'fecha', 'valoracion', 'sistolica', 'diastolica', 'valor_en_rango'), show='headings')
        self.tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        headers = {
            'paciente': 'Paciente',
            'estado': 'Estado (FHIR)',
            'fecha': 'Fecha',
            'valoracion': 'Valoración',
            'sistolica': 'Sistólica',
            'diastolica': 'Diastólica',
            'valor_en_rango': 'En Rango'
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
            on_add=self.add_tension,
            on_edit=self.edit_tension,
            on_delete=self.delete_tension
        ).pack()

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

    def load_data(self, fetch=True, patient_id=None):
        if fetch:
            self.all_data = self.controller.read_all()
        
        if patient_id is not None:
            self.filter_patient_id = patient_id
        
        patients = self.patient_controller.read_all()
        patient_map = {str(p['_id']): f"{p.get('nombre', '')} {p.get('apellido', '')}" for p in patients}

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().lower()
        if query == "buscar...": query = ""
        
        filtered_data = []
        for t in self.all_data:
            p_id = str(t.get('id_paciente', ''))
            p_name = patient_map.get(p_id, p_id)
            
            if self.filter_patient_id and p_id != self.filter_patient_id:
                continue

            searchable_text = f"{p_name} {t.get('estado', '')} {t.get('fecha', '')} {t.get('valoracion', '')}".lower()
            if query in searchable_text:
                t['_p_name'] = p_name 
                filtered_data.append(t)

        if self.sort_state['col']:
            col = self.sort_state['col']
            reverse = self.sort_state['reverse']
            sort_key = '_p_name' if col == 'paciente' else col
            
            if col == 'fecha' and not reverse:
                filtered_data.sort(key=lambda x: str(x.get(sort_key, '')), reverse=True)
            else:
                filtered_data.sort(key=lambda x: str(x.get(sort_key, '')).lower(), reverse=reverse)

        self.update_study_panel(patient_map.get(self.filter_patient_id))

        for t in filtered_data:
            valores = t.get('valores', {})
            self.tree.insert('', tk.END, values=(
                t.get('_p_name', ''),
                t.get('estado', ''),
                str(t.get('fecha', ''))[:10],
                t.get('valoracion', ''),
                valores.get('sistolica', '-'),
                valores.get('diastolica', '-'),
                '✓' if t.get('valor_en_rango') else '✗',
            ), tags=(str(t['_id']),))

    def update_study_panel(self, patient_name=None):
        if not self.filter_patient_id:
            self.study_frame.pack_forget()
            return

        estudio = self.controller.study_by_patient(self.filter_patient_id)
        solicitudes = self.list_controller.read_by_patient(self.filter_patient_id)
        pending_requests = [s for s in solicitudes if s.get('servicio') == 'enfermeria' and s.get('estado') == 'pendiente']
        next_request = min(pending_requests, key=lambda x: x.get('fechaHora', ''), default=None) if pending_requests else None

        paciente_display = patient_name or str(self.filter_patient_id)

        self.study_labels["Paciente:"].config(text=paciente_display)
        self.study_labels["Total de tomas:"].config(text=str(estudio.get('total_tomas', 0)))
        self.study_labels["Tomas calculadas:"].config(text=str(estudio.get('tomas_utilizadas', 0)))
        self.study_labels["Media sistólica:"].config(
            text=f"{estudio.get('media_sistolica'):.1f}" if estudio.get('media_sistolica') is not None else '-'
        )
        self.study_labels["Media diastólica:"].config(
            text=f"{estudio.get('media_diastolica'):.1f}" if estudio.get('media_diastolica') is not None else '-'
        )

        ultima = estudio.get('ultima_toma')
        if ultima:
            fecha = str(ultima.get('fecha', ''))[:10]
            sistolica = ultima.get('valores', {}).get('sistolica', '-')
            diastolica = ultima.get('valores', {}).get('diastolica', '-')
            ultima_text = f"{fecha} (S:{sistolica}, D:{diastolica})"
        else:
            ultima_text = "No hay tomas"
        self.study_labels["Última toma:"].config(text=ultima_text)

        if next_request:
            request_text = f"{str(next_request.get('fechaHora', ''))[:16]} - {next_request.get('estado', '')}"
        else:
            request_text = "Sin solicitud programada"
        self.study_labels["Solicitud programada:"].config(text=request_text)

        if not self.study_frame.winfo_ismapped():
            self.study_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

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
    def __init__(self, parent, controller, tension: dict | None, on_saved=None):
        self.parent = parent
        self.controller = controller
        self.tension = tension
        self.on_saved = on_saved
        self.top = tk.Toplevel(parent)
        self.top.title("Editar Tensión" if tension else "Dar de alta Tensión")
        apply_window_style(self.top)
        self.top.resizable(False, False)
        self.create_form()
        if tension:
            self.prefill()

    def create_form(self):
        # Datos básicos
        lf_basicos = ttk.LabelFrame(self.top, text="Datos Básicos")
        lf_basicos.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(lf_basicos, text="ID Paciente:").grid(row=0, column=0, padx=5, pady=5)
        self.id_paciente_var = tk.StringVar()
        ttk.Entry(lf_basicos, textvariable=self.id_paciente_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(lf_basicos, text="Estado (FHIR):").grid(row=1, column=0, padx=5, pady=5)
        self.estado_var = tk.StringVar()
        estado_combo = ttk.Combobox(lf_basicos, textvariable=self.estado_var,
                                    values=['registered', 'preliminary', 'final', 'amended', 'corrected', 'cancelled', 'entered-in-error', 'unknown'], state='readonly')
        estado_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(lf_basicos, text="Fecha (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.fecha_var = tk.StringVar()
        ttk.Entry(lf_basicos, textvariable=self.fecha_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(lf_basicos, text="Valoración:").grid(row=3, column=0, padx=5, pady=5)
        self.valoracion_var = tk.StringVar()
        ttk.Entry(lf_basicos, textvariable=self.valoracion_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(lf_basicos, text="Valor en Rango:").grid(row=4, column=0, padx=5, pady=5)
        self.valor_en_rango_var = tk.BooleanVar()
        ttk.Checkbutton(lf_basicos, variable=self.valor_en_rango_var).grid(row=4, column=1, padx=5, pady=5)

        # Datos LOINC
        lf_loinc = ttk.LabelFrame(self.top, text="Valores LOINC 85354-9")
        lf_loinc.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(lf_loinc, text="Sistólica:").grid(row=0, column=0, padx=5, pady=5)
        self.sistolica_var = tk.IntVar(value=120)
        ttk.Entry(lf_loinc, textvariable=self.sistolica_var, width=10).grid(row=0, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(lf_loinc, text="Diastólica:").grid(row=0, column=2, padx=5, pady=5)
        self.diastolica_var = tk.IntVar(value=80)
        ttk.Entry(lf_loinc, textvariable=self.diastolica_var, width=10).grid(row=0, column=3, sticky='w', padx=5, pady=5)

        ttk.Label(lf_loinc, text="Método:").grid(row=1, column=0, padx=5, pady=5)
        self.metodo_var = tk.StringVar(value="Auscultatorio")
        ttk.Entry(lf_loinc, textvariable=self.metodo_var).grid(row=1, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

        ttk.Label(lf_loinc, text="Sitio Cuerpo:").grid(row=2, column=0, padx=5, pady=5)
        self.sitio_var = tk.StringVar(value="Brazo izquierdo")
        ttk.Entry(lf_loinc, textvariable=self.sitio_var).grid(row=2, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

        ttk.Label(lf_loinc, text="Brazalete:").grid(row=3, column=0, padx=5, pady=5)
        self.tamano_var = tk.StringVar(value="Adulto estandar")
        ttk.Entry(lf_loinc, textvariable=self.tamano_var).grid(row=3, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

        ttk.Label(lf_loinc, text="Dispositivo:").grid(row=4, column=0, padx=5, pady=5)
        self.dispositivo_var = tk.StringVar(value="Esfigmomanometro manual")
        ttk.Entry(lf_loinc, textvariable=self.dispositivo_var).grid(row=4, column=1, columnspan=3, sticky='ew', padx=5, pady=5)

        ttk.Button(self.top, text="Guardar", command=self.save).pack(pady=10)

    def prefill(self):
        self.id_paciente_var.set(self.tension.get('id_paciente', ''))
        self.estado_var.set(self.tension.get('estado', ''))
        self.fecha_var.set(str(self.tension.get('fecha', ''))[:10])
        self.valoracion_var.set(self.tension.get('valoracion', ''))
        self.valor_en_rango_var.set(self.tension.get('valor_en_rango', False))

        valores = self.tension.get('valores', {})
        if isinstance(valores, dict):
            self.sistolica_var.set(valores.get('sistolica', 120))
            self.diastolica_var.set(valores.get('diastolica', 80))
            self.metodo_var.set(valores.get('metodo', 'Auscultatorio'))
            self.sitio_var.set(valores.get('sitio_cuerpo', 'Brazo izquierdo'))
            self.tamano_var.set(valores.get('tamano_brazalete', 'Adulto estandar'))
            self.dispositivo_var.set(valores.get('dispositivo', 'Esfigmomanometro manual'))

    def save(self):
        try:
            id_paciente = self.id_paciente_var.get()
            estado = self.estado_var.get()
            fecha = self.fecha_var.get()
            valoracion = self.valoracion_var.get()
            valor_en_rango = self.valor_en_rango_var.get()

            valores_loinc = {
                'sistolica': self.sistolica_var.get(),
                'diastolica': self.diastolica_var.get(),
                'metodo': self.metodo_var.get(),
                'sitio_cuerpo': self.sitio_var.get(),
                'tamano_brazalete': self.tamano_var.get(),
                'dispositivo': self.dispositivo_var.get()
            }

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

            # Para pasar 'valores' sin romper el controlador, podemos inyectarlo en el schema de alta
            # pero el método create() del controller no recibe 'valores'. 
            # Modificaremos el controller o usaremos args
            if self.tension:
                self.controller.update(str(self.tension['_id']), {
                    'id_paciente': id_paciente.strip(), 'estado': estado.strip(),
                    'fecha': fecha.strip(), 'valoracion': valoracion.strip(),
                    'valor_en_rango': valor_en_rango,
                    'valores': valores_loinc,
                })
            else:
                self.controller.create(id_paciente.strip(), estado.strip(), fecha.strip(), valoracion.strip(), valor_en_rango, valores=valores_loinc)

            self.parent.load_data()
            show_toast(self.parent.winfo_toplevel(), 
                       "Medición actualizada" if self.tension else "Medición registrada", 
                       type="success")
            if self.on_saved:
                self.on_saved()
            self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Errores de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))