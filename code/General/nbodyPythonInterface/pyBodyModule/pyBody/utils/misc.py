def load_list(n, start, ntrue):
    out = list()
    for i in range(n):
        if start <= i < start+ntrue:
            out.append(True)
        else:
            out.append(False)
    return out