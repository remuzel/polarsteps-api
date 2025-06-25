from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseRequest(ABC):
    def __init__(self, headers: Optional[dict[str, str]] = None):
        self.headers = headers or {}

    @abstractmethod
    def get_endpoint(self) -> str:
        pass

    @abstractmethod
    def get_method(self) -> str:
        pass


class BaseResponse:
    def __init__(self, data: Any, status_code: int, headers: dict[str, str]):
        self.data = data
        self.status_code = status_code
        self.headers = headers

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 400

    @property
    def is_error(self) -> bool:
        return not self.is_success
