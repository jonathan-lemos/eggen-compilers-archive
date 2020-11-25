from grammar import item, treenode


class SemAnalyzerException(Exception):
    pass


functab = {}
last_dec_main = False
last_func = None
return_hit = True
vartab = [{}]
param_flag = False


def functab_search(id):
    if id in functab:
        return functab[id]
    raise SemAnalyzerException()


def functab_push(type, id, params):
    global last_func
    global return_hit
    if id in functab:
        raise SemAnalyzerException()
    last_func = (type, params)
    return_hit = type == "void"
    functab[id] = last_func


def vartab_search(id):
    for vt in reversed(vartab):
        if id in vt:
            return vt[id]
    raise SemAnalyzerException()


def vartab_push(type, id, is_arr):
    if id in vartab[len(vartab) - 1]:
        raise SemAnalyzerException()
    vartab[len(vartab) - 1][id] = (type, is_arr)


def analyze_expr(expr):
    if len(expr.children) == 3:
        var = expr.children[0]
        analyze_var(var)
        var_is_arr_deref = len(var.children) == 4
        res = vartab_search(var.children[0].token)
        if res[1] != var_is_arr_deref:
            raise SemAnalyzerException()
        if (res[0], res[1] and not var_is_arr_deref) != analyze_expr(expr.children[2]):
            raise SemAnalyzerException()
        return res[0], res[1] and not var_is_arr_deref
    else:
        return analyze_simple_expr(expr.children[0])


def analyze_simple_expr(expr):
    if len(expr.children) == 3:
        r1 = analyze_additive_expr(expr.children[0])
        r2 = analyze_additive_expr(expr.children[2])
        if r1[0] == "void" or r1[1] or r1 != r2:
            raise SemAnalyzerException()
        return "int", False
    else:
        return analyze_additive_expr(expr.children[0])


def analyze_additive_expr(expr):
    if len(expr.children) == 3:
        r1 = analyze_additive_expr(expr.children[0])
        r2 = analyze_term(expr.children[2])
        if r1[0] == "void" or r1[1] or r1 != r2:
            raise SemAnalyzerException()
        return r1
    else:
        return analyze_term(expr.children[0])


def analyze_term(expr):
    if len(expr.children) == 3:
        r1 = analyze_term(expr.children[0])
        r2 = analyze_factor(expr.children[2])
        if r1[0] == "void" or r1[1] or r1 != r2:
            raise SemAnalyzerException()
        return r1
    else:
        return analyze_factor(expr.children[0])


def analyze_factor(expr):
    c = expr.children[0]

    if len(expr.children) == 3:
        return analyze_expr(expr.children[1])
    elif c.item.nt == "var":
        return analyze_var(c)
    elif c.item.nt == "call":
        return analyze_call(c)
    else:
        return "int", False


def analyze_var(v):
    res = vartab_search(v.children[0].token)
    res_is_arr_deref = len(v.children) == 4
    if res_is_arr_deref:
        if analyze_expr(v.children[2]) != ("int", False):
            raise SemAnalyzerException()
    return res[0], res[1] and not res_is_arr_deref


def compare_params(params, args):
    def compare_single(param, arg):
        if (param.children[0].children[0].token, len(param.children) == 4) != analyze_expr(arg):
            raise SemAnalyzerException()

    if params.item.prod == ("void",):
        if args.children[0].item.prod != ("#",):
            raise SemAnalyzerException()
        return
    pp = params.children[0]
    aa = args.children[0]

    def compare_params_rec(p, a):
        if len(p.children) != len(a.children):
            raise SemAnalyzerException()
        if len(p.children) == 1:
            compare_single(p.children[0], a.children[0])
        else:
            compare_single(p.children[2], a.children[2])
            compare_params_rec(p.children[0], a.children[0])

    compare_params_rec(pp, aa)


def analyze_call(c):
    f = functab_search(c.children[0].token)
    compare_params(f[1], c.children[2])
    return f[0], False


def analyze_vardec(vd):
    global last_dec_main

    vartab_push(vd.children[0].children[0].token, vd.children[1].token, len(vd.children) == 6)
    if vd.children[0].children[0].token == "void":
        raise SemAnalyzerException()
    if len(vartab) == 1:
        last_dec_main = False


def analyze_fundec(fd):
    global last_dec_main

    if not return_hit:
        raise SemAnalyzerException()
    dec = fd.children[0].children[0].token, fd.children[1].token, fd.children[3]
    functab_push(*dec)
    last_dec_main = dec[0] == "void" and dec[1] == "main" and dec[2].children[0].token == "void"


def analyze_params(pl):
    global param_flag
    param_flag = True
    vartab.append({})


def analyze_param(p):
    if p.children[0].children[0].token == "void":
        raise SemAnalyzerException("cannot have void parameters")
    vartab_push(p.children[0].children[0].token, p.children[1].token, len(p.children) == 4)


def analyze_compound_stmt(cps):
    global param_flag
    global vartab
    if not param_flag:
        vartab.append({})
    param_flag = False
    for child in cps:
        analyze(child)
    vartab = vartab[:-1]


def analyze_control_stmt(cs):
    if analyze_expr(cs.children[2]) != ("int", False):
        raise SemAnalyzerException()


def analyze_return_stmt(rs):
    global return_hit
    if len(rs.children) == 2:
        if last_func[0] != "void":
            raise SemAnalyzerException()
    else:
        if last_func[0] == "void":
            raise SemAnalyzerException()
        res = analyze_expr(rs.children[1])
        if res[1]:
            raise SemAnalyzerException()
        if last_func[0] != res[0]:
            raise SemAnalyzerException()
    return_hit = True


analyzers = {
    "expression": (analyze_expr, False),
    "simple-expression": (analyze_simple_expr, False),
    "additive-expression": (analyze_additive_expr, False),
    "term": (analyze_term, False),
    "factor": (analyze_factor, False),
    "var": (analyze_var, False),
    "call": (analyze_call, False),
    "param": (analyze_param, False),
    "var-declaration": (analyze_vardec, False),
    "fun-declaration": (analyze_fundec, True),
    "params": (analyze_params, True),
    "selection-stmt": (analyze_control_stmt, True),
    "iteration-stmt": (analyze_control_stmt, True),
    "return-stmt": (analyze_return_stmt, False),
    "compound-stmt": (analyze_compound_stmt, False)
}


def analyze(root):
    if not root.item.is_reduce():
        return

    if root.item.nt in analyzers:
        func, cont = analyzers[root.item.nt]
        func(root)
        if not cont:
            return

    for child in root:
        analyze(child)


def analyze_prgm(prgm):
    for child in prgm:
        analyze(child)
    if not last_dec_main:
        raise SemAnalyzerException()
    if not return_hit:
        raise SemAnalyzerException()
