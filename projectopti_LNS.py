import random
import sys
import time

NEG = -10**12
TIME_LIMIT = 0.35 # maximum runtime of LNS
MAX_ITERATIONS = 120 # meaning that LNS stops when reach time limit or max iterations
DESTROY_COUNT = 2 # remove all assginment of two cars, and then using dp to reconstruct the two cars
RATIO_CANDIDATES = 70 # top 70 , just like the previous code 
RANDOM_CANDIDATES = 30 # increasing variane
RESET_AFTER = 25 # if after 25 round the solution is not more efficient, comeback to the previous best solution
RANDOM_SEED = 42


def choose_subset(cands, weight, value, low, high):
    dp = [NEG] * (high + 1)
    picked = [None] * (high + 1)
    dp[0] = 0
    picked[0] = ()

    for oid in cands:
        current_weight = weight[oid]
        if current_weight > high:
            continue

        current_value = value[oid]
        for cap in range(high, current_weight - 1, -1):
            previous_value = dp[cap - current_weight]
            if previous_value == NEG:
                continue

            new_value = previous_value + current_value
            if new_value > dp[cap]:
                dp[cap] = new_value
                picked[cap] = (oid, picked[cap - current_weight])

    best_cap = -1
    best_score = NEG
    for cap in range(low, high + 1):
        if dp[cap] == NEG:
            continue

        score = dp[cap] - (cap - low) * 10000
        if score > best_score:
            best_score = score
            best_cap = cap

    if best_cap < 0:
        return []

    chosen = []
    node = picked[best_cap]
    while node:
        oid, node = node
        chosen.append(oid)
    return chosen


def build_candidates(used, weight, high, by_ratio, by_weight):
    cands = []
    seen = set()

    for oid in by_ratio:
        if not used[oid] and weight[oid] <= high:
            cands.append(oid)
            seen.add(oid)
            if len(cands) == RATIO_CANDIDATES:
                break

    for current_weight in range(1, min(100, high) + 1):
        taken = 0
        for oid in by_weight[current_weight]:
            if not used[oid] and oid not in seen:
                cands.append(oid)
                seen.add(oid)
                taken += 1
                if taken == 2:
                    break

    return cands


def solution_score(assigned, value):
    return sum(
        value[oid]
        for oid in range(1, len(assigned))
        if assigned[oid] != 0
    )


def make_initial_solution(n, k, weight, value, low, high):
    """Create the starting solution with the original greedy and DP method."""
    vehicles = list(range(1, k + 1))
    by_ratio = list(range(1, n + 1))
    by_ratio.sort(
        key=lambda oid: (value[oid] / weight[oid], value[oid]),
        reverse=True,
    )

    by_weight = [[] for _ in range(101)]
    for oid in range(1, n + 1):
        by_weight[weight[oid]].append(oid)
    for current_weight in range(1, 101):
        by_weight[current_weight].sort(
            key=lambda oid: value[oid],
            reverse=True,
        )

    vehicle_order = sorted(
        vehicles,
        key=lambda b: (high[b] - low[b], high[b], -low[b]),
    )
    used = [False] * (n + 1)
    assigned = [0] * (n + 1)
    load = [0] * (k + 1)

    for b in vehicle_order:
        cands = build_candidates(
            used, weight, high[b], by_ratio, by_weight
        )
        chosen = choose_subset(
            cands, weight, value, low[b], high[b]
        )

        if not chosen:
            cands = [
                oid
                for oid in range(1, n + 1)
                if not used[oid] and weight[oid] <= high[b]
            ]
            chosen = choose_subset(
                cands, weight, value, low[b], high[b]
            )

        for oid in chosen:
            used[oid] = True
            assigned[oid] = b
            load[b] += weight[oid]

    fill_remaining(
        assigned, load, vehicles, by_ratio, weight, low, high
    )
    return assigned, load, by_ratio


def fill_remaining(assigned, load, vehicles, by_ratio, weight, low, high):
    """Use best-fit greedy to fill free capacity after a repair."""
    for oid in by_ratio:
        if assigned[oid] != 0:
            continue

        best_vehicle = 0
        best_left = 10**18
        for b in vehicles:
            if load[b] < low[b]:
                continue

            left = high[b] - load[b] - weight[oid]
            if 0 <= left < best_left:
                best_vehicle = b
                best_left = left

        if best_vehicle:
            assigned[oid] = best_vehicle
            load[best_vehicle] += weight[oid]


