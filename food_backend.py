from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt

n_nutrients = 8


@dataclass
class Ingredient:
    """Represents an arbitrary food item.

    Args:
        name (str): Name of item.
        types (np.array): Indices of food types this item belongs to.
        cooking (bool): If item requires cooking.
        water (bool): If item requires added water.
        price_per_unit (float): Price per unit as bought from store.
        unit_size (float): Size of one unit in grams.
        nutritional_values (np.array): Energy, fat, saturated fat, fiber, carbs, sugar, protein, salt."""

    name: str
    types: npt.NDArray[int]
    cooking: bool
    water: bool
    price_per_unit: float
    unit_size: float
    nutritional_values: npt.NDArray[float]
    price_per_gram: float = 0

    def __post_init__(self):
        self.price_per_gram = self.price_per_unit / self.unit_size


@dataclass
class MealType:
    """Links a numerical value to a string literal and implements a basic type of meal, such as breakfast, lunch,
    dinner...

    Args:
        name (str): Name of meal type.
        code (int): Numerical representation of meal type."""

    name: str
    code: int


@dataclass
class Meal:
    """Implements a single meal belonging to one or several MealTypes, consisting of several Ingredient objects.

    Args:
        name (str): Name of meal.
        own_type (MealType): Type of meal.
        ingredients (list[list[Ingredient, float]]): List of list of Ingredient object and amount in grams.
        cooking (bool): If cooking is required.
        water (bool): If water is required.
        cost (float): Cost of all ingredients.
        weight (float): Total weight, excluding water.
        nutrition (ndarray): Total nutritional values of meal."""

    name: str
    own_type: MealType
    ingredients: list[list[Ingredient, float]] = field(default_factory=list[list])
    cooking: bool = False
    water: bool = False
    cost: float = 0
    weight: float = 0
    nutrition: npt.NDArray[float] = field(default=np.zeros(n_nutrients))

    def __post_init__(self):
        self.update_all_fields()

    def add_ingredient(self, item: Ingredient, amount: float):
        """
        Adds ingredient to meal.

        :param item: Item to add.
        :param amount: Amount in grams.
        """
        self.ingredients.append([item, amount])
        if item.cooking:
            self.cooking = True
        if item.water:
            self.water = True
        self.cost += item.price_per_gram * amount
        self.weight += amount
        self.nutrition += item.nutritional_values * 0.01 * amount

    def update_all_fields(self):
        """
        Updates all relevant fields.
        """
        self.cost = 0
        self.weight = 0
        self.nutrition = np.zeros(n_nutrients)

        for item, amount in self.ingredients:

            if item.cooking:
                self.cooking = True

            if item.water:
                self.water = True

            self.cost += item.price_per_gram * amount
            self.weight += amount
            self.nutrition += item.nutritional_values * 0.01 * amount
