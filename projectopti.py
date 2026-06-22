import sys


NEG = -10**12


def choose_subset(cands, w, val, low, high): #determine potential variable
    dp = [NEG] * (high + 1) #dp[cap] means the best value at the weight of cap
    picked = [None] * (high + 1)
    dp[0] = 0
    picked[0] = []

    for oid in cands:
        wi = w[oid] #current weight
        if wi > high:
            continue

        vi = val[oid] # current value

        for cap in range(high, wi - 1, -1): # 0/1 knapsack
            prev = dp[cap - wi]
            if prev == NEG:
                continue

            new_val = prev + vi
            if new_val > dp[cap]:
                dp[cap] = new_val # update the best value with current capacity
                picked[cap] = picked[cap - wi] + [oid] # add a potential candidate to picked

    best_cap = -1
    best_score = NEG

    for cap in range(low, high + 1):
        if dp[cap] == NEG: # cant obtain the weight 
            continue
        #penalty
        score = dp[cap] - (cap - low) * 10000 #prioritize the total weight to near low => smaller the cap - slow => the better
        if score > best_score:
            best_score = score
            best_cap = cap

    if best_cap < 0: # when there is no combination in range low and high
        return []

    return picked[best_cap] # list of potential variable

#by_ratio = val[i]/w[i], the bigger the better , sorted downward
#by_ weight stores candidates that have the weights[i]
def build_candidates(used, w, high, by_ratio, by_weight):
    cands = []
    seen = set()
    # prioritize quality
    for oid in by_ratio:
        if not used[oid] and w[oid] <= high:
            cands.append(oid)
            seen.add(oid)
            if len(cands) == 70 : # heuristic parameter , the higher , the better the quality, the lower the higher the speed:
                break

    # prioritize the variance to overcome issues like repetition

    for weight in range(1, min(100, high) + 1): #minimize sample size
        taken = 0
        for oid in by_weight[weight]:
            if not used[oid] and oid not in seen:
                cands.append(oid)
                seen.add(oid)
                taken += 1
                if taken == 2 : # heuristic parameter, the purpose is to minimize the size of cands and put the same weight into dp:
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
    by_ratio.sort(key=lambda i: (val[i] / w[i], val[i]), reverse=True) # the higher the ratio the better

    by_weight = [[] for _ in range(101)]
    for i in range(1, n + 1):
        by_weight[w[i]].append(i) 
    for weight in range(1, 101):
        by_weight[weight].sort(key=lambda i: val[i], reverse=True) # same weight => the better value will comefirst

    vehicles.sort(key=lambda b: (high[b] - low[b], high[b], -low[b])) # prioritize the harder combinations, meaning if car 1 runs from 12 to 14, car 2 runs from 27 to 31 => prioritize car 1

    used = [False] * (n + 1)
    assigned = [0] * (n + 1) # assigned[i] = b => the oid i belong to car b
    load = [0] * (k + 1) # stores current capacity of each car

    for b in vehicles:
        cands = build_candidates(used, w, high[b], by_ratio, by_weight)
        chosen = choose_subset(cands, w, val, low[b], high[b])

        if not chosen:
            cands = [i for i in range(1, n + 1) if not used[i] and w[i] <= high[b]] # take all appropriate combination
            chosen = choose_subset(cands, w, val, low[b], high[b]) # this recursion help to avoid when build_candidates qualify variable too strictly

        for oid in chosen:
            used[oid] = True
            assigned[oid] = b # avoid other cars to use this ship
            load[b] += w[oid] # update the current capacity

    # if there is still available capacity, add more
    for oid in by_ratio:
        if used[oid]:
            continue

        best_b = 0 # still not find suitable car 
        best_left = 10**9 # store the current capacity after add the bill

        for b in vehicles:
            if load[b] < low[b]: # only consider when the car reach its minimum capacity 
                continue

            left = high[b] - load[b] - w[oid] # compute left over capacity when add current bill
            if 0 <= left < best_left: # choose the bill that best fits
                best_left = left
                best_b = b

        if best_b: # if find the suitable car then we store this bill
            used[oid] = True
            assigned[oid] = best_b
            load[best_b] += w[oid]

    for b in vehicles:
        if load[b] and not (low[b] <= load[b] <= high[b]): # if exceed the limitation capacity => cancel assignment
            for oid in range(1, n + 1):
                if assigned[oid] == b:
                    assigned[oid] = 0

    ans = [(i, assigned[i]) for i in range(1, n + 1) if assigned[i]] # print value

    out = [str(len(ans))]
    out += [f"{i} {b}" for i, b in ans] # id - car
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()


 