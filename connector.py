import numpy as np
import numpy.typing as npt
from food_backend import Ingredient, MealType, Meal
from trip_backend import Trip
import pandas as pd


class LocalDatabase:
    def __init__(self):
        self.ingredients = []
        self.meal_types = []
        self.meals = []
        self.trips = []
        self.sep = ';'
        self.i_names = []

    def save(self, f_name):
        self.save_ingredients_to_file(f_name)

    def load(self, files):
        self.load_ingredients_from_file(files[0])

    def save_ingredients_to_file(self, f_name: str):
        with open(f'{f_name}_ingredients.csv', 'w') as file:
            file.write(
                f'name{self.sep} energy{self.sep} fat{self.sep} sat_fat{self.sep} fiber{self.sep} carbs{self.sep}'
                f'sugar{self.sep} protein{self.sep} salt{self.sep} cooking{self.sep} water{self.sep} '
                f'price_per_unit{self.sep} unit_size{self.sep} price_per_gram{self.sep} types\n'.replace(' ', ''))
            for i in self.ingredients:
                types = ''
                for j in i.types:
                    types += f'{j}--'

                file.write(
                    f'{i.name}{self.sep} {i.nutritional_values[0]}{self.sep} {i.nutritional_values[1]}{self.sep} '
                    f'{i.nutritional_values[2]}{self.sep} {i.nutritional_values[3]}{self.sep} '
                    f'{i.nutritional_values[4]}{self.sep} {i.nutritional_values[5]}{self.sep} '
                    f'{i.nutritional_values[6]}{self.sep} {i.nutritional_values[7]}{self.sep} '
                    f'{i.cooking}{self.sep} {i.water}{self.sep} {i.price_per_unit}{self.sep} '
                    f'{i.unit_size}{self.sep} {i.price_per_gram}{self.sep} {types}\n')

    def load_ingredients_from_file(self, f_name: str):
        self.ingredients = []
        data = pd.read_csv(f_name, sep=self.sep)
        print(data.types)
        for index, name in enumerate(data.name):
            types = [int(i) for i in data.types[index].split('--')[:-1]]
            item = Ingredient(name=name, nutritional_values=np.array(data.iloc[index, 1:9]),
                              types=types, cooking=bool(data.cooking[index]),
                              water=bool(data.water[index]), price_per_unit=float(data.price_per_unit[index]),
                              unit_size=float(data.unit_size[index]), price_per_gram=float(data.price_per_gram[index]))
            self.ingredients.append(item)

        print(self.ingredients)

    def add_meal(self, item: Meal):
        self.meals.append(item)

    def add_meal_type(self, item: MealType):
        self.meal_types.append(item)

    def add_trip(self, item: Trip):
        self.trips.append(item)

    def add_ingredient(self, name: str, nutrients: npt.NDArray, types: npt.NDArray, water: bool, cooking: bool,
                       price_per_unit: float, unit_size: float):
        ingredient = Ingredient(name=name, nutritional_values=nutrients, water=water, cooking=cooking,
                                price_per_unit=price_per_unit, unit_size=unit_size, types=types)
        self.ingredients.append(ingredient)

    def get_ingredient_names(self):
        names = []
        for i in self.ingredients:
            names.append(i.name)

        self.i_names = names

        return self.i_names
