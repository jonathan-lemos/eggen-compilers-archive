import re
from orderedset import orderedset


class item:
    def __init__(self, nt, prod, dotpos=0):
        self.nt, self.prod, self.dotpos = nt, prod, dotpos
        self.hash = hash((self.nt, self.prod, self.dotpos))

    def __eq__(self, other):
        return self.nt == other.nt and self.prod == other.prod and self.dotpos == other.dotpos

    def __hash__(self):
        return self.hash

    def advanced(self):
        assert self.dotpos < len(self.prod)
        return item(self.nt, self.prod, self.dotpos + 1)

    def retarded(self):
        assert self.dotpos > 0
        return item(self.nt, self.prod, self.dotpos - 1)

    def current(self):
        return self.prod[self.dotpos]

    def previous(self):
        assert self.dotpos > 0
        return self.prod[self.dotpos - 1]

    def is_reduce(self):
        return self.dotpos >= len(self.prod)

    def __str__(self):
        return self.nt + " -> " + " ".join(list(self.prod[:self.dotpos]) + ["."] + list(self.prod)[self.dotpos:])


class earleyitem:
    def __init__(self, item, origin, index):
        self.item, self.origin, self.index = item, origin, index
        self.hash = hash((self.item, self.origin))

    def __eq__(self, other):
        return self.item == other.item and self.origin == other.origin

    def __hash__(self):
        return self.hash

    def __str__(self):
        return "(" + str(self.item) + ", " + str(self.origin) + ". " + str(self.index) + ")"


class earleyset:
    def __init__(self):
        self.items, self.prev = orderedset(), {}

    def add(self, item, origin, index, prev):
        newitem = earleyitem(item, origin, index)
        if newitem in self.items:
            self.prev[newitem].add(prev)
        else:
            self.prev[newitem] = orderedset([prev])
            self.items.add(newitem)

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return str(self.items)


class treenode:
    def __init__(self, item, token, children=None):
        if not children:
            children = []
        self.item, self.token, self.children = item, token, children

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)

    def __str__(self):
        return str(self.item)


class grammar:
    def __init__(self, rules):
        self.start = ""
        self.rules = {}
        self.nonterms = set()
        all = set()
        for rule in rules:
            nt, rhs = (x.strip() for x in rule.split("->"))
            if self.start == "":
                self.start = nt
            self.nonterms.add(nt)
            for prod in (x.strip() for x in rhs.split("|")):
                if nt not in self.rules:
                    self.rules[nt] = set()
                self.rules[nt].add(tuple(x.strip() for x in prod.split()))
                all |= {x.strip() for x in prod.split()}
        self.terms = all - self.nonterms - {"#"}

    def __iter__(self):
        return iter(self.rules.items())

    def __getitem__(self, nt):
        return self.rules[nt]

    def lex(self, input, patterns):
        ret = []
        for string in input.split():
            while string != "":
                longest = ("", "")
                for term in self.terms:
                    if string.startswith(term):
                        longest = longest if len(longest[1]) >= len(term) else (term, term)
                for token, pattern in patterns:
                    mat = re.match(pattern, string)
                    if mat:
                        longest = longest if len(longest[1]) >= mat.end() else (token, string[:mat.end()])
                if longest == ("", ""):
                    longest = ("", string[0])
                string = string[len(longest[1]):].strip()
                ret.append(longest)
        return ret

    def parse(self, tokens):
        newstart = item(self.start + "'", (self.start,))
        table = [earleyset() for _ in range(len(tokens) + 1)]
        table[0].add(newstart, 0, 0, None)
        for i in range(len(table)):
            for eitem in table[i]:
                it, origin = eitem.item, eitem.origin
                if not it.is_reduce():
                    if it.prod == ("#",):
                        table[i].add(it.advanced(), i, i, eitem)
                    elif it.current() in self.nonterms:
                        for prod in self[it.current()]:
                            table[i].add(item(it.current(), prod), i, i, eitem)
                    else:
                        if i < len(tokens) and it.current() == tokens[i][0]:
                            table[i + 1].add(it.advanced(), origin, i + 1, eitem)
                else:
                    for eitem2 in table[origin]:
                        it2, origin2 = eitem2.item, eitem2.origin
                        if not it2.is_reduce() and it2.current() == it.nt:
                            table[i].add(it2.advanced(), origin2, i, eitem)
        tokenstomatch = list(tokens)
        stack = [earleyitem(newstart.advanced(), 0, len(table) - 1)]
        if stack[0] not in table[len(table) - 1]:
            return None
        path = []
        while len(stack) > 0:
            current = stack.pop()
            if current.index == -1:
                current = earleyitem(current.item, current.origin, path[len(path) - 1].index)
            path.append(current)
            if current in table[len(tokenstomatch)].prev and None in table[len(tokenstomatch)].prev[current]:
                continue
            if current.item.dotpos == 0:
                tomatch = stack.pop()
                if tomatch.item.dotpos > 0:
                    stack.append(table[current.index].prev[current].get(tomatch))
            else:
                tomatchtoken = current.item.previous()
                target = earleyitem(current.item.retarded(), current.origin, -1)
                if tomatchtoken in self.terms and tomatchtoken == tokenstomatch[
                    len(tokenstomatch) - 1][0] or tomatchtoken == "#":
                    if tomatchtoken != "#":
                        tokenstomatch.pop()
                    stack.append(table[current.index].prev[current].get(target))
                else:
                    prospect = None
                    for x in table[current.index].prev[current]:
                        if x.item.nt == tomatchtoken:
                            prospect = x
                            break
                    stack.append(target)
                    stack.append(prospect)
        enum = iter(path)
        eitem = next(enum, None)

        def completerule():
            nonlocal eitem
            if not eitem:
                return None
            elif eitem.item.is_reduce():
                children = []
                old = eitem.item
                for token in reversed(eitem.item.prod):
                    eitem = next(enum, None)
                    children.append(completerule())
                return treenode(old, old.nt, list(reversed([x for x in children if x is not None])))
            elif eitem.item.current() in self.nonterms:
                eitem = next(enum, None)
                if not eitem:
                    return None
                return completerule()
            elif eitem.item.current() == "#":
                return treenode(eitem.item, "#")
            else:
                return treenode(eitem.item, tokens[eitem.index][1])

        return completerule().children[0]
