import pandas as pd
from modules.route_optimizer import RouteOptimizer

optimizer = RouteOptimizer()  # No average speed parameter needed
df = pd.read_excel("Rotas Tranche 4 - Lote 2.xlsx")
all_routes = []

for localidade, grupo in df.groupby("Localidade"):
    optimized_route = optimizer.optimize_route(grupo.reset_index(drop=True), localidade)
    all_routes.append(optimized_route)

final_routes = pd.concat(all_routes, ignore_index=True)
final_routes.to_excel('Roteirização_clientes.xlsx', index=False)