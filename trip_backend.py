from dataclasses import dataclass, field
from food_backend import Meal


@dataclass
class Trip:
    """Implements the base class for any planning project.

    Args:
        name (str): Name of the trip.
        duration (int): Initial duration in days.
        meals_per_day (int): Standard number of planned meals per day."""

    name: str
    duration: int
    meals_per_day: int
    meals: list[list[Meal]] = field(default_factory=[[]])
    total_cost: float = 0
    total_weight: float = 0

    def add_days(self, n_days: int):
        """
        Adds days to the trip.

        :param n_days: How many days to add.
        """
        self.duration += n_days
        self.meals.append([] * n_days)

    def update_all_fields(self):
        """
        Updates all relevant fields.
        """
        self.total_cost = 0
        self.total_weight = 0
        for day in self.meals:
            for meal in day:
                self.total_cost += meal.cost
                self.total_weight += meal.weight
