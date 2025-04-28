import pandas as pd
from geopy.distance import geodesic

# Lê a planilha com a ordem já definida
df = pd.read_excel("rotas_otimizadas_detalhadas.xlsx")

# Garante que os dados estejam ordenados corretamente por localidade e ordem da rota
df = df.sort_values(by=["Localidade", "OrdemRota"]).reset_index(drop=True)

# Lista para armazenar as distâncias
distancias = []

# Itera pelas linhas para calcular a distância entre o ponto atual e o anterior
for i in range(len(df)):
    if i == 0 or df.loc[i, 'Localidade'] != df.loc[i - 1, 'Localidade']:
        distancias.append(None)  # Primeiro ponto da localidade
    else:
        coord_origem = (df.loc[i - 1, 'Latitude'], df.loc[i - 1, 'Longitude'])
        coord_destino = (df.loc[i, 'Latitude'], df.loc[i, 'Longitude'])
        distancia_km = geodesic(coord_origem, coord_destino).kilometers
        distancias.append(round(distancia_km, 2))

# Adiciona a nova coluna ao DataFrame
df['Distância (km)'] = distancias

# Salva o novo arquivo
df.to_excel("rotas_com_distancias.xlsx", index=False)

print("Planilha atualizada salva como 'rotas_com_distancias.xlsx'")
