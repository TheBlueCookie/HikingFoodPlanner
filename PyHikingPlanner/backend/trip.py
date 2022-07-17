from dataclasses import dataclass, field

import pandas as pd

from typing import Union

import numpy as np
import numpy.typing as npt

from PyHikingPlanner.app.connector import LocalDatabase
from PyHikingPlanner.backend.food import LocalDatabaseComponent, Meal, MealType, n_nutrients


@dataclass
class Trip(LocalDatabaseComponent):
    """Implements the base class for any planning project.

    Args:
        duration (int): Initial duration in days."""

    duration: int = 1
    meal_plan: list[dict[int, Union[Meal, None]]] = field(default_factory=list[dict])
    meal_types: list[MealType] = field(default_factory=list[MealType])
    sep: str = ','
    linked_database: LocalDatabase = None
    linked_db_code: int = None

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

    def link_database(self, db: LocalDatabase):
        self.linked_database = db

    def save_trip(self, f_path: str):
        """
        Saves trip to .csv file

        :param f_path: Full path to file.
        """
        if self.linked_database is None:
            raise Exception('No Database linked!')
        with open(f_path, 'w') as f:
            f.write(f'{self.linked_database.CODE}\n')
            f.write(f'{self.linked_database.name}\n')
            f.write(
                f'day{self.sep}{self.meal_types[0].name}{self.sep}{self.meal_types[1].name}{self.sep}'
                f'{self.meal_types[2].name}{self.sep}{self.meal_types[3].name}\n')

            for i in range(self.duration):
                day_plan = self.meal_plan[i]
                save_list = []
                for meal in day_plan.values():
                    if meal is not None:
                        save_list.append(meal.CODE)
                    else:
                        save_list.append('')
                f.write(f'{i + 1}{self.sep}{save_list[0]}{self.sep}{save_list[1]}{self.sep}{save_list[2]}{self.sep}'
                        f'{save_list[3]}\n')

    def set_meal_from_df(self, df: pd.DataFrame, day: int):
        day_ind = day - 1
        for i, col in enumerate(df):
            if i == 0:
                continue
            meal_code = df[col][day_ind]
            if meal_code is not None:
                meal = self.linked_database.get_meal_by_code(code=meal_code)
                self.set_meal_at_day(meal=meal, day_ind=day_ind, meal_type=self.linked_database.meal_types[i-1])

    def verify_linked_database(self, linked_db: LocalDatabase) -> bool:
        if linked_db.CODE == self.linked_db_code:
            return True
        else:
            return False

    def load_linked_db_code(self, f_path: str):
        with open(f_path, 'r') as f:
            self.linked_db_code = int(f.readline())

    def load_trip(self, f_path: str):
        self.duration = 0
        self.meal_plan = []
        trip_df = pd.read_csv(f_path, sep=self.sep, skiprows=2)

        for i, day in enumerate(trip_df.day):
            self.add_day()
            self.set_meal_from_df(df=trip_df, day=i+1)
