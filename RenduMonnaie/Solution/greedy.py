def greedy(amount: int, coins: list) -> int:
    result = 0
    for c in coins:
        result += amount//c
        amount %= c
    return result

    # SOL VERSION
    # coins = coins.copy()
    # coins.sort()
    # return _greedy(amount, coins, list())
    

def _greedy(amount: int, coins: list, result: list) -> list:
    if len(coins):
        coin = coins.pop()
        x = amount // coin
        result += [coin for _ in range(x)]
        amount %= coin
        return _greedy(amount, coins, result)
    return result

if __name__ == '__main__':
    coins = [30, 24, 12, 6, 3, 1]
    assert greedy(1, coins) == 1 # [1]
    assert greedy(60, coins) == 2 # [30, 30]
    assert greedy(48, coins) == 3 # [30, 12, 6]
    assert greedy(49, coins) == 4 # [30, 12, 6, 1]