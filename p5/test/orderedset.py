class orderedset:
    def __init__(self, iterable=None):
        if not iterable:
            iterable = []
        self.dict = {}
        self.list = []
        for item in iterable:
            self.add(item)

    def __contains__(self, item):
        return item in self.dict

    def __iter__(self):
        i = 0
        while i < len(self.list):
            yield self.list[i]
            i += 1

    def get(self, item):
        return self.list[self.dict[item]]

    def __getitem__(self, index):
        return self.list[index]

    def add(self, item):
        if item in self.dict:
            return
        self.list.append(item)
        self.dict[item] = len(self.list) - 1

    def __str__(self):
        return "{" + ", ".join(str(x) for x in self.list) + "}"
