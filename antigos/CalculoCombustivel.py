import pandas as pd

def calcular_combustivel(planilha_entrada, consumo_km_por_litro, preco_combustivel, planilha_saida):
    # Ler a planilha
    df = pd.read_excel(planilha_entrada)

    # Verificar se a coluna existe
    if "Distância (km)" not in df.columns:
        raise ValueError('A coluna "Distância (km)" não foi encontrada na planilha.')

    # Cálculo do combustível estimado em litros
    df["Combustível estimado (L)"] = df["Distância (km)"] / consumo_km_por_litro

    # Cálculo do custo estimado em reais
    df["Custo estimado (R$)"] = df["Combustível estimado (L)"] * preco_combustivel

    # Salvar nova planilha
    df.to_excel(planilha_saida, index=False)
    print(f"Planilha salva com sucesso em: {planilha_saida}")

# Exemplo de uso
calcular_combustivel(
    planilha_entrada="rotas_com_distancias.v.2.xlsx",
    consumo_km_por_litro=8.0,         # Exemplo: 8 km/l
    preco_combustivel=6.50,           # Exemplo: R$6,50 por litro
    planilha_saida="rotas_com_combustivel.xlsx"
)
