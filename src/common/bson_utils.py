from datetime import date, datetime, time
from typing import Any


def normalize_bson_dates(value: Any) -> Any:
    """Convierte fechas date a datetime para compatibilidad con MongoDB."""
    if isinstance(value, dict):
        return {key: normalize_bson_dates(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_bson_dates(item) for item in value]
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, time.min)
    return value
