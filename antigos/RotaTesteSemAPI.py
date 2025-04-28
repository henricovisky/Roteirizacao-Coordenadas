import pandas as pd 
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import googlemaps
import time

# Substitua pela sua chave da API do Google Maps
API_KEY = 'AIzaSyA0ddDAKR-YDFI9xXSPSJO7W0C0i8TpeCE'
gmaps = googlemaps.Client(key=API_KEY)

# Função para calcular a matriz de distâncias usando coordenadas geográficas
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

# Função para resolver o TSP com OR-Tools
def solve_tsp(distance_matrix):
    def distance_callback(from_index, to_index):
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

# Função para obter tempo e distância via Google Directions API
def get_directions_duration_distance(origem, destino):
    try:
        response = gmaps.directions(origem, destino, mode='driving')
        if response and len(response) > 0:
            leg = response[0]['legs'][0]
            duracao_min = leg['duration']['value'] / 60  # segundos para minutos
            distancia_km = leg['distance']['value'] / 1000  # metros para km
            return duracao_min, distancia_km
    except Exception as e:
        print(f"Erro ao chamar Directions API: {e}")
    return None, None

# --- INÍCIO DO SCRIPT PRINCIPAL ---

df = pd.read_excel("Rotas-Tranche-4-Lote-2.xlsx", sheet_name="Planilha1")
rotas_gerais = []

# Geração da rota por localidade
for localidade, grupo in df.groupby("Localidade"):
    grupo = grupo.reset_index(drop=True)
    locations = grupo[['Latitude', 'Longitude']].to_dict('records')
    distance_matrix = calculate_distance_matrix(locations)
    rota_otimizada = solve_tsp(distance_matrix)

    rota_clientes = grupo.iloc[rota_otimizada[:-1]].copy()  # Remove retorno ao início
    rota_clientes['OrdemRota'] = range(1, len(rota_clientes) + 1)
    rota_clientes['Origem'] = rota_clientes['idCliente'].shift(1)
    rota_clientes.loc[rota_clientes.index[0], 'Origem'] = None
    rota_clientes['Localidade'] = localidade

    # Adiciona colunas para duração e distância
    duracoes = []
    distancias = []

    for i in range(len(rota_clientes)):
        if i == 0:
            duracoes.append(None)
            distancias.append(None)
        else:
            origem = f"{rota_clientes.iloc[i - 1]['Latitude']},{rota_clientes.iloc[i - 1]['Longitude']}"
            destino = f"{rota_clientes.iloc[i]['Latitude']},{rota_clientes.iloc[i]['Longitude']}"
            dur, dist = get_directions_duration_distance(origem, destino)
            duracoes.append(dur)
            distancias.append(dist)
            time.sleep(1)  # Evita exceder o limite da API

    rota_clientes['Duração (min)'] = duracoes
    rota_clientes['Distância (km)'] = distancias

    # Conversão e arredondamento
    rota_clientes['Duração (min)'] = rota_clientes['Duração (min)'].apply(lambda x: int(round(x)) if pd.notnull(x) else None)
    rota_clientes['Distância (km)'] = rota_clientes['Distância (km)'].apply(lambda x: round(float(x), 2) if pd.notnull(x) else None)

    rotas_gerais.append(rota_clientes)

# Concatenar todas as rotas e salvar em Excel
rotas_finais = pd.concat(rotas_gerais, ignore_index=True)
rotas_finais.to_excel('testando.xlsx', index=False)

print("testando.xlsx'")
