# Public Transport Network Defense from Extreme Weather Events
We are developing this project as part of the MIT [6.C75 Optimization Methods](https://student.mit.edu/catalog/m6e.html#6.C57) class of 2024

## How to run
```shell
$ poetry install
$ python ./erna/optimization/*.py # replace * with the file you want to run. See below for more information.
```

## Experiments and Expected Outputs
### [full_formulation.py](erna%2Foptimization%2Ffull_formulation.py)
```shell
INFO:erna_logging:Path Weighting: {(0, 3): 0.0104, (1, 2): 0.004}
INFO:erna_logging:Path Weighting: {(0, 3): 0.0104, (1, 2): 0.004}
INFO:erna_logging:Path Weighting: {(0, 3): 0.0104, (1, 2): 0.004}
INFO:erna_logging:Path Weighting: {(0, 3): 0.0104, (1, 2): 0.004}
INFO:erna_logging:Path Weighting: {(0, 3): 0.0104, (1, 2): 0.004}
INFO:erna_logging:Path Weighting: {(0, 3): 0.0104, (1, 2): 0.004}
```
### [shortest_path.py](erna%2Foptimization%2Fshortest_path.py)
```shell
Shortest path (toy_graph_1, OD: (0,3)):
Edge from 0 to 1 with cost 2
Edge from 1 to 3 with cost 1
```

### [shortest_path_dual.py](erna%2Foptimization%2Fshortest_path_dual.py)
```shell
Shortest path (dual formulation) (toy_graph_1, OD: (0, 3)):
For OD: (0, 3)
[0, 1, 3] travel time: 3.0
```
### [shortest_path_dual_multi_path.py](erna%2Foptimization%2Fshortest_path_dual_multi_path.py)
```shell
Shortest path (dual formulation | multi-path) (toy_graph_1, ODs: [(0, 3), (1, 2)]):
	For OD pair (0, 3)
for node i: 0.0, node j: 2.0
for node i: 0.0, node j: 0.0
for node i: 2.0, node j: 0.0
for node i: 2.0, node j: 3.0
[0, 1, 3] travel time: 3.0
	For OD pair (1, 2)
for node i: 0.0, node j: 2.0
for node i: 0.0, node j: 1.0
for node i: 1.0, node j: 2.0
[1, 3, 2] travel time: 2.0
```

### [shortest_path_dual_multi_path_simple_interdiction.py](erna%2Foptimization%2Fshortest_path_dual_multi_path_simple_interdiction.py)
```shell
Shortest path (dual formulation | multi-path) (toy_graph_1, ODs: [(0, 3), (1, 2)]):
	For OD pair (0, 3)
for node i: 0.0, node j: 2.0
for node i: 0.0, node j: 8.0
for node i: 2.0, node j: 8.0
for node i: 2.0, node j: 13.0
for node i: 8.0, node j: 13.0
[0, 1, 2, 3] travel time: 17.0
	For OD pair (1, 2)
for node i: 0.0, node j: 10.0
for node i: 0.0, node j: 11.0
[1, 2] travel time: 10.0
```
### [shortest_path_dual_multi_path_simple_interdiction_weighted_paths.py](erna%2Foptimization%2Fshortest_path_dual_multi_path_simple_interdiction_weighted_paths.py)
```shell
Shortest path (dual formulation | multi-path) (toy_graph_1, ODs: [(0, 3), (1, 2)]):
	For OD pair (0, 3)
		Interdicted: [(1, 3)]
		 [0, 1, 2, 3] travel time: 17.0
	For OD pair (1, 2)
		Interdicted: [(1, 3)]
		 [1, 2] travel time: 10.0
Interdictions: {(0, 1): 0.0, (0, 2): 0.0, (1, 2): 0.0, (1, 3): 1.0, (2, 3): 0.0, (3, 2): 0.0}
`````
### [shortest_path_dual_simple_interdiction.py](erna%2Foptimization%2Fshortest_path_dual_simple_interdiction.py)
```shell
Shortest path (dual formulation) (toy_graph_1, ODs: (0, 3)):
{0: <gurobi.Var pi[0] (value 0.0)>, 1: <gurobi.Var pi[1] (value 12.0)>, 2: <gurobi.Var pi[2] (value 3.0)>, 3: <gurobi.Var pi[3] (value 8.0)>}
For OD: (0, 3)
[0, 2, 3] travel time: 8.0
Interdictions: {(0, 1): 1.0, (0, 2): 0.0, (1, 2): 0.0, (1, 3): 0.0, (2, 3): 0.0, (3, 2): 0.0}
```
### [shortest_path_dual_simple_interdiction_weighted_paths.py](erna%2Foptimization%2Fshortest_path_dual_simple_interdiction_weighted_paths.py)
```shell
Shortest path (dual formulation) (toy_graph_1, ODs: (0, 3)):
For OD: (0, 3)
[0, 2, 3] travel time: 8.0
Interdictions: {(0, 1): 1.0, (0, 2): 0.0, (1, 2): 0.0, (1, 3): 0.0, (2, 3): 0.0, (3, 2): 0.0}
```
### [shortest_path_multi_path.py](erna%2Foptimization%2Fshortest_path_multi_path.py)
```shell
Shortest paths (multi-path approach) (toy_graph_1, ODs: [(0, 3), (1, 2)]):
	For OD pair (0, 3)
		Edge from 0 to 1 with cost 2
		Edge from 1 to 3 with cost 1
	For OD pair (1, 2)
		Edge from 1 to 3 with cost 1
		Edge from 3 to 2 with cost 1
```
### [shortest_path_multi_path_fixed_interdiction_weighted_paths.py](erna%2Foptimization%2Fshortest_path_multi_path_fixed_interdiction_weighted_paths.py)
```shell
Shortest paths (multi-path approach) (toy_graph_1, ODs: [(0, 3), (1, 2)]):
	For OD pair (0, 3)
		Edge from 0 to 1 with cost 2
		Edge from 1 to 3 with cost 1
	For OD pair (1, 2)
		Edge from 1 to 3 with cost 1
		Edge from 3 to 2 with cost 1
```
### [shortest_path_multi_path_simple_interdiction_weighted_paths.py](erna%2Foptimization%2Fshortest_path_multi_path_simple_interdiction_weighted_paths.py)
```shell
Shortest paths (multi-path approach) (toy_graph_1, ODs: [(0, 3), (1, 2)]):
	For OD pair (0, 3)
		Edge from 0 to 1 with cost 2
		Edge from 1 to 3 with cost 1
	For OD pair (1, 2)
		Edge from 1 to 3 with cost 1
		Edge from 3 to 2 with cost 1
```
### [stochastic_approximation.py](erna%2Foptimization%2Fstochastic_approximation.py)
```shell
Shortest path (dual formulation | multi-path) (toy_graph_1, ODs: [(0, 3), (1, 2)]):
	For OD pair (0, 3)
for node i: 0.0, node j: 2.0
for node i: 0.0, node j: 3.0
for node i: 2.0, node j: 3.0
for node i: 2.0, node j: 8.0
for node i: 3.0, node j: 8.0
[0, 1, 2, 3] travel time: 17.0
	For OD pair (1, 2)
for node i: 0.0, node j: 10.0
for node i: 0.0, node j: 11.0
[1, 2] travel time: 10.0
Interdictions: {(0, 1): 0.0, (0, 2): 0.0, (1, 2): 0.0, (1, 3): 1.0, (2, 3): 0.0, (3, 2): 0.0}
```
### [STOCHASTIC_shortest_path_multi_path_simple_interdiction_weighted_paths.py](erna%2Foptimization%2FSTOCHASTIC_shortest_path_multi_path_simple_interdiction_weighted_paths.py)

# Creating a New Toy Graph
If you would like to add your own graph to the _erna_ package, you can do so here: `./erna/toy_data`.
Just create a new file and define your graph using the `erna/data/graph.py::Graph` class.
