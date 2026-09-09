from enum import Enum


class ExpenseCategory(str, Enum):
    FOOD = "Food"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    RENT = "Rent"
    OTHER = "Other"