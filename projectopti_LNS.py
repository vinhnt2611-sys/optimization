import heapq
import random
import sys
import time
from array import array


TIME_LIMIT = 0.75
MAX_ITERATIONS = 200
DESTROY_ROUTES = 2
RCL_SIZE = 4
RESET_AFTER = 20
RANDOM_SEED = 42


def read_row(expected):
    values = []
    while len(values) < expected:
        values.extend(map(int, sys.stdin.buffer.readline().split()))
    return values


def read_instance():
    first = sys.stdin.buffer.readline().split()
    if not first:
        return None

    n, m, k = map(int, first)
    parcel_quantity = read_row(m)
    capacity = read_row(k)
    size = 2 * n + 2 * m + 1
    distance = [array("I", read_row(size)) for _ in range(size)]
    return n, m, k, parcel_quantity, capacity, distance


def request_nodes(request, n, m):
    if request < n:
        pickup = request + 1
        return pickup, pickup + n + m

    parcel = request - n
    return n + parcel + 1, 2 * n + m + parcel + 1


def request_demand(request, n, parcel_quantity):
    return 0 if request < n else parcel_quantity[request - n]


def insertion_delta(route, position, request, n, m, distance):
    pickup, dropoff = request_nodes(request, n, m)
    previous = 0 if position == 0 else request_nodes(route[position - 1], n, m)[1]
    following = 0 if position == len(route) else request_nodes(route[position], n, m)[0]
    return (
        distance[previous][pickup]
        + distance[pickup][dropoff]
        + distance[dropoff][following]
        - distance[previous][following]
    )


def request_priority(request, n, m, parcel_quantity, capacity, distance):
    pickup, dropoff = request_nodes(request, n, m)
    direct_cost = (
        distance[0][pickup]
        + distance[pickup][dropoff]
        + distance[dropoff][0]
    )
    demand = request_demand(request, n, parcel_quantity)
    eligible_count = sum(taxi_capacity >= demand for taxi_capacity in capacity)
    return eligible_count, -direct_cost


def insertion_choices(
    request,
    routes,
    lengths,
    n,
    m,
    parcel_quantity,
    capacity,
    distance,
    limit,
):
    demand = request_demand(request, n, parcel_quantity)
    largest = max(lengths, default=0)
    largest_count = sum(length == largest for length in lengths)
    second_largest = max((x for x in lengths if x != largest), default=0)
    choices = []

    for taxi, route in enumerate(routes):
        if capacity[taxi] < demand:
            continue

        other_max = largest
        if lengths[taxi] == largest and largest_count == 1:
            other_max = second_largest

        for position in range(len(route) + 1):
            delta = insertion_delta(route, position, request, n, m, distance)
            new_length = lengths[taxi] + delta
            key = (max(other_max, new_length), new_length, delta)
            choices.append((key, taxi, position, delta))

    if not choices:
        return []
    if limit == 1:
        return [min(choices)]
    return heapq.nsmallest(limit, choices)


def greedy_routes(n, m, k, parcel_quantity, capacity, distance):
    routes = [[] for _ in range(k)]
    lengths = [0] * k
    requests = list(range(n + m))
    requests.sort(
        key=lambda request: request_priority(
            request, n, m, parcel_quantity, capacity, distance
        )
    )

    for request in requests:
        choices = insertion_choices(
            request,
            routes,
            lengths,
            n,
            m,
            parcel_quantity,
            capacity,
            distance,
            1,
        )
        if not choices:
            raise ValueError("No taxi has enough capacity for a parcel")

        _, taxi, position, delta = choices[0]
        routes[taxi].insert(position, request)
        lengths[taxi] += delta

    return routes, lengths


def objective(lengths):
    return max(lengths, default=0), sum(lengths) # reduce the longest route, if the longest route is equal, reduce the total length


