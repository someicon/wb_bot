

class Lst():
    def __init__(self, my_lst) -> None:
        self.my_lst = my_lst

    def print_lst(self):
        for i in self.my_lst:
            yield i


a = Lst([1, 2, 3, 4, 5])

result = a.print_lst()

print(*result)
