import sys


NEG = -10**12


def choose_subset(cands, w, val, low, high):
    dp = [NEG] * (high + 1)
    picked = [None] * (high + 1)
    dp[0] = 0
    picked[0] = []

    for oid in cands:
        wi = w[oid]
        if wi > high:
            continue

        vi = val[oid]

        for cap in range(high, wi - 1, -1):
            prev = dp[cap - wi]
            if prev == NEG:
                continue

            new_val = prev + vi
            if new_val > dp[cap]:
                dp[cap] = new_val
                picked[cap] = picked[cap - wi] + [oid]

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

    return picked[best_cap]


def build_candidates(used, w, high, by_ratio, by_weight):
    cands = []
    seen = set()

    for oid in by_ratio:
        if not used[oid] and w[oid] <= high:
            cands.append(oid)
            seen.add(oid)
            if len(cands) == 70:
                break

    for weight in range(1, min(100, high) + 1):
        taken = 0
        for oid in by_weight[weight]:
            if not used[oid] and oid not in seen:
                cands.append(oid)
                seen.add(oid)
                taken += 1
                if taken == 2:
                    break

    return cands


def main():
    first_line = sys.stdin.buffer.readline().split()
    if not first_line:
        return

    n, k = map(int, first_line)

    w = [0] * (n + 1)
    val = [0] * (n + 1)
    for i in range(1, n + 1):
        w[i], val[i] = map(int, sys.stdin.buffer.readline().split())

    low = [0] * (k + 1)
    high = [0] * (k + 1)
    vehicles = list(range(1, k + 1))
    for b in vehicles:
        low[b], high[b] = map(int, sys.stdin.buffer.readline().split())

    by_ratio = list(range(1, n + 1))
    by_ratio.sort(key=lambda i: (val[i] / w[i], val[i]), reverse=True)

    by_weight = [[] for _ in range(101)]
    for i in range(1, n + 1):
        by_weight[w[i]].append(i)
    for weight in range(1, 101):
        by_weight[weight].sort(key=lambda i: val[i], reverse=True)

    vehicles.sort(key=lambda b: (high[b] - low[b], high[b], -low[b]))

    used = [False] * (n + 1)
    assigned = [0] * (n + 1)
    load = [0] * (k + 1)

    for b in vehicles:
        cands = build_candidates(used, w, high[b], by_ratio, by_weight)
        chosen = choose_subset(cands, w, val, low[b], high[b])

        if not chosen:
            cands = [i for i in range(1, n + 1) if not used[i] and w[i] <= high[b]]
            chosen = choose_subset(cands, w, val, low[b], high[b])

        for oid in chosen:
            used[oid] = True
            assigned[oid] = b
            load[b] += w[oid]

    for oid in by_ratio:
        if used[oid]:
            continue

        best_b = 0
        best_left = 10**9

        for b in vehicles:
            if load[b] < low[b]:
                continue

            left = high[b] - load[b] - w[oid]
            if 0 <= left < best_left:
                best_left = left
                best_b = b

        if best_b:
            used[oid] = True
            assigned[oid] = best_b
            load[best_b] += w[oid]

    for b in vehicles:
        if load[b] and not (low[b] <= load[b] <= high[b]):
            for oid in range(1, n + 1):
                if assigned[oid] == b:
                    assigned[oid] = 0

    ans = [(i, assigned[i]) for i in range(1, n + 1) if assigned[i]]

    out = [str(len(ans))]
    out += [f"{i} {b}" for i, b in ans]
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()


#hello anh em nhe ]
