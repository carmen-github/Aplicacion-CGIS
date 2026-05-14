"""Utilidades compartidas para extracción de errores de validación Pydantic."""

from pydantic import ValidationError


def extraer_errores(ve: ValidationError) -> list[str]:
    """Convierte los errores de un ValidationError de Pydantic en mensajes legibles.

    Args:
        ve: Excepción ValidationError de Pydantic.

    Returns:
        Lista de strings con los mensajes de error.
    """
    errores = []
    for error in ve.errors():
        msg = error.get('msg', '')
        campo = error.get('loc', ('',))[0]

        if 'Value error, ' in msg:
            msg = msg.replace('Value error, ', '')
        elif 'Input should be a valid boolean' in msg:
            msg = f"El campo '{campo}' debe ser verdadero o falso."
        elif 'String should have at least' in msg:
            msg = f"El campo '{campo}' es obligatorio y no puede estar vacío."
        elif 'missing' in msg.lower():
            msg = f"El campo '{campo}' es obligatorio."

        errores.append(msg)
    return errores
