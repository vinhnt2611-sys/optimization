from collections import Counter
nums = [4,1,-1,2,-1,2,3]
k = 2
mp = Counter(nums)

result = sorted(mp.items(), key = lambda x : x[1], reverse = True)
res = []
for i in range (k) : 
    res.append(result[i][0])

print(res)