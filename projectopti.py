import heapq
import sys
from array import array


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
    point_count = 2 * n + 2 * m + 1
    distance = [array("I", read_row(point_count)) for _ in range(point_count)]
    return n, m, k, parcel_quantity, capacity, distance


def request_nodes(request, n, m):
    if request < n:
        pickup = request + 1
        dropoff = pickup + n + m
        return pickup, dropoff

    parcel = request - n
    pickup = n + parcel + 1
    dropoff = 2 * n + m + parcel + 1
    return pickup, dropoff


def request_demand(request, n, parcel_quantity):
    if request < n:
        return 0
    return parcel_quantity[request - n]


def insertion_delta(route, position, request, n, m, distance):
    pickup, dropoff = request_nodes(request, n, m)

    if position == 0:
        previous = 0
    else:
        _, previous = request_nodes(route[position - 1], n, m)

    if position == len(route):
        following = 0
    else:
        following, _ = request_nodes(route[position], n, m)

    return (
        distance[previous][pickup]
        + distance[pickup][dropoff]
        + distance[dropoff][following]
        - distance[previous][following]
    )


def request_priority(request, n, m, parcel_quantity, capacity, distance):
    pickup, dropoff = request_nodes(request, n, m)
    standalone = (
        distance[0][pickup]
        + distance[pickup][dropoff]
        + distance[dropoff][0]
    )
    demand = request_demand(request, n, parcel_quantity)
    eligible_taxis = sum(cap >= demand for cap in capacity)
    return eligible_taxis, -standalone


def best_insertion(
    request,
    routes,
    lengths,
    n,
    m,
    parcel_quantity,
    capacity,
    distance,
):
    demand = request_demand(request, n, parcel_quantity)
    largest = max(lengths, default=0)
    largest_count = sum(length == largest for length in lengths)
    second_largest = max((x for x in lengths if x != largest), default=0)

    best = None
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
            if best is None or key < best[0]:
                best = (key, taxi, position, delta)

    return best


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
        choice = best_insertion(
            request,
            routes,
            lengths,
            n,
            m,
            parcel_quantity,
            capacity,
            distance,
        )
        if choice is None:
            raise ValueError("No taxi has enough capacity for a parcel")

        _, taxi, position, delta = choice
        routes[taxi].insert(position, request)
        lengths[taxi] += delta

    return routes, lengths


def route_points(route, n, m):
    points = [0]
    for request in route:
        pickup, dropoff = request_nodes(request, n, m)
        points.extend((pickup, dropoff))
    points.append(0)
    return points


def route_length(points, distance):
    return sum(distance[a][b] for a, b in zip(points, points[1:]))


def can_insert_at(points, position, n, m):
    previous = points[position - 1]
    following = points[position]
    return not (
        1 <= previous <= n
        and following == previous + n + m
    )


def capacity_is_valid(points, taxi, n, m, parcel_quantity, capacity):
    current_load = 0
    for point in points:
        if n + 1 <= point <= n + m:
            current_load += parcel_quantity[point - n - 1]
            if current_load > capacity[taxi]:
                return False
        elif 2 * n + m + 1 <= point <= 2 * n + 2 * m:
            current_load -= parcel_quantity[point - (2 * n + m + 1)]
            if current_load < 0:
                return False
    return current_load == 0


def shared_parcel_route(
    route, taxi, n, m, parcel_quantity, capacity, distance
):
    original = route_points(route, n, m)
    passengers = [request for request in route if request < n]
    parcels = [request for request in route if request >= n]
    points = route_points(passengers, n, m)
    current_length = route_length(points, distance)

    parcels.sort(
        key=lambda request: request_priority(
            request, n, m, parcel_quantity, capacity, distance
        )
    )

    for request in parcels:
        pickup, dropoff = request_nodes(request, n, m)
        pickup_positions = []
        for position in range(1, len(points)):
            if not can_insert_at(points, position, n, m):
                continue
            previous, following = points[position - 1], points[position]
            delta = (
                distance[previous][pickup]
                + distance[pickup][following]
                - distance[previous][following]
            )
            pickup_positions.append((delta, position))

        best = None
        for pickup_delta, pickup_position in heapq.nsmallest(
            10, pickup_positions
        ):
            with_pickup = (
                points[:pickup_position]
                + [pickup]
                + points[pickup_position:]
            )
            delivery_positions = []
            for delivery_position in range(pickup_position + 1, len(with_pickup)):
                if not can_insert_at(with_pickup, delivery_position, n, m):
                    continue
                previous = with_pickup[delivery_position - 1]
                following = with_pickup[delivery_position]
                delta = (
                    distance[previous][dropoff]
                    + distance[dropoff][following]
                    - distance[previous][following]
                )
                delivery_positions.append((delta, delivery_position))

            for delivery_delta, delivery_position in heapq.nsmallest(
                10, delivery_positions
            ):
                candidate = (
                    with_pickup[:delivery_position]
                    + [dropoff]
                    + with_pickup[delivery_position:]
                )
                if not capacity_is_valid(
                    candidate, taxi, n, m, parcel_quantity, capacity
                ):
                    continue
                candidate_length = current_length + pickup_delta + delivery_delta
                if best is None or candidate_length < best[0]:
                    best = (candidate_length, candidate)

        if best is None:
            points[-1:-1] = [pickup, dropoff]
            current_length = route_length(points, distance)
        else:
            current_length, points = best

    if route_length(original, distance) < current_length:
        return original
    return points


def write_solution(routes, n, m, parcel_quantity, capacity, distance):
    output = [str(len(routes))]
    for taxi, route in enumerate(routes):
        points = shared_parcel_route(
            route, taxi, n, m, parcel_quantity, capacity, distance
        )
        output.append(str(len(points)))
        output.append(" ".join(map(str, points)))
    sys.stdout.write("\n".join(output))


def main():
    instance = read_instance()
    if instance is None:
        return

    n, m, k, parcel_quantity, capacity, distance = instance
    routes, _ = greedy_routes(
        n, m, k, parcel_quantity, capacity, distance
    )
    write_solution(routes, n, m, parcel_quantity, capacity, distance)


if __name__ == "__main__":
    main()
