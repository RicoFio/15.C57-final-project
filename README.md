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

# Working with real-world data
This repository includes a fully-fledged problem graph generation script that can be used to generate a graph from real-world data. Here, you will need some form of census (optimally the ACS in the US) and a GTFS of the transit authority that is operative in the area of study. The OSMNX graph is automatically downloaded, and we can also automatically generate data on the points of interest using OSMNX. To understand how to generate data, have a look at `./notebooks/graph_gen.py`. The script uses the tools provided by the `erna` package.

We already generated the problem graph for Boston and its MBTA metro network. A sample of the data dict available for each residential centroid is:

```python
{
    'id': 2995.0,
    'x': -70.9886912,
    'y': 42.2583235,
    'uniqueagencyid': 'None',
    'routetype': nan,
    'stopid': 'None',
    'name': 'Quincy (250214177022)',
    'color': 'red',
    'type': 'rc_node',
    'MBTACommunityType': 'subway or light rail',
    'Households': 385.0,
    'HouseholdsLessthan25000': 120.0,
    'Households25000to49999': 12.0,
    'Households50000to74999': 74.0,
    'Households75000to99999': 35.0,
    'Households100000orMore': 144.0,
    'TotalPopulation': 1017.0,
    'TotalPopulationMale': 481.0,
    'TotalPopulationMaleUnder18Years': 45.0,
    'TotalPopulationMale18to34Years': 218.0,
    'TotalPopulationMale35to64Years': 167.0,
    'TotalPopulationMale65YearsandOver': 51.0,
    'TotalPopulationFemale': 536.0,
    'TotalPopulationFemaleUnder18Years': 37.0,
    'TotalPopulationFemale18to34Years': 201.0,
    'TotalPopulationFemale35to64Years': 259.0,
    'TotalPopulationFemale65YearsandOver': 39.0,
    'TotalPopulationHispanicorLatino': 136.0,
    'TotalPopulationNotHispanicorLatino': 881.0,
    'TotalPopulationNotHispanicorLatinoWhiteAlone': 641.0,
    'TotalPopulationNotHispanicorLatinoBlackorAfricanAmericanAlone': 53.0,
    'TotalPopulationNotHispanicorLatinoAmericanIndianandAlaskaNativeAlone': 0.0,
    'TotalPopulationNotHispanicorLatinoAsianAlone': 168.0,
    'TotalPopulationNotHispanicorLatinoNativeHawaiianandOtherPacificIslanderAlone': 0.0,
    'TotalPopulationNotHispanicorLatinoSomeOtherRaceAlone': 6.0,
    'TotalPopulationNotHispanicorLatinoTwoorMoreRaces': 13.0,
    'Workers16YearsandOver': 609.0,
    'Workers16YearsandOverCarTruckorVan': 379.0,
    'Workers16YearsandOverDroveAlone': 247.0,
    'Workers16YearsandOverPublicTransportationIncludesTaxicab': 143.0,
    'Workers16YearsandOverMotorcycle': 0.0,
    'Workers16YearsandOverBicycle': 20.0,
    'Workers16YearsandOverWalked': 47.0,
    'Workers16YearsandOverOtherMeans': 8.0,
    'Workers16YearsandOverWorkedAtHome': 12.0,
    'OccupiedHousingUnitsNoVehicleAvailable': 41.0,
    'OccupiedHousingUnits1VehicleAvailable': 195.0,
    'OccupiedHousingUnits2VehiclesAvailable': 103.0,
    'AreaTotal': 0.4208128,
    'AreaLand': 896706.0,
    'AreaWater': 193194.0,
    'PopulationDensityPerSqMile': 2937.438,
    'MedianHouseholdIncomeIn2022InflationAdjustedDollars': 63917.0,
 }
```

In general, the graph can be subdivided into the following subgraphs:

- **Residential Centroids (`rc_node`):** These are the nodes that represent the residential areas in the city. They are connected to transit stops and points of interests by an edge of type `walking`. The maximum travel time by walk is `45 minutes`.
- **Public Transit Stops (`pt_node`):** These are the nodes that represent the transit stops in the city. They are connected to the nearest residential centroid by an edge of type `walking`.
- **Points of Interest (`poi_node`):** These are the nodes that represent the points of interest in the city (i.e. LODES work locations which are equivalent to the rc_nodes). They are connected to the nearest public transit station by an edge of type `walking`.

Thus, there are walking edges between RC nodes and PT nodes, between PT nodes and POI nodes, and between RC and POI nodes. The walking edges are weighted by the walking time between the two nodes. The walking time is calculated using the Haversine formula or through OSMNX routing.