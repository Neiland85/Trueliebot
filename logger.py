"""
Configuración de logging para TruelieBot.

Este módulo proporciona un logger estructurado para registrar
eventos y errores de forma consistente en toda la aplicación.
"""

import datetime
import json
import logging
import os
from typing import Any, Dict, Optional, Union


class JsonFormatter(logging.Formatter):
    """
    Formateador que genera logs en formato JSON estructurado.
    """

    def __init__(self) -> None:
        super().__init__()
        self.default_fields = {
            "timestamp": "",
            "level": "",
            "name": "",
            "message": "",
        }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea el registro como JSON.
        """
        log_data = {**self.default_fields}

        # Datos básicos
        log_data["timestamp"] = datetime.datetime.fromtimestamp(
            record.created
        ).isoformat()
        log_data["level"] = record.levelname
        log_data["name"] = record.name
        log_data["message"] = record.getMessage()

        # Datos adicionales
        if hasattr(record, "data") and isinstance(record.data, dict):
            for key, value in record.data.items():
                log_data[key] = value

        # Información de excepción, si existe
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        # Convertir a JSON
        return json.dumps(log_data)


def setup_logger(
    name: str, log_level: str = "INFO", log_to_file: bool = True
) -> logging.Logger:
    """
    Configura y devuelve un logger estructurado.

    Args:
        name: Nombre del logger
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Si True, también escribe logs a un archivo

    Returns:
        Logger configurado
    """
    # Convertir nivel de log
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    logger.handlers = []  # Borrar handlers existentes

    # Handler de consola con formato JSON
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)

    # Handler de archivo si se solicita
    if log_to_file:
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(os.path.join(log_dir, f"{name}.log"))
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger


def log_with_data(
    logger: logging.Logger,
    level: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Registra un evento con datos adicionales estructurados.

    Args:
        logger: Logger configurado
        level: Nivel de log (debug, info, warning, error, critical)
        message: Mensaje de log
        data: Datos adicionales para incluir en el log
    """
    log_method = getattr(logger, level.lower())

    # Crear una copia del registro con datos adicionales
    extra = {"data": data or {}}
    log_method(message, extra=extra)
