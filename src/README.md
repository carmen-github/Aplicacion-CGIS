# Aplicación Médica con Tkinter y PyMongo

Esta aplicación proporciona una interfaz gráfica para gestionar pacientes y sus mediciones de tensión arterial, utilizando MongoDB como base de datos.

## Arquitectura

El proyecto sigue una arquitectura en capas con separación clara de responsabilidades:

```
src/
├── main.py                 # Punto de entrada de la aplicación
├── database/               # Conexión a MongoDB
│   └── connection.py
├── esquemas/               # Validaciones Pydantic (una clase por entidad)
│   ├── patient_schema.py   # PatientSchema
│   └── tension_schema.py   # TensionSchema
├── models/                 # Clases de datos (Patient, Tension)
│   ├── patient.py
│   └── tension.py
├── repository/             # Acceso a datos — CRUD contra MongoDB
│   ├── patient_repository.py
│   └── tension_repository.py
├── servicios/              # Lógica de negocio — una clase por operación
│   ├── alta_paciente.py
│   ├── baja_paciente.py
│   ├── modificacion_paciente.py
│   ├── consulta_paciente.py
│   ├── alta_tension.py
│   ├── baja_tension.py
│   ├── modificacion_tension.py
│   └── consulta_tension.py
├── controllers/            # Orquestadores que conectan vistas con servicios
│   ├── patient_controller.py
│   └── tension_controller.py
├── views/                  # Interfaz de usuario (Tkinter)
│   ├── main_window.py
│   ├── patient_view.py
│   └── tension_view.py
└── styles/                 # Estilos y temas para la UI
    └── styles.py
```

### Flujo de datos

```
Vista → Controller → Servicio (validación) → Repository (MongoDB)
```

| Capa | Responsabilidad |
|------|----------------|
| **esquemas/** | Validaciones Pydantic puras (campos obligatorios, formatos, rangos) |
| **models/** | Clases de datos con métodos `to_dict()`, `from_dict()` y `validate()` |
| **repository/** | Operaciones CRUD directas contra las colecciones de MongoDB |
| **servicios/** | Lógica de negocio: cada clase encapsula una operación (alta, baja, modificación, consulta) |
| **controllers/** | Orquestan los servicios y exponen una interfaz unificada a las vistas |
| **views/** | Interfaz gráfica Tkinter (formularios, tablas, diálogos) |

## Requisitos

- Python 3.x
- MongoDB corriendo en localhost:27017
- Base de datos 'mi_app' con colecciones 'pacientes' y 'tensiones'

## Instalación

1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar: `python main.py`

## Uso

- Pantalla principal con botones para Pacientes y Tensiones.
- CRUD completo para ambas entidades con validación automática.