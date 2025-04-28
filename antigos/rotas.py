import pandas as pd
from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Função para calcular matriz de distâncias
def calculate_distance_matrix(locations):
    """
    Calcula a matriz de distâncias entre todos os pontos usando latitude e longitude.
    """
    distance_matrix = []
    item = 1
    for i in range(len(locations)):
        row = []
        for j in range(len(locations)):
            if i == j:
                row.append(0)  # Distância de um ponto para ele mesmo é zero
            else:
                coord_i = (locations[i]['Latitude'], locations[i]['Longitude'])
                coord_j = (locations[j]['Latitude'], locations[j]['Longitude'])
                distance = geodesic(coord_i, coord_j).kilometers
                row.append(distance)
                print(item)
                item +=1
        distance_matrix.append(row)
    return distance_matrix

# Função para resolver o Problema do Caixeiro Viajante (TSP)
def solve_tsp(distance_matrix):
    """
    Resolve o TSP usando OR-Tools e retorna a rota otimizada.
    """
    def distance_callback(from_index, to_index):
        """Retorna a distância entre dois nós."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    # Número de locações
    num_locations = len(distance_matrix)

    # Cria o gerenciador de índices
    manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)

    # Cria o modelo de roteamento
    routing = pywrapcp.RoutingModel(manager)

    # Define a função de custo (distância)
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Define a estratégia de busca
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Resolve o problema
    solution = routing.SolveWithParameters(search_parameters)

    # Extrai a rota otimizada
    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    route.append(manager.IndexToNode(index))  # Adiciona o ponto de retorno ao início
    return route

# Carregar os dados do banco de dados (substitua pela sua conexão real)
df = pd.read_excel("Rotas-Tranche-4-Lote-2.xlsx", sheet_name= "Planilha1" )
#data = {
   # 'idCliente': [1, 2, 3, 4, 5],
  #  'Latitude': [-23.5505, -23.5605, -23.5705, -23.5805, -23.5905],
  #  'Longitude': [-46.6333, -46.6433, -46.6533, -46.6633, -46.6733],
  #  'status': ['Não realizado', 'Realizado', 'Não realizado', 'Não realizado', 'Realizado']
#}
##df = pd.DataFrame(data)

# Filtrar clientes com status "Não realizado"
#clientes_nao_realizados = df[df['status'] == 'Não realizado']

# Preparar lista de locações
locations = df[['Latitude', 'Longitude']].to_dict('records')

# Calcular matriz de distâncias
distance_matrix = calculate_distance_matrix(locations)

# Resolver o TSP
rota_otimizada = solve_tsp(distance_matrix)

# Mapear a rota otimizada para os IDs dos clientes
rota_clientes = df.iloc[rota_otimizada[:-1]]  # Remove o último ponto (volta ao início)

# Adicionar colunas de ordem e local de origem
rota_clientes = rota_clientes.copy()
rota_clientes['OrdemRota'] = range(1, len(rota_clientes) + 1)
rota_clientes['Origem'] = rota_clientes['idCliente'].shift(1)  # O cliente anterior é a origem
rota_clientes.loc[rota_clientes.index[0], 'Origem'] = None  # O primeiro cliente não tem origem

# Salvar os resultados em um arquivo Excel para uso no Power BI
rota_clientes.to_excel('rotas_otimizadas.xlsx', index=False)

print("Rotas otimizadas salvas em 'rotas_otimizadas.xlsx'")