def choose_destroyed_routes(routes, lengths, rng): 
    nonempty = [taxi for taxi, route in enumerate(routes) if route]
    if not nonempty:
        return []

    nonempty.sort(key=lambda taxi: lengths[taxi], reverse=True) # sort from longest to shortest
    first = rng.choice(nonempty[: min(3, len(nonempty))]) # choose 3 longest randomly to destroy
    destroyed = [first] # create destroyed list
    remaining = [taxi for taxi in nonempty if taxi != first] # other unchoosen taxi
    extra = min(DESTROY_ROUTES - 1, len(remaining)) # chek whether are there any taxi left
    if extra:
        destroyed.extend(rng.sample(remaining, extra)) # choose randomly
    return destroyed


def destroy(routes, lengths, destroyed):
    removed = []
    for taxi in destroyed:
        removed.extend(routes[taxi])
        routes[taxi] = []
        lengths[taxi] = 0
    return removed


def repair(
    removed,
    routes,
    lengths,
    n,
    m,
    parcel_quantity,
    capacity,
    distance,
    rng,
):
    removed.sort(
        key=lambda request: request_priority(
            request, n, m, parcel_quantity, capacity, distance
        )
    )

    for request in removed:
        choices = insertion_choices(
            request,
            routes,
            lengths,
            n,
            m,
            parcel_quantity,
            capacity,
            distance,
            RCL_SIZE,
        )
        if not choices:
            return False

        if len(choices) == 1 or rng.random() < 0.65:
            _, taxi, position, delta = choices[0]
        else:
            _, taxi, position, delta = rng.choice(choices[1:])

        routes[taxi].insert(position, request)
        lengths[taxi] += delta
    return True


def large_neighborhood_search(
    routes, lengths, n, m, parcel_quantity, capacity, distance
):
    rng = random.Random(RANDOM_SEED)
    start = time.perf_counter()
    current_routes = [route[:] for route in routes]
    current_lengths = lengths[:]
    best_routes = [route[:] for route in routes]
    best_lengths = lengths[:]
    best_objective = objective(best_lengths)
    no_improvement = 0

    for _ in range(MAX_ITERATIONS):
        if time.perf_counter() - start >= TIME_LIMIT:
            break

        candidate_routes = [route[:] for route in current_routes]
        candidate_lengths = current_lengths[:]
        destroyed = choose_destroyed_routes(candidate_routes, candidate_lengths, rng)
        removed = destroy(candidate_routes, candidate_lengths, destroyed)
        rng.shuffle(removed)

        feasible = repair(
            removed,
            candidate_routes,
            candidate_lengths,
            n,
            m,
            parcel_quantity,
            capacity,
            distance,
            rng,
        )
        if not feasible:
            continue

        candidate_objective = objective(candidate_lengths)
        current_objective = objective(current_lengths)
        threshold = best_objective[0] * 1.03

        if candidate_objective <= current_objective or candidate_objective[0] <= threshold:
            current_routes = candidate_routes
            current_lengths = candidate_lengths

        if candidate_objective < best_objective:
            best_objective = candidate_objective
            best_routes = [route[:] for route in candidate_routes]
            best_lengths = candidate_lengths[:]
            no_improvement = 0
        else:
            no_improvement += 1

        if no_improvement >= RESET_AFTER:
            current_routes = [route[:] for route in best_routes]
            current_lengths = best_lengths[:]
            no_improvement = 0

    return best_routes, best_lengths


def route_points(route, n, m):
    points = [0]
    for request in route:
        points.extend(request_nodes(request, n, m))
    points.append(0)
    return points


def write_solution(routes, n, m):
    output = [str(len(routes))]
    for route in routes:
        points = route_points(route, n, m)
        output.append(str(len(points)))
        output.append(" ".join(map(str, points)))
    sys.stdout.write("\n".join(output))


def main():
    instance = read_instance()
    if instance is None:
        return

    n, m, k, parcel_quantity, capacity, distance = instance
    routes, lengths = greedy_routes(n, m, k, parcel_quantity, capacity, distance)
    routes, _ = large_neighborhood_search(
        routes, lengths, n, m, parcel_quantity, capacity, distance
    )
    write_solution(routes, n, m)


if __name__ == "__main__":
    main()
