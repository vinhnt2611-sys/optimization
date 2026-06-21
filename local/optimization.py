from ortools.linear_solver import pywraplp

# def solve(name, obj, weights, cap):
#     s = pywraplp.Solver.CreateSolver('CBC')
#     x = [s.IntVar(0, s.infinity(), f'x{i+1}') for i in range(len(obj))]
#     s.Add(sum(weights[i]*x[i] for i in range(len(obj))) <= cap)
#     s.Maximize(sum(obj[i]*x[i] for i in range(len(obj))))
#     s.Solve()
#     vals = [int(x[i].solution_value()) for i in range(len(obj))]
#     print(f"{name}: {vals} → obj={int(s.Objective().Value())}")

# solve('a', [17,8,6,3], [7,6,4,2], 19)
# solve('b', [16,9,7,5], [6,5,3,2], 17)
# solve('c', [16,8,6,1], [7,6,4,1], 26)

# def solve_d():
#     s = pywraplp.Solver.CreateSolver('CBC')
#     x1 = s.IntVar(0, s.infinity(), 'x1')
#     x2 = s.IntVar(0, s.infinity(), 'x2')
#     x3 = s.IntVar(0, s.infinity(), 'x3')
#     s.Add(5*x1 + 9*x2 + 13*x3 >= 19)
#     s.Maximize(x1 + x2)
#     s.Solve()
#     print(f"d: x1={int(x1.solution_value())}, x2={int(x2.solution_value())} → obj={int(s.Objective().Value())}")

# solve_d()


# Problem 1: Farmer's field — maximize profit = revenue - cost
# x[i] = area (m²) planted with vegetable type i (continuous)
# Constraints: sum(x) == A, x[i] <= c[i], sum(x[i] for i in group j) <= d[j]

# from ortools.linear_solver import pywraplp
# solver=pywraplp.Solver.CreateSolver("GLOP")
# A,n,m=map(int,input().split())
# group=list(map(int,input().split()))
# a=list(map(int,input().split()))
# b=list(map(int,input().split()))
# c=list(map(int,input().split()))
# d=list(map(int,input().split()))
# x={}
# for i in range(n):
#     x[i]=solver.NumVar(0,c[i],f"x{i}")
# for j in range(1,m+1):
#     solver.Add(sum(x[i] for i in range(n) if group[i]==j)<=d[j-1])
# solver.Add(sum(x[i] for i in range(n))==A)
# solver.Maximize(sum((b[i]-a[i])*x[i] for i in range(n)))
# status=solver.Solve()
# if status==pywraplp.Solver.OPTIMAL:
#     print("Solution")
#     print(f"{solver.Objective().Value():.2f}")
# else:
#     print("No solution")

# from ortools.linear_solver import pywraplp
# s=pywraplp.Solver.CreateSolver('SAT')
# x=[s.IntVar(0,s.infinity(),f'x{i+1}') for i in range(5)]
# s.Add( 5*x[0]+ 7*x[1]+ 9*x[2]+ 2*x[3]+  x[4]<=250)
# s.Add(18*x[0]+ 4*x[1]- 9*x[2]+10*x[3]+12*x[4]<=285)
# s.Add( 4*x[0]+ 7*x[1]+ 3*x[2]+ 8*x[3]+ 5*x[4]<=211)
# s.Add( 5*x[0]+13*x[1]+16*x[2]+ 3*x[3]- 7*x[4]<=315)
# s.Maximize(7*x[0]+8*x[1]+2*x[2]+9*x[3]+6*x[4])
# s.Solve()
# for i in range(len(x)):
#     if i < len(x) - 1:
#         print(f'x{i+1} = {int(x[i].solution_value())}',end = ',')
#     else :
#         print(f'x{i+1} = {int(x[i].solution_value())}')

# print('Optimal = 'f'{s.Objective().Value():0.0f}')





