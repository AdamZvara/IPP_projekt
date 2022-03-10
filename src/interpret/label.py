class Label:
    def __init__(self, name : str, pos : int) -> None:
        self.__name = name
        self.__pos = pos

    @property
    def name(self):
        return self.__name

    @property
    def pos(self):
        return self.__pos