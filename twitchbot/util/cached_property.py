from collections.abc import Callable


class CachedProperty:
    def __init__(self, getter: Callable):
        self.getter = getter
        self.value = None

    def __get__(self, instance, owner):
        if self.value is None and instance is not None:
            self.value = self.getter(instance)
        return self.value


class CachedClassProperty:
    def __init__(self, getter: Callable):
        self.getter = getter
        self.value = None

    def __get__(self, instance, owner):
        if self.value is None and owner is not None:
            self.value = self.getter(owner)
        return self.value


class CachedStaticProperty:
    def __init__(self, getter: Callable):
        self.getter = getter
        self.value = None

    def __get__(self, instance, owner):
        if self.value is None:
            self.value = self.getter()
        return self.value
