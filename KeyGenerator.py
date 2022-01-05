class KeyGenerator:
    def __init__(self):
        self.key = 0      
    def __next__(self):
        return_value = self.key
        self.key += 1
        return return_value
    def __iter__(self):
        return self
    def __restart__(self):
        self.__init__()


