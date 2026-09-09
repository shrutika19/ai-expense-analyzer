from abc import ABC, abstractmethod
from typing import Any


class PreprocessingProcessor(ABC):

    @abstractmethod
    def process(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Process raw expense records."""