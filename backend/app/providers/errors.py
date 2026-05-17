from __future__ import annotations


class ProviderError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class ProviderConfigError(ProviderError):
    pass


class ProviderCallError(ProviderError):
    pass


class ProviderResponseError(ProviderError):
    pass
