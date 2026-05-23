from datetime import date, datetime


class ConsultaTension:
    """Servicio para consultar tensiones."""

    def __init__(self, tension_repository):
        self.repository = tension_repository

    def obtener_todas(self):
        """Devuelve todas las tensiones."""
        return self.repository.find_all()

    def obtener_por_id(self, id):
        """Busca una tensión por su _id. Devuelve Tension o None."""
        return self.repository.find_by_id(id)

    def obtener_por_paciente(self, id_paciente):
        """Devuelve todas las tensiones de un paciente dado."""
        return self.repository.find_by_patient_id(id_paciente)

    def obtener_estudio_por_paciente(self, id_paciente, ultimas_n: int | None = None):
        """Calcula métricas de estudio para un paciente."""
        tensiones = self.obtener_por_paciente(id_paciente)
        if not tensiones:
            return {
                'paciente_id': id_paciente,
                'ultimas_n': ultimas_n,
                'total_tomas': 0,
                'media_sistolica': None,
                'media_diastolica': None,
                'ultima_toma': None,
            }

        def parse_date(value):
            if isinstance(value, date):
                return value
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, str):
                for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
            return None

        tensiones = [t for t in tensiones]
        tensiones.sort(key=lambda t: parse_date(t.get('fecha')) or date.min, reverse=True)

        if ultimas_n and ultimas_n > 0:
            seleccionadas = tensiones[:ultimas_n]
        else:
            seleccionadas = tensiones

        valores_validos = []
        for t in seleccionadas:
            valores = t.get('valores', {}) or {}
            try:
                sistolica = float(valores.get('sistolica'))
                diastolica = float(valores.get('diastolica'))
            except (TypeError, ValueError):
                continue
            valores_validos.append((sistolica, diastolica))

        if valores_validos:
            media_sistolica = sum(v[0] for v in valores_validos) / len(valores_validos)
            media_diastolica = sum(v[1] for v in valores_validos) / len(valores_validos)
        else:
            media_sistolica = None
            media_diastolica = None

        ultima_toma = tensiones[0]

        return {
            'paciente_id': id_paciente,
            'ultimas_n': ultimas_n,
            'total_tomas': len(tensiones),
            'tomas_utilizadas': len(seleccionadas),
            'media_sistolica': media_sistolica,
            'media_diastolica': media_diastolica,
            'ultima_toma': ultima_toma,
        }
