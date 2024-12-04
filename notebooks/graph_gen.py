import os
from pathlib import Path
import geopandas as gpd
import igraph as ig
from tqdm import tqdm
from erna.graph_generation.problem_graph_generator import ProblemGraphGenerator
from erna.graph_generation.utils.osm_utils import get_pois_gdf

BASE_PATH = Path('/Users/hanyongxu/Dropbox (MIT)/2024Fall/6.C57_optimization/FinalProject/15.C57-final-project/data/Boston')
city = "Boston"
country = "US"
osm_poi_tags = {'amenity':'school'}
poi_file = BASE_PATH / "boston_pois.geojson"
gtfs_file = BASE_PATH / "mbta_transit_feed.zip"
crs = "EPSG:4326"


if __name__ == "__main__":
    poi_gdf = get_pois_gdf(', '.join([city, country]), osm_poi_tags)
    gdf = gpd.read_parquet(BASE_PATH / 'complete_census_2022.parquet')
    gdf = gdf.to_crs(crs)

    columns_to_keep = [
        'GEOID20',
        'TOWN',
        'MBTA Community Type',
        'Households:',
        'Households: Less than $25,000',
        'Households: $25,000 to $49,999',
        'Households: $50,000 to $74,999',
        'Households: $75,000 to $99,999',
        'Households: $100,000 or More',
        'Total Population',
        'Total Population: Male',
        'Total Population: Male: Under 18 Years',
        'Total Population: Male: 18 to 34 Years',
        'Total Population: Male: 35 to 64 Years',
        'Total Population: Male: 65 Years and Over',
        'Total Population: Female',
        'Total Population: Female: Under 18 Years',
        'Total Population: Female: 18 to 34 Years',
        'Total Population: Female: 35 to 64 Years',
        'Total Population: Female: 65 Years and Over',
        'Total Population: Hispanic or Latino',
        'Total Population: Not Hispanic or Latino',
        'Total Population: Not Hispanic or Latino: White Alone',
        'Total Population: Not Hispanic or Latino: Black or African American Alone',
        'Total Population: Not Hispanic or Latino: American Indian and Alaska Native Alone',
        'Total Population: Not Hispanic or Latino: Asian Alone',
        'Total Population: Not Hispanic or Latino: Native Hawaiian and Other Pacific Islander Alone',
        'Total Population: Not Hispanic or Latino: Some Other Race Alone',
        'Total Population: Not Hispanic or Latino: Two or More Races',
        'Workers 16 Years and Over:',
        'Workers 16 Years and Over: Car, Truck, or Van',
        'Workers 16 Years and Over: Drove Alone',
        'Workers 16 Years and Over: Public Transportation (Includes Taxicab)',
        'Workers 16 Years and Over: Motorcycle',
        'Workers 16 Years and Over: Bicycle',
        'Workers 16 Years and Over: Walked',
        'Workers 16 Years and Over: Other Means',
        'Workers 16 Years and Over: Worked At Home',
        'Occupied Housing Units: No Vehicle Available',
        'Occupied Housing Units: 1 Vehicle Available',
        'Occupied Housing Units: 2 Vehicles Available', 'Area Total:',
        'Area (Land)',
        'Area (Water)',
        'Population Density (Per Sq. Mile)',
        'Median Household Income (In 2022 Inflation Adjusted Dollars)',
        'res_centroid'
   ]

    res_centroids_gdf = gdf[columns_to_keep].copy()
    res_centroids_gdf = res_centroids_gdf.rename(columns={'res_centroid': 'geometry', 'TOWN': 'name'})
    res_centroids_gdf['name'] = res_centroids_gdf['name'].str.title() + ' (' + res_centroids_gdf['GEOID20'] + ')'
    res_centroids_gdf = gpd.GeoDataFrame(res_centroids_gdf, geometry='geometry', crs=crs)

    gtfs_zip_file_path = BASE_PATH / gtfs_file
    out_dir_path = BASE_PATH / 'resulting_graph/'

    if not os.path.exists(out_dir_path):
        os.mkdir(out_dir_path)

    day = "monday"
    time_from = "07:00:00"
    time_to = "09:00:00"

    graph_generator = ProblemGraphGenerator(city=city, gtfs_zip_file_path=gtfs_zip_file_path,
                                            out_dir_path=out_dir_path, day=day,
                                            time_from=time_from, time_to=time_to,
                                            poi_gdf=res_centroids_gdf, res_centroids_gdf=res_centroids_gdf,
                                            geographical_neighborhoods_gdf=gdf,
                                            clip_graph_to_neighborhoods=False,
                                            distances_computation_mode='haversine',
                                            max_walking_travel_time=15)

    resulting_graph_file = graph_generator.generate_problem_graph()

    # Load the resulting graph
    g = ig.read(resulting_graph_file)

    # Filter edges with 'type' = 'METRO'
    metro_edges = g.es.select(type='METRO')

    # Create a subgraph with only 'METRO' edges
    metro_subgraph = g.subgraph_edges(metro_edges, delete_vertices=True)

    # Get the indices of vertices in the metro_subgraph
    metro_subgraph_vertex_indices = set(
        metro_subgraph.vs['name'] if 'name' in metro_subgraph.vs.attributes() else metro_subgraph.vs.indices)

    # Identify vertices to remove
    vertices_to_remove = []
    for v in tqdm(g.vs.select(type_in=['rc_node', 'poi_node'])):
        # Check if the vertex has a 'walk' edge to any 'pt_node' that is also in the metro_subgraph
        has_valid_edge = any(
            g.es[e]['type'] == 'walk' and
            g.vs[neighbor]['type'] == 'pt_node' and
            g.vs[neighbor]['name'] in metro_subgraph_vertex_indices
            for e in g.incident(v, mode="all")
            for neighbor in g.neighbors(v, mode="all")
        )
        if not has_valid_edge:
            vertices_to_remove.append(v.index)

    # Remove the vertices
    g.delete_vertices(vertices_to_remove)

    # Modify the file name to include '_reduced'
    reduced_file = resulting_graph_file.with_stem(resulting_graph_file.stem + '_reduced_15min')

    # Save the resulting graph
    ig.write(g, str(reduced_file))
