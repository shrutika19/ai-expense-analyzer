from typing import Any

from expense_analyzer.preprocessing.processors.base import (
    PreprocessingProcessor,
)


class PreprocessingPipeline:

    def __init__(
        self,
        processors: list[PreprocessingProcessor],
    ) -> None:
        self.processors = processors

    def process(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        processed_records = records

        for processor in self.processors:
            processed_records = processor.process(processed_records)

        return processed_records