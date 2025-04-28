import pandas as pd
from modules.distance_calculator import DistanceCalculator
from modules.tsp_solver import TSPSolver

class RouteOptimizer:
    def __init__(self):
        self.distance_calculator = DistanceCalculator()
        self.tsp_solver = TSPSolver()

    def optimize_route(self, dataframe, localidade):
        locations = dataframe[['Latitude', 'Longitude']].to_dict('records')
        distance_matrix = self.distance_calculator.calculate_distance_matrix(locations)
        optimized_route = self.tsp_solver.solve_tsp(distance_matrix)
        route_df = dataframe.iloc[optimized_route[:-1]].copy()
        route_df['OrdemRota'] = range(1, len(route_df) + 1)
        route_df['Origem'] = route_df['idCliente'].shift(1)
        route_df.loc[route_df.index[0], 'Origem'] = None
        route_df['Localidade'] = localidade

        # Calculate and add distance
        for i in range(1, len(route_df)):
            distance = distance_matrix[optimized_route[i-1]][optimized_route[i]]
            route_df.loc[route_df.index[i], 'Distância (km)'] = round(float(distance), 2)

        return route_df