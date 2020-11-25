from SemAnalyzer import functab

_ctr = -1


def ctr():
    global _ctr
    _ctr += 1
    return _ctr


_tmp = -1


def tmp():
    global _tmp
    _tmp += 1
    return "_t" + str(_tmp)


def params_len(p):
    if p.item.prod == ("void",):
        return 0

    def plist_len(pl):
        if len(pl.children) == 3:
            return 1 + plist_len(pl.children[0])
        else:
            return 1

    return plist_len(p.children[0])


def gen_fundec(fd):
    return [(ctr(), "func", fd.children[1].token, fd.children[0].children[0].token, params_len(fd.children[3]))] + \
           gen_params(fd.children[3]) + \
           [y for x in fd.children[5] for y in default_gen(x)] + \
           [(ctr(), "end", "func", fd.children[1].token, "")]


def gen_params(p):
    if p.item.prod == ("void",):
        return []

    def plist_rec(pl):
        if len(pl.children) == 3:
            q = pl.children[2]
            return plist_rec(pl.children[0]) + [(ctr(), "param", "", "", q.children[1].token)]
        else:
            q = pl.children[0]
            return [(ctr(), "param", "", "", q.children[1].token)]

    return plist_rec(p.children[0])


def gen_comp_stmt(c):
    #return [(ctr(), "block", "", "", "")] + \
    #       [y for x in c for y in default_gen(x)] + \
    #       [(ctr(), "end", "block", "", "")]
    return [y for x in c for y in default_gen(x)]


def gen_vardec(vd):
    if len(vd.children) == 3:
        return [(ctr(), "alloc", "4", "", vd.children[1].token)]
    else:
        size = int(vd.children[3].token) * 4
        return [(ctr(), "alloc", str(size), "", vd.children[1].token)]


def gen_selectionstmt(ss):
    cond = gen_condition(ss.children[2])
    e2 = default_gen(ss.children[4])
    if len(ss.children) == 7:
        e2 += [(ctr(), "br", "", "", "")]
        cond[-1] = tuple(list(cond[-1])[:-1] + [str(_ctr + 1)])
        e3 = default_gen(ss.children[6])
        txx = list(e2[-1])
        txx[-1] = str(_ctr + 1)
        e2[-1] = tuple(txx)
        return cond + e2 + e3
    else:
        cond[-1] = tuple(list(cond[-1])[:-1] + [str(_ctr + 1)])
        return cond + e2


def gen_iterationstmt(ss):
    ctrinit = _ctr + 1
    cond = gen_condition(ss.children[2])
    e2 = default_gen(ss.children[4])
    x = [(ctr(), "br", "", "", str(ctrinit))]
    cond[-1] = tuple(list(cond[-1])[:-1] + [str(_ctr + 1)])
    return cond + e2 + x


def gen_returnstmt(rs):
    if len(rs.children) == 3:
        e, n = gen_expr(rs.children[1])
        return e + [(ctr(), "return", "", "", n)]
    else:
        return [(ctr(), "return", "", "", "")]


def gen_condition(ex):
    if len(ex.children) == 3:
        v, nv = gen_var(ex.children[0])
        e, ne = gen_expr(ex.children[2])
        res = [(ctr(), "assgn", ne, "", nv)]
        cmp = [(ctr(), "compr", res[-1][-1], "0", tmp())]
        br = [(ctr(), "breq", cmp[-1][-1], "", "XXX")]
        return v + e + res + cmp + br
    else:
        return gen_condition_simple_expr(ex.children[0])


def gen_condition_simple_expr(se):
    if len(se.children) == 3:
        e1, n1 = gen_additive_expr(se.children[0])
        e2, n2 = gen_additive_expr(se.children[2])
        br = {
            "==": "brne",
            "!=": "breq",
            ">=": "brlt",
            "<=": "brgt",
            ">": "brle",
            "<": "brge"
        }[se.children[1].token]
        cmp = [(ctr(), "compr", n1, n2, tmp())]
        brr = [(ctr(), br, cmp[-1][-1], "", "XXX")]
        return e1 + e2 + cmp + brr
    else:
        a, n = gen_additive_expr(se.children[0])
        cmp = [(ctr(), "compr", n, "0", tmp())]
        br = [(ctr(), "breq", cmp[-1][-1], "", "XXX")]
        return a + cmp + br


