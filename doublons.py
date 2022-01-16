def doublons(lst: list) -> bool:
    p = []
    for e in lst:
        if e in p:
            return True
        p.append(e)
    return False
