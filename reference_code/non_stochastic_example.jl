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

# Node data
# residential centers
rc = [1]
# # population groups in all residential centers
# pg = [1, 2, 3]
# # population group income levels
# pgil = [1000, 2000, 3000]

# Edge data
# edge travel times
tt = [1, 2, 1, 2, 1]
# edge fortification levels
fl = [1, 1, 1, 1, 1]

# od pairs for each residential center
od = [(1,4)]
# # population group sizes per residential center
# pgs = [[100, 20, 10], [20, 100, 10], [10, 20, 100]]
# edge disruption travel time penalties
e = [10, 10, 10, 10, 10]

# Budgets
## Fortification budget
B_f = 10
## Weakening budget
B_w = 10

# bilevel model formulation
model = BilevelModel(
    HiGHS.Optimizer,
    mode = BilevelJuMP.FortunyAmatMcCarlMode(primal_big_M = 1000, dual_big_M = 1000)
)

# Dummie variable for objective function
@variable(Upper(model), hu)
@variable(Lower(model), hl)

# Fortification variables
@variable(Upper(model), f[i=1:length(A)])
# Weakening variables
@variable(Lower(model), w[i=1:length(A)])
# Successful interdiction variables
@variable(Lower(model), 0<= z[i=1:length(A)]<=1)
# Flow variables
### [[[_ for _ in A] for _ in od[rc_i]] for rc_i in rc]
@variable(Lower(model), Pi[1:length(rc), 1:length(A)])

@objective(Upper(model), Min, hu)
@objective(Lower(model), Max, hl)

@constraint(Upper(model), hu == 
    sum(Pi[rc_i, origin] - Pi[rc_i, destination] 
        for (rc_i, (origin, destination)) in zip(range(1,length(rc)), od) 
    )
)

@constraint(Lower(model), hl == 
    sum(Pi[rc_i, origin] - Pi[rc_i, destination] 
        for (rc_i, (origin, destination)) in zip(range(1,length(rc)), od)
    )
)

for (a_idx, (a_i, a_j)) in enumerate(A)
    for rc_i in range(1,length(rc))
        @constraint(Lower(model), Pi[rc_i, a_j] - Pi[rc_i, a_i] - e[a_idx] *z[a_idx] - tt[a_idx] <= 0)
    end
    @constraint(Lower(model), f[a_idx]-w[a_idx]-M*z[a_idx]+eps <= 0)
    @constraint(Lower(model), -M*(1-z[a_idx])-f[a_idx]+w[a_idx] <= 0)
end

for (o, _) in od
    for rc_i in range(1, length(rc))
        @constraint(Lower(model), Pi[rc_i, o] == 0)
    end
end

@constraint(Upper(model), sum(f) <= B_f)
@constraint(Lower(model), sum(w) <= B_w)

optimize!(model)