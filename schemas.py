"""
Esquemas de validación para TruelieBot.

Este módulo define esquemas Marshmallow para validar
las entradas a los diferentes endpoints de la API.
"""

from typing import Any, Dict, List, Optional, Union

from marshmallow import Schema, ValidationError, fields, validate, validates


class FeedbackSchema(Schema):
    """Esquema para validar feedback de usuario."""

    analisis_id = fields.Integer(required=True)
    usuario_id = fields.Integer()  # Opcional, se puede tomar del token
    tipo = fields.String(
        required=True, validate=validate.OneOf(["positivo", "negativo", "sugerencia"])
    )
    comentario = fields.String(validate=validate.Length(max=1000))


class PatronSchema(Schema):
    """Esquema para validar patrones de manipulación."""

    descripcion = fields.String(required=True, validate=validate.Length(min=3, max=200))
    expresion_regular = fields.String(
        required=True, validate=validate.Length(min=2, max=500)
    )
    creado_por = fields.Integer()  # Opcional, se puede tomar del token
    validado = fields.Boolean(default=False)

    @validates("expresion_regular")
    def validate_regex(self, value: str) -> None:
        """
        Valida que la expresión regular sea válida.
        """
        import re

        try:
            re.compile(value)
        except re.error:
            raise ValidationError("La expresión regular no es válida")


class AnalisisSchema(Schema):
    """Esquema para validar análisis de conversaciones."""

    conversacion_id = fields.Integer(required=True)
    usuario_id = fields.Integer()  # Opcional, se puede tomar del token
    texto = fields.String(required=True, validate=validate.Length(min=1, max=5000))
    modelo = fields.String(default="gpt-3.5-turbo")


class LoginSchema(Schema):
    """Esquema para validar login de usuario."""

    usuario_id = fields.Integer(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8, max=100))
    role = fields.String(validate=validate.OneOf(["user", "admin"]), default="user")


def validate_request(schema_class: Schema, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida una solicitud contra un esquema.

    Args:
        schema_class: Clase de esquema Marshmallow
        data: Datos a validar

    Returns:
        Datos validados y deserializados

    Raises:
        ValidationError: Si la validación falla
    """
    schema = schema_class()
    return schema.load(data)
