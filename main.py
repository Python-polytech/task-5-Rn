from functools import lru_cache

class CoordDescriptor:

    def __init__(self, name):
        self.name = name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(
                f"Координата {self.name} должна быть числом (int или float), "
                f"получено {type(value).__name__}"
            )
        instance.__dict__[self.name] = value


@lru_cache(maxsize=None)
def make_point_class(n, name=None):

    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n должно быть целым числом >= 1")

    class_name = name or f"Point{n}"

    attrs = {f"x{i}": CoordDescriptor(f"x{i}") for i in range(n)}

    def __init__(self, *args):
        if len(args) != n:
            raise TypeError(
                f"{class_name} принимает ровно {n} позиционных аргументов, "
                f"получено {len(args)}"
            )
        for i, value in enumerate(args):
            setattr(self, f"x{i}", value)

    def to_tuple(self):
        return tuple(getattr(self, f"x{i}") for i in range(n))

    def __repr__(self):
        coords = ", ".join(repr(getattr(self, f"x{i}")) for i in range(n))
        return f"{class_name}({coords})"

    namespace = {
        **attrs,
        "__init__": __init__,
        "to_tuple": to_tuple,
        "__repr__": __repr__,
    }

    cls = type(class_name, (), namespace)
    return cls

if __name__ == "__main__":
    Point2 = make_point_class(2)
    Point3 = make_point_class(3)

    p = Point2(1, 2.5)
    print(p)  # Point2(1, 2.5)
    print(p.to_tuple())  # (1, 2.5)
    print(p.x0, p.x1)  # 1 2.5

    q = Point3(1, 2, 3)
    print(q.to_tuple())  # (1, 2, 3)

    # Проверка кэширования — один и тот же класс
    assert make_point_class(2) is make_point_class(2)
    assert make_point_class(2) is not make_point_class(3)

    # Ошибка типа
    try:
        Point2("a", 1)
    except TypeError as e:
        print("TypeError:", e)

    # Ошибка количества аргументов
    try:
        Point3(1, 2)
    except TypeError as e:
        print("TypeError:", e)