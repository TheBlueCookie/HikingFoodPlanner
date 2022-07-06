from dataclasses import dataclass, field
from food_backend import Meal, LocalDatabaseComponent, MealType, n_nutrients
from typing import Union

import numpy as np
import numpy.typing as npt


@dataclass
class Trip(LocalDatabaseComponent):
    """Implements the base class for any planning project.

    Args:
        duration (int): Initial duration in days."""

    duration: int = 1
    meal_plan: list[dict[int, Union[Meal, None]]] = field(default_factory=list[dict])

    def __post_init__(self):
        for i in range(self.duration):
            self.add_day(init_mode=True)

    def add_day(self, init_mode=False) -> bool:
        self.meal_plan.append({0: None, 1: None, 2: None, 3: None})
        if not init_mode:
            self.duration += 1
        return True

    def set_meal_at_day(self, meal: Meal, day_ind: int, meal_type: MealType) -> bool:
        if day_ind > self.duration - 1:
            return False

        self.meal_plan[day_ind][meal_type.CODE] = meal
        return True

    def remove_meal_at_day(self, day_ind: int, meal_type: MealType) -> bool:
        if day_ind > self.duration - 1:
            return False

        self.meal_plan[day_ind][meal_type.CODE] = None
        return True

    def get_day_summary(self, day_ind) -> (npt.NDArray, float, float, int):
        if day_ind > self.duration - 1:
            return False

        nutrition = np.zeros(n_nutrients)
        cost = 0
        weight = 0
        cooking_count = 0
        for i, meal in enumerate(self.meal_plan[day_ind].values()):
            if meal is not None:
                nutrition = nutrition + meal.nutrition
                cost += meal.cost
                weight += meal.weight
                cooking_count += int(meal.cooking)

        return nutrition, cost, weight, cooking_count

    def get_meal_plan_summary(self) -> (npt.NDArray, float, float, int):
        nutrition = np.zeros(n_nutrients)
        cost = 0
        weight = 0
        cooking_count = 0
        for i, day in enumerate(self.meal_plan):
            day_nut, day_cost, day_weight, day_cooking = self.get_day_summary(day_ind=i)
            nutrition = nutrition + day_nut
            cost += day_cost
            weight += day_weight
            cooking_count += day_cooking

        return nutrition, cost, weight, cooking_count, self.duration
