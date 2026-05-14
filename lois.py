def loi_ohm(resistance, tension):
    intensite = tension / resistance
    return intensite


def resistance_serie(*args):
    res_eq = 0
    for arg in args:
        res_eq += arg
    return res_eq


def resistance_parallele(*args):
    res_eq = 0
    for arg in args:
        res_eq += 1 / arg
    return 1 / res_eq
