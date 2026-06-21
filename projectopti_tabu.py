import random
import sys


NEG = -10**18
MAX_ITERATIONS = 500
MAX_NEIGHBORS = 4000
ITEM_LIMIT = 60
TABU_TENURE = 12
MAX_STAGNATION = 100
RANDOM_SEED = 42


def choose_subset(cands, weight, value, low, high):
    """Find the highest-value subset whose total weight is in [low, high]."""
    dp = [NEG] * (high + 1)
    picked = [None] * (high + 1)
    dp[0] = 0
    picked[0] = []

    for oid in cands:
        wi = weight[oid]
        if wi > high:
            continue

        for cap in range(high, wi - 1, -1):
            if dp[cap - wi] == NEG:
                continue

            new_value = dp[cap - wi] + value[oid]
            if new_value > dp[cap]:
                dp[cap] = new_value
                picked[cap] = picked[cap - wi] + [oid]

    feasible_caps = [cap for cap in range(low, high + 1) if dp[cap] != NEG]
    if not feasible_caps:
        return []

    best_cap = max(feasible_caps, key=lambda cap: (dp[cap], -cap))
    return picked[best_cap]


def make_initial_solution(n, vehicles, weight, value, low, high):
    """Build a feasible starting solution with greedy ordering and local DP."""
    order_ids = list(range(1, n + 1))
    order_ids.sort(key=lambda i: (value[i] / weight[i], value[i]), reverse=True)
    vehicle_order = sorted(
        vehicles,
        key=lambda b: (high[b] - low[b], high[b], -low[b]),
    )

    assigned = [0] * (n + 1)
    load = [0] * (len(vehicles) + 1)

    for b in vehicle_order:
        cands = [i for i in order_ids if assigned[i] == 0 and weight[i] <= high[b]]
        chosen = choose_subset(cands[:ITEM_LIMIT], weight, value, low[b], high[b])

        if not chosen and len(cands) > ITEM_LIMIT:
            chosen = choose_subset(cands, weight, value, low[b], high[b])

        for oid in chosen:
            assigned[oid] = b
            load[b] += weight[oid]

    # Fill unused capacity with the most valuable orders first.
    for oid in order_ids:
        if assigned[oid] != 0:
            continue

        choices = [
            b
            for b in vehicles
            if load[b] >= low[b] and load[b] + weight[oid] <= high[b]
        ]
        if choices:
            b = min(choices, key=lambda x: high[x] - load[x] - weight[oid])
            assigned[oid] = b
            load[b] += weight[oid]

    return assigned, load


def solution_score(assigned, value):
    return sum(value[i] for i in range(1, len(assigned)) if assigned[i] != 0)


def valid_load(total, vehicle, low, high):
    return total == 0 or low[vehicle] <= total <= high[vehicle]


def tabu_search(assigned, load, vehicles, weight, value, low, high):
    """Improve a feasible assignment using add, replace, move and swap moves."""
    rng = random.Random(RANDOM_SEED)
    current_score = solution_score(assigned, value)
    best_assigned = assigned[:]
    best_score = current_score

    # (order, forbidden_vehicle) -> first iteration where it is allowed again.
    tabu_until = {}
    stagnation = 0

    for iteration in range(MAX_ITERATIONS):
        unassigned = [i for i in range(1, len(assigned)) if assigned[i] == 0]
        used_orders = [i for i in range(1, len(assigned)) if assigned[i] != 0]

        unassigned.sort(key=lambda i: (value[i], value[i] / weight[i]), reverse=True)
        used_orders.sort(key=lambda i: (value[i] / weight[i], value[i]))
        unassigned = unassigned[:ITEM_LIMIT]
        used_orders = used_orders[:ITEM_LIMIT]
        rng.shuffle(vehicles)

        best_move = None
        best_move_score = NEG
        checked = 0

        def consider(changes, new_loads, new_score):
            nonlocal best_move, best_move_score, checked
            if checked >= MAX_NEIGHBORS:
                return
            checked += 1

            for b, total in new_loads.items():
                if not valid_load(total, b, low, high):
                    return

            is_tabu = any(tabu_until.get((oid, new_b), -1) > iteration for oid, new_b in changes)
            aspiration = new_score > best_score
            if is_tabu and not aspiration:
                return

            if new_score > best_move_score:
                best_move_score = new_score
                best_move = (changes, new_loads)

        # Add one unused order to a vehicle.
        for oid in unassigned:
            for b in vehicles:
                new_total = load[b] + weight[oid]
                consider([(oid, b)], {b: new_total}, current_score + value[oid])

        # Replace an assigned order with an unused order.
        for new_oid in unassigned:
            for old_oid in used_orders:
                b = assigned[old_oid]
                new_total = load[b] - weight[old_oid] + weight[new_oid]
                new_score = current_score - value[old_oid] + value[new_oid]
                consider(
                    [(old_oid, 0), (new_oid, b)],
                    {b: new_total},
                    new_score,
                )

        # Move an order between vehicles. The score is unchanged, but this can
        # create room for a valuable order in a later iteration.
        for oid in used_orders:
            old_b = assigned[oid]
            for new_b in vehicles:
                if new_b == old_b:
                    continue
                new_loads = {
                    old_b: load[old_b] - weight[oid],
                    new_b: load[new_b] + weight[oid],
                }
                consider([(oid, new_b)], new_loads, current_score)

        # Swap two assigned orders belonging to different vehicles.
        for pos, first in enumerate(used_orders):
            first_b = assigned[first]
            for second in used_orders[pos + 1:]:
                second_b = assigned[second]
                if first_b == second_b:
                    continue
                new_loads = {
                    first_b: load[first_b] - weight[first] + weight[second],
                    second_b: load[second_b] - weight[second] + weight[first],
                }
                consider(
                    [(first, second_b), (second, first_b)],
                    new_loads,
                    current_score,
                )

        if best_move is None:
            break

        changes, new_loads = best_move
        old_vehicles = {oid: assigned[oid] for oid, _ in changes}

        for oid, new_b in changes:
            assigned[oid] = new_b
        for b, total in new_loads.items():
            load[b] = total

        current_score = best_move_score
        for oid, _ in changes:
            tabu_until[(oid, old_vehicles[oid])] = iteration + TABU_TENURE

        if current_score > best_score:
            best_score = current_score
            best_assigned = assigned[:]
            stagnation = 0
        else:
            stagnation += 1

        if stagnation >= MAX_STAGNATION:
            break

    return best_assigned


def main():
    first_line = sys.stdin.buffer.readline().split()
    if not first_line:
        return

    n, k = map(int, first_line)
    weight = [0] * (n + 1)
    value = [0] * (n + 1)
    for i in range(1, n + 1):
        weight[i], value[i] = map(int, sys.stdin.buffer.readline().split())

    vehicles = list(range(1, k + 1))
    low = [0] * (k + 1)
    high = [0] * (k + 1)
    for b in vehicles:
        low[b], high[b] = map(int, sys.stdin.buffer.readline().split())

    assigned, load = make_initial_solution(
        n, vehicles, weight, value, low, high
    )
    assigned = tabu_search(
        assigned, load, vehicles, weight, value, low, high
    )

    answer = [(i, assigned[i]) for i in range(1, n + 1) if assigned[i] != 0]
    output = [str(len(answer))]
    output.extend(f"{oid} {b}" for oid, b in answer)
    sys.stdout.write("\n".join(output))


if __name__ == "__main__":
    main()


#ok con de 
# ok ae 