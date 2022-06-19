class NoIngredientPassedError(Exception):
    def __init__(self):
        msg = 'No ingredient was passed!'
        super().__init__(msg)