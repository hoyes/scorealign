class Factory:
    def __init__(self, methods):
        self._factory_methods = methods
    def __call__(self, name):
        return self._factory_methods[name]();
    def keys(self):
        return self._factory_methods.keys()
