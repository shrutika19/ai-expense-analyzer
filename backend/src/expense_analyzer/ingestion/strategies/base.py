from abc import ABC, abstractmethod
from typing import Any


class IngestionStrategy(ABC):

    @abstractmethod
    def read(self, source: Any) -> list[dict[str, Any]]:
        """Read raw expense data from the source."""