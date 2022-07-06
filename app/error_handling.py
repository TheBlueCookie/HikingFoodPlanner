class NoIngredientPassedError(Exception):
    def __init__(self):
        msg = 'No ingredient was passed!'
        super().__init__(msg)


class ItemUsedElsewhereError(Exception):
    def __init__(self):
        super().__init__('Item is used somewhere!')
