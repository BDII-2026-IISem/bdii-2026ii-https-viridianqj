import hashlib
import secrets


def generate_refresh_value() -> str:
    """Valor aleatorio que se entrega al cliente (nunca se guarda en claro)."""
    return secrets.token_urlsafe(48)


def hash_refresh_value(value: str) -> str:
    """SHA-256 en hexadecimal (64 caracteres)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
