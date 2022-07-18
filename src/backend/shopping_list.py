import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.app.connector import LocalDatabase
from src.backend.trip import Trip


@dataclass
class ShoppingList:
    database: LocalDatabase
    trip: Trip
    base_name: str
    shop_list: pd.DataFrame = pd.DataFrame(
        columns={'ingredient_name', 'ingredient_code', 'total_amount_needed', 'unit_size', 'needed_units',
                 'price_per_unit', 'total_price'})
    cost: float = 0
    persons: int = 1
    updated: bool = False
    shop_lists_dir: str = '..\\saves\\shopping_lists\\'

    def update_amounts(self):
        self.shop_list = pd.DataFrame(
            columns={'ingredient_name', 'ingredient_code', 'total_amount_needed', 'unit_size', 'needed_units',
                     'price_per_unit', 'total_price'})
        for i, day in enumerate(self.trip.meal_plan):
            for meal in day.values():
                if meal is None:
                    continue
                ins = meal.get_all_ingredients()
                ams = meal.get_all_ingredient_amounts()
                for j, ing in enumerate(ins):
                    code_list = list(self.shop_list.ingredient_code)
                    if ing.CODE in code_list:
                        self.shop_list.at[code_list.index(ing.CODE), 'total_amount_needed'] = \
                            self.shop_list.iloc[code_list.index(ing.CODE)]['total_amount_needed'] + \
                            self.persons * ams[j]

                    else:
                        new_row = {'ingredient_name': ing.name, 'ingredient_code': ing.CODE,
                                   'total_amount_needed': self.persons * ams[j], 'unit_size': ing.unit_size,
                                   'needed_units': 0, 'price_per_unit': ing.price_per_unit, 'total_price': 0}
                        self.shop_list.loc[len(self.shop_list.index)] = new_row

        self.updated = False

    def update_units(self):
        for i, size in enumerate(list(self.shop_list.unit_size)):
            units = int(np.ceil(self.shop_list.iloc[i]['total_amount_needed'] / size))
            self.shop_list.at[i, 'needed_units'] = units
            self.shop_list.at[i, 'total_price'] = units * self.shop_list.iloc[i]['price_per_unit']

        self.updated = True

    def generate_excel(self):
        if not os.path.isdir(self.shop_lists_dir):
            os.mkdir(self.shop_lists_dir)
        if self.updated:
            self.shop_list.to_excel(f'{self.shop_lists_dir}{self.base_name}.xlsx', sheet_name=self.base_name)
        else:
            raise Exception('Shopping list not updated!')
