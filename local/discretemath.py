# from collections import Counter 
# a = list(map(int,input().split()))
# b = list(map(int,input().split()))
# target = int(input())
# def knapsack(a,b,target) :
#     n = len(a)
#     ratios = [a[i]/b[i] for i in range(n)]          # thêm 1: tính ratio value/weight
#     path = []
#     res = [[]]
#     ans = 0

#     # def upper_bound(k, remaining, score):             # thêm 2: upper bound
#     #     return score + remaining * max(ratios[k:])

#     def Try(k,cursum) :
#         nonlocal ans,res

#         cur = sum(path[i]*a[i] for i in range(len(path)))

#         if k == n :
#             if cur > ans :
#                 ans = cur
#                 res[0] = path[:]
#             return

#         # if upper_bound(k, target - cursum, cur) <= ans:  # cắt nhánh
#         #     return

#         maxval = (target - cursum)//b[k]

#         for i in range (maxval, -1, -1) :   #đổi thành [1,0] nếu làm knapsack 0 1 
#             path.append(i)
#             Try(k + 1,cursum + b[k]*i)
#             path.pop()

#     Try(0,0)

#     return res,ans

# path, final = knapsack(a,b,target)
# print(final)
# nums = [1,2,3,4,5,6]
# k =5
# def combination(nums,k) : 
#     path = []
#     res = []
#     def Try(idx) : 
#         if len(path)== k : 
#             res.append(''.join(str(x) for x in path))

#             return 
        
#         for i in range (idx,len(nums)) : 
    
#             path.append(nums[i])
#             Try(i + 1)
#             path.pop()

#     Try(0)
#     return res 

# ans = combination(nums,k)
# print(ans)
# print(len(ans))


# def permutations(nums) : 
#     path = []
#     res = []
#     used = [False]*(len(nums))

#     def Try(k) : 
#         if len(path) == len(nums) : 
#             res.append(''.join(str(x) for x in path))

#             return 

#         for i in range (len(nums)) : 
#             if used[i] : 
#                 continue 

#             path.append(nums[i])
#             used[i] = True
#             Try(k + 1)
#             path.pop()
#             used[i] = False

#     Try(0)

#     return res 

# ans = permutations(nums)
# for i in ans : 
#     print(i)
# print(len(ans))
        

# def win() : 
#     path = []
#     res = []

#     def Try(k) : 
#         mp = Counter(path)
#         for i in mp : 
#             if mp[i] == 3 : 
#                 res.append(path[:])

#                 return 
        
#         for i in ['A','B'] : 
#             path.append(i)
#             Try(k + 1)
#             path.pop()

#     Try(0)
#     return res 

# print(win())

# candidates = [1,2,3]
# target = 7
# def combinationsum(candidates,target) : 
#     path = []
#     res = []

#     def Try(k,cursum) : 
#         if cursum == target : 
#             res.append(path[:])
#             return 
#         if cursum > target : 
#             return 
#         for i in range (k,len(candidates)) : 
#             path.append(candidates[i])
#             Try(i,cursum + candidates[i])
#             path.pop()

#     Try(0,0)

#     return res 

# print(combinationsum(candidates,target))

n = int(input())
cost = [[0]*n for _ in range(n)]
for i in range(n):
    cost[i] = list(map(int, input().split()))

min_edge = float('inf')
for i in range(n):
    for j in range(n):
        if i != j:
            min_edge = min(min_edge, cost[i][j])
def tsp(cost,n) : 
    optimal = float('inf')
    path = [0]
    res = []
    visited = [False]*n
    visited[0] = True
    def Try(k,cur) : 
        nonlocal optimal, res
        if cur + (n - k + 1)*min_edge >= optimal : 
            return 
        if k == n :
            total_cost = cur + cost[path[-1]][0]
            if total_cost < optimal : 
                optimal = total_cost
                res = path + [0]

            return 
        
        for i in range (1,n) : 
            if visited[i] : 
                continue 
            
            path.append(i)
            visited[i] = True 
            Try(k+1,cur + cost[path[-2]][path[-1]])
            path.pop()
            visited[i] = False

    Try(1,0)

    return res,optimal

res, ans= tsp(cost,n)
print(ans)
print(res)

