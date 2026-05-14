import tkinter.ttk as ttk

# ── Paleta de colores — Azul oscuro + acentos rojos ────────────────────────
BG_DARK       = '#0F1B2D'   # fondo principal oscuro
BG_CARD       = '#1A2742'   # fondo tarjetas / paneles
BG_INPUT      = '#243352'   # fondo campos de texto
BG_SIDEBAR    = '#162036'   # barra lateral / separadores

# Acentos
ACCENT_BLUE   = '#3B82F6'   # azul vibrante
ACCENT_BLUE_H = '#2563EB'   # azul hover
ACCENT_RED    = '#EF4444'   # rojo vibrante
ACCENT_RED_H  = '#DC2626'   # rojo hover
ACCENT_GREEN  = '#22C55E'   # verde confirmación

# Texto
TEXT_WHITE     = '#F1F5F9'   # texto principal
TEXT_MUTED     = '#94A3B8'   # texto secundario
TEXT_DARK      = '#1E293B'   # texto oscuro (para fondos claros)

# Bordes
BORDER_COLOR   = '#334155'
BORDER_FOCUS   = '#3B82F6'

# Fuente (segura en Windows)
FONT           = 'Segoe UI'

# ── Retrocompatibilidad con imports existentes ─────────────────────────────
BG_COLOR       = BG_DARK
BTN_MENU_BG    = ACCENT_RED
TEXT_COLOR      = TEXT_WHITE


def apply_styles():
    """Aplica el tema oscuro moderno a toda la aplicación."""
    style = ttk.Style()
    style.theme_use('alt')

    # ── Frames ─────────────────────────────────────────────────────────────
    style.configure('TFrame', background=BG_DARK)
    style.configure('Card.TFrame', background=BG_CARD)

    # ── Labels ─────────────────────────────────────────────────────────────
    style.configure('TLabel',
        background=BG_DARK,
        foreground=TEXT_WHITE,
        font=(FONT, 11),
    )
    style.configure('Card.TLabel',
        background=BG_CARD,
        foreground=TEXT_WHITE,
        font=(FONT, 11),
    )
    style.configure('Title.TLabel',
        background=BG_DARK,
        foreground=TEXT_WHITE,
        font=(FONT, 20, 'bold'),
    )
    style.configure('Subtitle.TLabel',
        background=BG_DARK,
        foreground=TEXT_MUTED,
        font=(FONT, 11),
    )
    style.configure('Heading.TLabel',
        background=BG_DARK,
        foreground=TEXT_WHITE,
        font=(FONT, 16, 'bold'),
    )

    # ── Botones generales (azul) ───────────────────────────────────────────
    style.configure('TButton',
        font=(FONT, 11),
        padding=(16, 8),
        background=ACCENT_BLUE,
        foreground=TEXT_WHITE,
        borderwidth=0,
        relief='flat',
    )
    style.map('TButton',
        background=[('active', ACCENT_BLUE_H), ('pressed', ACCENT_BLUE_H)],
        foreground=[('active', TEXT_WHITE)],
    )

    # ── Botón de acento rojo (eliminar, etc.) ──────────────────────────────
    style.configure('Danger.TButton',
        font=(FONT, 11),
        padding=(16, 8),
        background=ACCENT_RED,
        foreground=TEXT_WHITE,
        borderwidth=0,
        relief='flat',
    )
    style.map('Danger.TButton',
        background=[('active', ACCENT_RED_H), ('pressed', ACCENT_RED_H)],
        foreground=[('active', TEXT_WHITE)],
    )

    # ── Botón de acento verde (guardar, confirmar) ─────────────────────────
    style.configure('Success.TButton',
        font=(FONT, 11),
        padding=(16, 8),
        background=ACCENT_GREEN,
        foreground=TEXT_DARK,
        borderwidth=0,
        relief='flat',
    )
    style.map('Success.TButton',
        background=[('active', '#16A34A'), ('pressed', '#16A34A')],
    )

    # ── Botón secundario (volver, cancelar) ────────────────────────────────
    style.configure('Secondary.TButton',
        font=(FONT, 11),
        padding=(16, 8),
        background=BG_CARD,
        foreground=TEXT_MUTED,
        borderwidth=1,
        relief='solid',
    )
    style.map('Secondary.TButton',
        background=[('active', BG_INPUT), ('pressed', BG_INPUT)],
        foreground=[('active', TEXT_WHITE)],
    )

    # ── Entradas de texto ──────────────────────────────────────────────────
    style.configure('TEntry',
        font=(FONT, 11),
        fieldbackground=BG_INPUT,
        foreground=TEXT_WHITE,
        insertcolor=TEXT_WHITE,  # color del cursor
        borderwidth=1,
        relief='solid',
    )

    # ── Combobox ───────────────────────────────────────────────────────────
    style.configure('TCombobox',
        font=(FONT, 11),
        fieldbackground=BG_INPUT,
        foreground=TEXT_WHITE,
        background=BG_INPUT,
        arrowcolor=TEXT_MUTED,
        borderwidth=1,
        relief='solid',
    )
    style.map('TCombobox',
        fieldbackground=[('readonly', BG_INPUT)],
        foreground=[('readonly', TEXT_WHITE)],
    )

    # ── Checkbutton ────────────────────────────────────────────────────────
    style.configure('TCheckbutton',
        background=BG_CARD,
        foreground=TEXT_WHITE,
        font=(FONT, 11),
    )
    style.map('TCheckbutton',
        background=[('active', BG_CARD)],
    )

    # ── LabelFrame ─────────────────────────────────────────────────────────
    style.configure('TLabelframe',
        background=BG_CARD,
        foreground=TEXT_WHITE,
        bordercolor=BORDER_COLOR,
    )
    style.configure('TLabelframe.Label',
        background=BG_CARD,
        foreground=TEXT_WHITE,
        font=(FONT, 12, 'bold'),
    )

    # ── Tabla (Treeview) ───────────────────────────────────────────────────
    style.configure('Treeview',
        font=(FONT, 10),
        background=BG_CARD,
        fieldbackground=BG_CARD,
        foreground=TEXT_WHITE,
        rowheight=32,
        borderwidth=0,
    )
    style.configure('Treeview.Heading',
        font=(FONT, 11, 'bold'),
        background=BG_SIDEBAR,
        foreground=TEXT_MUTED,
        borderwidth=0,
        relief='flat',
    )
    style.map('Treeview',
        background=[('selected', ACCENT_BLUE)],
        foreground=[('selected', TEXT_WHITE)],
    )
    