def repair_destroyed_vehicles(
    assigned,
    load,
    destroyed,
    by_ratio,
    weight,
    value,
    low,
    high,
    rng,
):
    """Remove selected vehicles' orders and rebuild those vehicles with DP."""
    for oid in range(1, len(assigned)):
        if assigned[oid] in destroyed:
            assigned[oid] = 0
    for b in destroyed:
        load[b] = 0

    repair_order = destroyed[:]
    rng.shuffle(repair_order)

    for b in repair_order:
        eligible = [
            oid
            for oid in by_ratio
            if assigned[oid] == 0 and weight[oid] <= high[b]
        ]
        if not eligible:
            continue

        cands = eligible[:RATIO_CANDIDATES]
        remaining = eligible[RATIO_CANDIDATES:]
        if remaining:
            sample_size = min(RANDOM_CANDIDATES, len(remaining))
            cands.extend(rng.sample(remaining, sample_size))

        chosen = choose_subset(
            cands, weight, value, low[b], high[b]
        )

        for oid in chosen:
            assigned[oid] = b
            load[b] += weight[oid]

    fill_remaining(
        assigned, load, destroyed, by_ratio, weight, low, high
    )

    return all(
        load[b] == 0 or low[b] <= load[b] <= high[b]
        for b in destroyed
    )


def large_neighborhood_search(
    assigned, load, vehicles, by_ratio, weight, value, low, high
):
    """Improve the greedy solution by repeatedly destroying and repairing it."""
    rng = random.Random(RANDOM_SEED)
    start = time.perf_counter()

    current_assigned = assigned[:]
    current_load = load[:]
    best_assigned = assigned[:]
    best_load = load[:]
    best_score = solution_score(best_assigned, value)
    no_improvement = 0

    for _ in range(MAX_ITERATIONS):
        if time.perf_counter() - start >= TIME_LIMIT:
            break

        candidate_assigned = current_assigned[:]
        candidate_load = current_load[:]
        count = min(DESTROY_COUNT, len(vehicles))
        destroyed = rng.sample(vehicles, count)

        feasible = repair_destroyed_vehicles(
            candidate_assigned,
            candidate_load,
            destroyed,
            by_ratio,
            weight,
            value,
            low,
            high,
            rng,
        )
        if not feasible:
            continue

        candidate_score = solution_score(candidate_assigned, value)
        current_assigned = candidate_assigned
        current_load = candidate_load

        if candidate_score > best_score:
            best_score = candidate_score
            best_assigned = candidate_assigned[:]
            best_load = candidate_load[:]
            no_improvement = 0
        else:
            no_improvement += 1

        if no_improvement >= RESET_AFTER:
            current_assigned = best_assigned[:]
            current_load = best_load[:]
            no_improvement = 0

    return best_assigned


def main():
    first_line = sys.stdin.buffer.readline().split()
    if not first_line:
        return

    n, k = map(int, first_line)
    weight = [0] * (n + 1)
    value = [0] * (n + 1)
    for oid in range(1, n + 1):
        weight[oid], value[oid] = map(
            int, sys.stdin.buffer.readline().split()
        )

    vehicles = list(range(1, k + 1))
    low = [0] * (k + 1)
    high = [0] * (k + 1)
    for b in vehicles:
        low[b], high[b] = map(int, sys.stdin.buffer.readline().split())

    assigned, load, by_ratio = make_initial_solution(
        n, k, weight, value, low, high
    )
    assigned = large_neighborhood_search(
        assigned,
        load,
        vehicles,
        by_ratio,
        weight,
        value,
        low,
        high,
    )

    answer = [
        (oid, assigned[oid])
        for oid in range(1, n + 1)
        if assigned[oid] != 0
    ]
    output = [str(len(answer))]
    output.extend(f"{oid} {b}" for oid, b in answer)
    sys.stdout.write("\n".join(output))


if __name__ == "__main__":
    main()
