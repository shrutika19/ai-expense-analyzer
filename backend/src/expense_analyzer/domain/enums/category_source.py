from enum import Enum


class CategorySource(str, Enum):
    MANUAL = "manual"
    ML = "ml"