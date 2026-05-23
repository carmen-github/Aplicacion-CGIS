import tkinter as tk
from tkinter import ttk, messagebox
from styles.styles import apply_window_style
from views.components.toast import show_toast


class AddEditListDialog:
    def __init__(self, parent, controller, patient_controller, record: dict | None, patient_id: str | None = None, patient_name: str | None = None, on_saved=None):
        self.parent = parent
        self.controller = controller
        self.patient_controller = patient_controller
        self.record = record
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.on_saved = on_saved
        self.top = tk.Toplevel(parent)
        self.top.title("Editar solicitud" if record else "Nueva solicitud")
        apply_window_style(self.top)
        self.top.resizable(False, False)
        self.create_form()
        if record:
            self.prefill()

    def create_form(self):
        if self.patient_id and self.patient_name:
            ttk.Label(self.top, text=f"Paciente: {self.patient_name}", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, columnspan=2, padx=5, pady=8, sticky='w')
        else:
            ttk.Label(self.top, text="Paciente:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
            self.patient_var = tk.StringVar()
            patient_ids = [str(p['_id']) for p in self.patient_controller.read_all()]
            self.patient_combo = ttk.Combobox(self.top, textvariable=self.patient_var, values=patient_ids, state='readonly')
            self.patient_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Fecha y Hora (YYYY-MM-DD HH:MM):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.fecha_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.fecha_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Servicio:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.servicio_var = tk.StringVar()
        ttk.Combobox(self.top, textvariable=self.servicio_var, values=['Consulta', 'Enfermeria'], state='readonly').grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Estado:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.estado_var = tk.StringVar(value='Pendiente')
        ttk.Combobox(self.top, textvariable=self.estado_var, values=['Pendiente', 'Atendido', 'Anulado'], state='readonly').grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Patrón:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.patron_var = tk.StringVar(value='Unico')
        ttk.Combobox(self.top, textvariable=self.patron_var, values=['Unico', 'Diario', 'Semanal'], state='readonly').grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Repeticiones:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.repeticiones_var = tk.IntVar(value=1)
        ttk.Entry(self.top, textvariable=self.repeticiones_var, width=8).grid(row=5, column=1, padx=5, pady=5, sticky='w')

        ttk.Button(self.top, text="Guardar", command=self.save).grid(row=6, column=0, columnspan=2, pady=10)

    def prefill(self):
        self.patient_var.set(str(self.record.get('id_paciente', '')))
        self.fecha_var.set(str(self.record.get('fechaHora', '')))
        self.servicio_var.set(self.record.get('servicio', ''))
        self.estado_var.set(self.record.get('estado', 'Pendiente'))
        self.patron_var.set(self.record.get('patron', 'Unico'))
        self.repeticiones_var.set(self.record.get('repeticiones', 1))

    def save(self):
        try:
            id_paciente = self.patient_id or self.patient_var.get().strip()
            data = {
                'id_paciente': id_paciente,
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
