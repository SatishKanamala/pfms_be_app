from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHERS = "others"

class Category(str, Enum):
    INCOME = "income"
    EXPENSES = "expenses"
    BUDGET = "budget"
    INVESTMENTS = "investments"
    