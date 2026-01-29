_optimals={}

def optimal(amount: int, coins: list) -> int:
    if amount in coins:
        return 1
    if amount in _optimals:
        return _optimals[amount]
    opt = 1 + min(optimal(amount-coins[i], coins[i:]) for i in range(len(coins)) if amount-coins[i]>0)
    _optimals[amount] = opt
    return opt
    
    # SOL VERSION
    # coins = coins.copy()
    # results = _optimal(amount, coins)
    # results.sort(key=lambda r: len(r))
    # result = results[0]
    # _optimals[amount] = result
    # return result

def _optimal(amount: int, coins: list) -> list:
    results = list()
    for i in range(len(coins)):
        c = coins[i]
        if amount in _optimals:
            return [_optimals[amount]]
        if amount > c:
            for o in _optimal(amount-c, coins[i:]):
                results.append([c] + o)
        if amount == c:
            return [[c]]
    return results


if __name__ == '__main__':
    coins = [30, 24, 12, 6, 3, 1]
    assert optimal(1, coins) == 1 # [1]
    assert optimal(2, coins) == 2 # [1, 1]
    assert optimal(48, coins) == 2 # [24, 24]
    assert optimal(49, coins) == 3 # [24, 24, 1]
    assert optimal(60, coins) == 2 # [30, 30]