def gen_expr(ex):
    if len(ex.children) == 3:
        v, vn = gen_var(ex.children[0])
        e, en = gen_expr(ex.children[2])
        return v + e + [(ctr(), "assgn", en, "", vn)], vn
    else:
        return gen_simple_expr(ex.children[0])


def gen_var(v):
    if len(v.children) == 1:
        return [], v.children[0].token
    else:
        e, n = gen_expr(v.children[2])
        x = [(ctr(), "mul", n, "4", tmp())]
        t = [(ctr(), "disp", v.children[0].token, x[-1][-1], tmp())]
        return e + x + t, t[-1][-1]
        # return e + t, t[-1][-1]


def gen_simple_expr(se):
    if len(se.children) == 3:
        e1, n1 = gen_additive_expr(se.children[0])
        e2, n2 = gen_additive_expr(se.children[2])
        br = {
            "==": "brne",
            "!=": "breq",
            ">=": "brlt",
            "<=": "brgt",
            ">": "brle",
            "<": "brge"
        }[se.children[1].token]
        agn1 = [(ctr(), "assgn", "0", "", tmp())]
        comp = [(ctr(), "compr", n1, n2, tmp())]
        brr = [(ctr(), br, comp[-1][-1], "", _ctr + 2)]
        agn2 = [(ctr(), "assgn", "1", "", agn1[-1][-1])]
        return e1 + e2 + agn1 + comp + brr + agn2, agn1[-1][-1]
    else:
        return gen_additive_expr(se.children[0])


def gen_additive_expr(ae):
    if len(ae.children) == 3:
        e1, n1 = gen_additive_expr(ae.children[0])
        op = {
            "+": "add",
            "-": "sub",
        }[ae.children[1].token]
        e2, n2 = gen_term(ae.children[2])
        x = [(ctr(), op, n1, n2, tmp())]
        return e1 + e2 + x, x[-1][-1]
    else:
        return gen_term(ae.children[0])


def gen_term(t):
    if len(t.children) == 3:
        e1, n1 = gen_term(t.children[0])
        op = {
            "*": "mul",
            "/": "div",
        }[t.children[1].token]
        e2, n2 = gen_factor(t.children[2])
        x = [(ctr(), op, n1, n2, tmp())]
        return e1 + e2 + x, x[-1][-1]
    else:
        return gen_factor(t.children[0])


def gen_factor(f):
    if len(f.children) == 3:
        return gen_expr(f.children[1])
    elif f.children[0].item.prod == ("NUM",):
        return [], f.children[0].token
    elif f.children[0].item.nt == "var":
        return gen_var(f.children[0])
    else:
        return gen_call(f.children[0])


def gen_args(a):
    if a.item.prod == ("#",):
        return [], 0

    counter = 0

    def gen_args_rec(alist):
        nonlocal counter
        counter += 1

        if len(alist.children) == 3:
            x, y = gen_args_rec(alist.children[0])
            b, c = gen_expr(alist.children[2])
            return x + b, y + [c]
        else:
            b, c = gen_expr(alist.children[0])
            return b, [c]

    res = gen_args_rec(a.children[0])
    q = res[0] + [(ctr(), "arg", "", "", x) for x in res[1]], counter
    return q


def gen_call(c):
    a, ct = gen_args(c.children[2])
    b = [(ctr(), "call", c.children[0].token, str(ct), tmp() if functab[c.children[0].token][0] != "void" else "")]
    return a + b, b[-1][-1]


def gen_expr_discard(r):
    return gen_expr(r)[0]


generators = {
    "var-declaration": gen_vardec,
    "fun-declaration": gen_fundec,
    "params": gen_params,
    "selection-stmt": gen_selectionstmt,
    "expression": gen_expr_discard,
    "compound-stmt": gen_comp_stmt,
    "iteration-stmt": gen_iterationstmt,
    "return-stmt": gen_returnstmt
}


def default_gen(root):
    if not root.item.is_reduce():
        return []
    if root.item.nt in generators:
        return generators[root.item.nt](root)
    else:
        return [y for x in root for y in default_gen(x)]
