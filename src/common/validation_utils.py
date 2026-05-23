from pydantic import ValidationError

def validate_schema(schema_class, **kwargs):
    """Instancia el esquema Pydantic y devuelve un diccionario. Levanta ValueError si falla."""
    try:
        instance = schema_class(**kwargs)
        return instance.model_dump(by_alias=True)
    except ValidationError as e:
        errors = e.errors()
        if errors:
            err = errors[0]
            field = err.get('loc', ['desconocido'])[0]
            msg = err.get('msg', 'Error de validación')
            raise ValueError(f"Campo '{field}': {msg}")
        raise ValueError(str(e))
