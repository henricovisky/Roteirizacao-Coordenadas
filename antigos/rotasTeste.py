import pandas as pd 
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def calculate_distance_matrix(locations):
    distance_matrix = []
    for i in range(len(locations)):
        row = []
        for j in range(len(locations)):
            if i == j:
                row.append(0)
            else:
                coord_i = (locations[i]['Latitude'], locations[i]['Longitude'])
                coord_j = (locations[j]['Latitude'], locations[j]['Longitude'])
                distance = geodesic(coord_i, coord_j).kilometers
                row.append(distance)
        distance_matrix.append(row)
    return distance_matrix

def solve_tsp(distance_matrix):
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node] * 1000)  # OR-Tools espera inteiros

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
        route.append(manager.IndexToNode(index))
        return route
    else:
        return list(range(num_locations))  # fallback caso não encontre solução

# --- INÍCIO DO SCRIPT PRINCIPAL ---

df = pd.read_excel("Rotas-Tranche-4-Lote-2.xlsx", sheet_name="Planilha1")

rotas_gerais = []

for localidade, grupo in df.groupby("Localidade"):
    grupo = grupo.reset_index(drop=True)
    locations = grupo[['Latitude', 'Longitude']].to_dict('records')
    distance_matrix = calculate_distance_matrix(locations)
    rota_otimizada = solve_tsp(distance_matrix)

    rota_clientes = grupo.iloc[rota_otimizada[:-1]].copy()
    rota_clientes['OrdemRota'] = range(1, len(rota_clientes) + 1)
    rota_clientes['Origem'] = rota_clientes['idCliente'].shift(1)
    rota_clientes.loc[rota_clientes.index[0], 'Origem'] = None
    rota_clientes['Localidade'] = localidade  # para manter a info agrupada

    rotas_gerais.append(rota_clientes)

# Concatenar todas as rotas por localidade
rotas_finais = pd.concat(rotas_gerais, ignore_index=True)

# Salvar no Excel
rotas_finais.to_excel('rotas_otimizadas_por_localidade.xlsx', index=False)

print("Rotas por localidade salvas em 'rotas_otimizadas_por_localidade.xlsx'")
