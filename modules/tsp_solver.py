from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class TSPSolver:
    """
    Resolve o Problema do Caixeiro Viajante (TSP) usando OR-Tools.
    """
    def solve_tsp(self, distance_matrix):
        """
        Resolve o TSP para encontrar a rota otimizada.

        Args:
            distance_matrix (list): Matriz de distâncias entre as localizações.

        Returns:
            list: Rota otimizada como uma lista de índices.
        """
        def distance_callback(from_index, to_index):
            """Retorna a distância entre os nós."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node] * 1000)  # distância em metros

        num_locations = len(distance_matrix)
        manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            route = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))  # Volta ao início
            return route
        else:
            return list(range(num_locations))  # Caso não consiga resolver