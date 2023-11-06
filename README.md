
# HikingFoodPlanner

A Python application for precise customizable meal planning on backpacking trips.



## Author

[@eliasankerhold](https://www.github.com/eliasankerhold)


## License

[GPL-3.0-only](https://choosealicense.com/licenses/gpl-3.0/)


## Run Locally

Clone the project

```bash
  git clone https://github.com/TheBlueCookie/HikingFoodPlanner.git
```

Go to the project directory

```bash
  cd HikingFoodPlanner
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the application

```bash
  python main.py
```


## Quick Usage

1. Add ingredients by clicking **Add** next to the search bar in the **Ingredients** tab.
2. Switch to the **Meals** tab and create a new meal analog to 1. Select one or several types of meals (breakfast, lunch, ...)
3. Add ingredients to the meal by selecting it in the list and clicking **Edit Meal**:

    - Select an ingredient from the list, enter the amount to be added to the meal and click **Add to Meal**.
    - Ingredients which are already part of the meal (marked light green) can be removed from the meal or their amount can be changed.
4. Switch to the **Trip** tab and select day 1 or add more days.
5. Assign a meal as breakfast, lunch, dinner or snack by clicking **Add Meal** next to the respective meal type. Make sure a day is selected (blue background).
6. To get a trip overview, click **Trip Summary** in the **Trip** tab. Select a day to go back to day view.

Trips can be loaded and saved in the **Trip** menu. Ingredients and meals are saved as databases in the **Database** menu. The program tries to automatically load the database last used.
