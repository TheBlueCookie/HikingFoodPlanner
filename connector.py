import numpy as np
import numpy.typing as npt
from food_backend import Ingredient, MealType, Meal
from trip_backend import Trip
import pandas as pd

from food_backend import n_nutrients


class LocalDatabase:
    def __init__(self):
        self.ingredients = []
        self.meal_types = [MealType('Breakfast', 0), MealType('Lunch', 1), MealType('Dinner', 2), MealType('Snack', 3)]
        self.meals = []
        self.trips = []
        self.sep = ';'
        self.i_names = []
        self.string_true = ['true']

    def save(self, f_name):
        self.save_ingredients_to_file(f_name)

    def load(self, files):
        self.load_ingredients_from_file(files[0])

    def load_from_basefile(self, f_name: str):
        with open(f_name, 'r') as file:
            in_file = file.readline()

        self.load([in_file])

    def save_ingredients_to_file(self, f_name: str):
        with open(f'{f_name}_ingredients.csv', 'w') as file:
            file.write(
                f'name{self.sep} energy{self.sep} fat{self.sep} sat_fat{self.sep} carbs{self.sep}'
                f'sugar{self.sep} fiber{self.sep} protein{self.sep} salt{self.sep} cooking{self.sep} water{self.sep} '
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
        for index, name in enumerate(data.name):
            types = [int(i) for i in data.types[index].split('--')[:-1]]
            if data.water[index].lower().strip() in self.string_true:
                water = True
            else:
                water = False
            if data.cooking[index].lower().strip() in self.string_true:
                cooking = True
            else:
                cooking = False
            item = Ingredient(name=name, nutritional_values=np.array(data.iloc[index, 1:9]),
                              types=types, cooking=cooking, water=water,
                              price_per_unit=float(data.price_per_unit[index]), unit_size=float(data.unit_size[index]),
                              price_per_gram=float(data.price_per_gram[index]))
            self.ingredients.append(item)

    def get_ingredient_by_name(self, name: str) -> Ingredient:
        try:
            ind = self.get_ingredient_names().index(name)
            return self.ingredients[ind]
        except IndexError:
            pass

    def delete_ingredient_by_name(self, name: str):
        if name in self.get_ingredient_names():
            self.ingredients.pop(self.get_ingredient_names().index(name))

    def search_ingredients_by_name(self, search_text: str) -> list[str]:
        names = self.get_ingredient_names()
        hits = []
        search_len = len(search_text)
        if search_len <= 2:
            for name in names:
                if search_text == name[:search_len]:
                    hits.append(name)

        elif search_len > 2:
            for name in names:
                if search_text in name:
                    hits.append(name)

        return hits

    def num_to_meal_type(self, num: int) -> MealType:
        return self.meal_types[num]

    def add_meal(self, name: str, own_type: int, ingredients: list[list[Ingredient, float]]):
        nutrition_vals = np.zeros(n_nutrients)
        weight = 0
        cost = 0
        cooking = False
        water = False
        for i, a in ingredients:
            nutrition_vals += i.nutritional_values * 0.01 * a
            weight += a
            cost += i.price_per_gram * a
            if i.cooking:
                cooking = True
            if i.water:
                water = True

        meal = Meal(name=name, own_type=self.num_to_meal_type(own_type), ingredients=ingredients, cooking=cooking,
                    water=water, cost=cost, weight=weight, nutrition=nutrition_vals)

        self.meals.append(meal)

    def get_meal_names(self) -> list[str]:
        names = []
        for m in self.meals:
            names.append(m)

        return names

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
