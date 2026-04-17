def solve_01_knapsack(items, max_W, max_V):
    n = len(items)
    dp = [[0] * (max_V + 1) for _ in range(max_W + 1)]
    chosen = [[[] for _ in range(max_V + 1)] for _ in range(max_W + 1)]
    dp_history = [[dp[w][max_V] for w in range(max_W + 1)]]

    for i in range(n):
        wi = items[i]["weight"]
        vi = items[i]["volume"]
        val = items[i]["value"]
        for w in range(max_W, wi - 1, -1):
            for v in range(max_V, vi - 1, -1):
                candidate = dp[w - wi][v - vi] + val
                if candidate > dp[w][v]:
                    dp[w][v] = candidate
                    chosen[w][v] = chosen[w - wi][v - vi] + [i]
        dp_history.append([dp[w][max_V] for w in range(max_W + 1)])

    return dp[max_W][max_V], chosen[max_W][max_V], dp_history


def solve_greedy(items, max_W, max_V):
    ranked = sorted(
        enumerate(items),
        key=lambda x: x[1]["value"] / (x[1]["weight"] + x[1]["volume"]),
        reverse=True,
    )
    selected = []
    total_weight = 0
    total_volume = 0
    total_value = 0
    for idx, item in ranked:
        if (total_weight + item["weight"] <= max_W and
                total_volume + item["volume"] <= max_V):
            selected.append(idx)
            total_weight += item["weight"]
            total_volume += item["volume"]
            total_value += item["value"]
    return total_value, selected


def evaluate(user_selected, dp_selected, greedy_selected, items, dp_value, greedy_value):
    user_value = sum(items[i]["value"] for i in user_selected)
    user_weight = sum(items[i]["weight"] for i in user_selected)
    user_volume = sum(items[i]["volume"] for i in user_selected)
    efficiency = round((user_value / dp_value * 100), 1) if dp_value > 0 else 0.0
    dp_gap = dp_value - user_value
    greedy_gap = dp_value - greedy_value
    if dp_gap == 0:
        status = "OPTIMAL"
    elif efficiency >= 90:
        status = "NEAR OPTIMAL"
    elif efficiency >= 70:
        status = "SUBOPTIMAL"
    else:
        status = "POOR"
    return {
        "user_value":   user_value,
        "user_weight":  user_weight,
        "user_volume":  user_volume,
        "dp_value":     dp_value,
        "greedy_value": greedy_value,
        "efficiency":   efficiency,
        "dp_gap":       dp_gap,
        "greedy_gap":   greedy_gap,
        "status":       status,
    }