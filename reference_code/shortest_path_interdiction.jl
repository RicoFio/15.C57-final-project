import Pkg
Pkg.add("BilevelJuMP")
Pkg.add("HiGHS")
using BilevelJuMP
using HiGHS

# Big M value
M = 1000
# Epsilon value
eps = 0.0001

# graph definitions
# nodes
N = [1,2,3,4]
# edges
A = [(1,2), (1,3), (2,3), (2,4), (3,4)]

# Edge data
# edge travel times
tt = [1, 2, 1, 2, 1]
# edge fortification levels
fl = [1, 1, 1, 1, 1]

# od pair
s = 1
t = 4
# interdiction cost
c = [1, 1, 1, 1, 1]
# edge disruption travel time penalties
e = [10, 10, 10, 10, 10]

# Budgets
## Interdiction budget
B_interdiction = 3

# bilevel model formulation
model = BilevelModel(
    HiGHS.Optimizer,
    mode = BilevelJuMP.FortunyAmatMcCarlMode(primal_big_M = 1000, dual_big_M = 1000)
)

# Interdiction variables
@variable(Upper(model), x[i=1:length(A)], Bin)
# Flow variables
@variable(Lower(model), y[i=1:length(A)] >= 0)

@objective(Upper(model), Max, sum([(tt[k_idx] + e[k_idx]*x[k_idx]) * y[k_idx] for (k_idx, _) in enumerate(A)]))
@objective(Lower(model), Min, sum([(tt[k_idx] + e[k_idx]*x[k_idx]) * y[k_idx] for (k_idx, _) in enumerate(A)]))


@constraint(Lower(model), sum(y[(s, j)] for j in A if (s, j) in A) == 1)
@constraint(Lower(model), sum(x[(i, t)] for i in A if (i, t) in A) == 1)

for k in setdiff(A, [s, t])
    @constraint(Lower(model), sum(x[(i, node)] for i in A if (i, node) in A) ==
                        sum(x[(node, j)] for j in A if (node, j) in A))
end

@constraint(Upper(model), dot(x, c) <= B_interdiction)

optimize!(model)

