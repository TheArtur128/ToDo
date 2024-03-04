class Visualizable:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self})"
