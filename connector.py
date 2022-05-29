import numpy as np
import numpy.typing as npt
from food_backend import Ingredient, MealType, Meal, LocalDatabaseComponent
from trip_backend import Trip
import pandas as pd

from food_backend import n_nutrients

from typing import Union


class LocalDatabase:
    def __init__(self):
        self.ingredients = []
        self.meal_types = [MealType('Breakfast', 0), MealType('Lunch', 1), MealType('Dinner', 2), MealType('Snack', 3)]
        self.meals = []
        self.trips = []
        self.sep = ';'
        self.i_names = []
        self.string_true = ['true']

    def save(self, f_name: str):
        self.save_ingredients_to_file(f_name)
        self.save_meals_to_file(f_name)

    def load(self, files: list[str]):
        self.load_ingredients_from_file(files[0])
        if len(files) > 1:
            self.load_meals_from_file(files[1])

    def load_from_basefile(self, f_name: str):
        with open(f_name, 'r') as file:
            file_paths = file.read().splitlines()

        self.load(file_paths)

    def has_ingredients(self) -> bool:
        return bool(self.ingredients)

    def has_meals(self) -> bool:
        return bool(self.meals)

    def remove_item(self, item: LocalDatabaseComponent) -> bool:
        if type(item) is Meal:
            return self.remove_meal_by_name(item.name)
        elif type(item) is Ingredient:
            return self.remove_ingredient_by_name(item.name)

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
                    f'{i.name}{self.sep} {i.nutrition[0]}{self.sep} {i.nutrition[1]}{self.sep} '
                    f'{i.nutrition[2]}{self.sep} {i.nutrition[3]}{self.sep} '
                    f'{i.nutrition[4]}{self.sep} {i.nutrition[5]}{self.sep} '
                    f'{i.nutrition[6]}{self.sep} {i.nutrition[7]}{self.sep} '
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
            item = Ingredient(name=name, nutrition=np.array(data.iloc[index, 1:9]),
                              types=types, cooking=cooking, water=water,
                              price_per_unit=float(data.price_per_unit[index]), unit_size=float(data.unit_size[index]),
                              price_per_gram=float(data.price_per_gram[index]))
            self.ingredients.append(item)

    def save_meals_to_file(self, f_name: str):
        with open(f'{f_name}_meals.csv', 'w') as file:
            file.write(f'name{self.sep} energy{self.sep} fat{self.sep} sat_fat{self.sep} carbs{self.sep}'
                       f'sugar{self.sep} fiber{self.sep} protein{self.sep} salt{self.sep} own_types{self.sep} '
                       f'ingredients{self.sep} amount{self.sep} cooking{self.sep} water{self.sep} cost{self.sep} '
                       f'weight\n'.replace(' ', ''))
            for i in self.meals:
                types = ''
                for j in i.own_types:
                    types += f'{j.code}--'

                file.write(
                    f'{i.name}{self.sep} {i.nutrition[0]}{self.sep} {i.nutrition[1]}{self.sep} '
                    f'{i.nutrition[2]}{self.sep} {i.nutrition[3]}{self.sep} {i.nutrition[4]}{self.sep} '
                    f'{i.nutrition[5]}{self.sep} {i.nutrition[6]}{self.sep} {i.nutrition[7]}{self.sep} '
                    f'{types}{self.sep} {i.get_all_ingredient_names()}{self.sep} '
                    f'{i.get_all_ingredient_amounts()}{self.sep} {i.cooking}{self.sep} {i.water}{self.sep} '
                    f'{i.cost}{self.sep} {i.weight}\n')

    def load_meals_from_file(self, f_name: str):
        data = pd.read_csv(f_name, sep=self.sep)
        for i, in_str in enumerate(data.ingredients):
            types = [self.num_to_meal_type(int(i)) for i in data.own_types[i].split('--')[:-1]]
            if data.water[i].lower().strip() in self.string_true:
                water = True
            else:
                water = False
            if data.cooking[i].lower().strip() in self.string_true:
                cooking = True
            else:
                cooking = False
            ingredients = self.ingredient_and_amount_str_to_list(in_str=in_str, am_str=data.amount[i])
            meal = Meal(name=data.name[i], nutrition=np.array(data.iloc[i, 1:9]), own_types=types,
                        ingredients=ingredients, cooking=cooking, water=water, cost=float(data.cost[i]),
                        weight=float(data.weight[i]))

            self.meals.append(meal)

    def ingredient_and_amount_str_to_list(self, in_str: str, am_str: str) -> list[list[Union[Ingredient, float]]]:
        in_strings = in_str.replace('[', '').replace(']', '').replace("'", "").split(',')
        am_strings = am_str.replace('[', '').replace(']', '').replace("'", "").split(',')
        in_strings = [i.strip() for i in in_strings]
        am_strings = [i.strip() for i in am_strings]

        ret_list = []

        for i, am in enumerate(am_strings):
            ingredient = self.get_ingredient_by_name(in_strings[i])
            amount = float(am)
            ret_list.append([ingredient, amount])

        return ret_list

    def get_ingredient_by_name(self, name: str) -> Ingredient:
        try:
            ind = self.get_ingredient_names().index(name)
            return self.ingredients[ind]
        except ValueError:
            pass

    def remove_ingredient_by_name(self, name: str) -> bool:
        if name in self.get_ingredient_names():
            self.ingredients.pop(self.get_ingredient_names().index(name))

        if name not in self.get_ingredient_names():
            return True
        else:
            return False

    def replace_meal(self, old_meal: Meal, new_meal: Meal) -> bool:
        if old_meal in self.meals:
            ind = self.meals.index(old_meal)
            self.meals[ind] = new_meal
            return True
        else:
            return False

    def search_by_name(self, mode: str, search_text: str) -> list[str]:
        if mode == 'ingredients':
            names = self.get_ingredient_names()
        elif mode == 'meals':
            names = self.get_meal_names()
        elif mode == 'trips':
            names = []
        else:
            return []
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

    def num_to_meal_type(self, num: Union[int, list[int]]) -> Union[MealType, list[MealType]]:
        if type(num) is int:
            return self.meal_types[num]
        elif type(num) is list[int]:
            return [self.meal_types[i] for i in num]

    def add_meal(self, name: str, own_type: Union[int, MealType, list[int], list[MealType]],
                 ingredients: list[list[Ingredient, float]] = None):
        nutrition_vals = np.zeros(n_nutrients)
        weight = 0
        cost = 0
        cooking = False
        water = False

        if type(own_type) is Union[int, list[int]]:
            own_type = self.num_to_meal_type(own_type)

        if ingredients is not None:
            for i, a in ingredients:
                nutrition_vals += i.nutrition * 0.01 * a
                weight += a
                cost += i.price_per_gram * a
                if i.cooking:
                    cooking = True
                if i.water:
                    water = True

            meal = Meal(name=name, own_types=own_type, ingredients=ingredients, cooking=cooking,
                        water=water, cost=cost, weight=weight, nutrition=nutrition_vals)

        else:
            meal = Meal(name=name, own_types=own_type)

        self.meals.append(meal)

    def get_meal_names(self) -> list[str]:
        names = []
        for m in self.meals:
            names.append(m.name)

        return names

    def add_trip(self, item: Trip):
        self.trips.append(item)

    def add_ingredient(self, name: str, nutrients: npt.NDArray, types: npt.NDArray, water: bool, cooking: bool,
                       price_per_unit: float, unit_size: float):
        ingredient = Ingredient(name=name, nutrition=nutrients, water=water, cooking=cooking,
                                price_per_unit=price_per_unit, unit_size=unit_size, types=types)
        self.ingredients.append(ingredient)

    def get_ingredient_names(self):
        names = []
        for i in self.ingredients:
            names.append(i.name)

        self.i_names = names

        return self.i_names

    def get_meal_type_names(self) -> list[str]:
        names = []
        for m in self.meal_types:
            names.append(m.name)

        return names

    def remove_meal_by_name(self, name: str):
        if name in self.get_meal_names():
            ind = self.get_meal_names().index(name)
            self.meals.pop(ind)

        if name not in self.get_meal_names():
            return True
        else:
            return False

    def get_meal_by_name(self, name: str):
        if name in self.get_meal_names():
            return self.meals[self.get_meal_names().index(name)]
