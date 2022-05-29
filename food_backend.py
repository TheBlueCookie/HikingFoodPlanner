from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt
from typing import Union

n_nutrients = 8


@dataclass
class LocalDatabaseComponent:
    name: str


@dataclass
class Ingredient(LocalDatabaseComponent):
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
    nutritional_values: npt.NDArray[float]
    cooking: bool = False
    water: bool = False
    price_per_unit: float = np.nan
    unit_size: float = np.nan
    price_per_gram: float = np.nan

    def __post_init__(self):
        super().__init__(name=self.name)
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
class Meal(LocalDatabaseComponent):
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
    ingredients: list[list[Union[Ingredient, float]]] = field(default_factory=list[list])
    cooking: bool = False
    water: bool = False
    cost: float = 0
    weight: float = 0
    nutrition: npt.NDArray[float] = field(default=np.zeros(n_nutrients))

    def __post_init__(self):
        super().__init__(name=self.name)

    def add_ingredient(self, item: Ingredient, amount: float):
        """
        Adds ingredient to meal.

        :param item: Item to add.
        :param amount: Amount in grams.
        """
        if item not in self.get_all_ingredients():
            self.ingredients.append([item, amount])
            if item.cooking:
                self.cooking = True
            if item.water:
                self.water = True
            self.cost += item.price_per_gram * amount
            self.weight += amount
            self.nutrition = self.nutrition + (item.nutritional_values * 0.01 * amount)
        else:
            self.update_ingredient_amount(item=item, amount=amount)
            self.update_nutrients_weight_cost()

    def get_all_ingredients(self) -> list[Ingredient]:
        all_ins = []
        for i in self.ingredients:
            all_ins.append(i[0])

        return all_ins

    def update_nutrients_weight_cost(self):
        self.cost = 0
        self.weight = 0
        self.nutrition = np.zeros(n_nutrients)
        for i, a in self.ingredients:
            self.cost += i.price_per_gram * a
            self.weight += a
            self.nutrition = self.nutrition + (i.nutritional_values * 0.01 * a)

    def update_ingredient_amount(self, item: Ingredient, amount: float):
        if item in self.get_all_ingredients():
            ind = self.get_all_ingredients().index(item)
            self.ingredients[ind][1] = amount
            self.update_nutrients_weight_cost()

    def get_copy(self):
        return Meal(name=self.name, own_type=self.own_type, ingredients=self.ingredients, cooking=self.cooking,
                    water=self.water, weight=self.weight, cost=self.cost, nutrition=self.nutrition.copy())
