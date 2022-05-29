from trip_backend import Trip
from food_backend import Meal, MealType, Ingredient
import numpy as np

breakfast = MealType('breakfast', 0)
lunch = MealType('lunch', 1)
dinner = MealType('dinner', 2)

rolled_oats = Ingredient(name='Rolled Oats', types=np.array([0]), cooking=True, water=True, price_per_unit=1.15,
                         unit_size=850, nutritional_values=np.array([370, 6.9, 1.2, 59, 1.3, 10, 13, 0]))

peanut_butter = Ingredient(name='Smooth Peanut Butter', types=np.array([0]), cooking=False, water=False,
                           price_per_unit=2.29, unit_size=340,
                           nutritional_values=np.array([641, 54, 8.7, 11.1, 7.2, 0, 24.5, 1]))

day_1_breakfast = Meal(name='Breakfast 1', own_type=breakfast)

day_1_breakfast.add_ingredient(rolled_oats, 40)
day_1_breakfast.add_ingredient(peanut_butter, 20)

print(day_1_breakfast.nutrition)
print(day_1_breakfast.weight)