import tkinter as tk
from styles.styles import BG_CARD, TEXT_WHITE, FONT

class Toast(tk.Toplevel):
    """
    Componente de notificación temporal (Toast) que aparece y desaparece suavemente.
    """
    def __init__(self, parent, message, type="info", duration=3000):
        super().__init__(parent)
        
        # Configuración de ventana sin bordes y siempre encima
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)  # Inicia transparente para el fade-in
        
        # Determinar colores e icono según el tipo
        bg_color = BG_CARD
        icon = "ℹ️"
        
        if type == "success":
            bg_color = "#064E3B"  # Verde oscuro esmeralda
            icon = "✅"
        elif type == "error":
            bg_color = "#7F1D1D"  # Rojo oscuro
            icon = "❌"
        elif type == "warning":
            bg_color = "#78350F"  # Ámbar oscuro
            icon = "⚠️"

        self.configure(bg=bg_color)
        
        # Contenido
        container = tk.Frame(self, bg=bg_color, padx=25, pady=15)
        container.pack()
        
        # Borde redondeado simulado (opcional, aquí usamos un frame con padding)
        self.label = tk.Label(
            container, 
            text=f"{icon}  {message}", 
            fg=TEXT_WHITE, 
            bg=bg_color, 
            font=(FONT, 11, "bold"),
            wraplength=400
        )
        self.label.pack()

        # Posicionamiento dinámico
        self.update_idletasks()
        self._position_toast(parent)
        
        # Iniciar animaciones
        self._fade_in()
        self.after(duration, self._fade_out)

    def _position_toast(self, parent):
        """Posiciona el toast en la parte inferior central de la ventana principal."""
        w = self.winfo_width()
        h = self.winfo_height()
        
        # Obtener coordenadas de la ventana padre
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        
        # Calcular posición (Centro inferior con margen)
        x = px + (pw // 2) - (w // 2)
        y = py + ph - h - 50
        
        self.geometry(f"+{int(x)}+{int(y)}")

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 0.95:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(20, self._fade_in)

    def _fade_out(self):
        try:
            alpha = self.attributes("-alpha")
            if alpha > 0.0:
                alpha -= 0.1
                self.attributes("-alpha", alpha)
                self.after(20, self._fade_out)
            else:
                self.destroy()
        except tk.TclError:
            pass # La ventana ya pudo haber sido destruida

def show_toast(parent, message, type="info", duration=3000):
    """Función de utilidad para mostrar un toast rápidamente."""
    Toast(parent, message, type, duration)
