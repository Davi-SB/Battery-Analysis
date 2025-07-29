import numpy as np
from pysr import PySRRegressor
import matplotlib.pyplot as plt

# Criar e preparar os dados
np.random.seed(10)
X = np.random.rand(150, 1) * 10

# y = 2.5 * cos(x) * exp(x/3) + x/2 + ruido
y = 2.5 * np.cos(X.flatten()) * np.exp(-X.flatten() / 3) + X.flatten()/2 + (np.random.randn(150) * 0.1)

# Instanciar e configurar o PySRRegressor
model = PySRRegressor(
    niterations=50,
    populations=30,
    binary_operators=["+", "-", "*", "/", "pow"],
    unary_operators=["cos", "exp", "sin"],
    constraints={'^': (-1, 1), 'pow': (-1, 1)},
    complexity_of_operators={"exp": 2, "cos": 2},
    model_selection="best",
    verbosity=0
)

# Treinar o modelo
print("Iniciando o treinamento do PySR... isso pode levar alguns minutos.")
model.fit(X, y, variable_names=["x"])
print("Treinamento completo.")


# Exibir a tabela de resultados
print(" Resultados do Modelo")
print("A tabela abaixo mostra as melhores equações encontradas, balanceando complexidade e perda.")
print(model)

# Imprimir a equação final escolhida (Modificação)
# Pega a melhor equação encontrada pelo critério de 'score'
final_equation_details = model.get_best()

# Imprime a equação final de forma destacada
print("\n" + "="*50)
print("Equação Final Escolhida")
print(f"   Score de complexidade/perda: {final_equation_details['score']:.4f}")
print(f"   y = {final_equation_details['equation']}")
print("="*50 + "\n")


# Visualizar os Resultados
print("Gerando o gráfico...")
plt.figure(figsize=(12, 7))
plt.scatter(X.flatten(), y, s=20, label='Dados Originais', color='blue', alpha=0.7)
X_plot = np.linspace(X.min(), X.max(), 500).reshape(-1, 1)
y_plot = model.predict(X_plot)

# Usa a string da equação final na legenda do gráfico
plt.plot(X_plot.flatten(), y_plot, label=f'Previsão do PySR: y = {final_equation_details["equation"]}', color='red', linewidth=3)
plt.title('PySR: Dados Originais vs. Função Prevista', fontsize=16)
plt.xlabel('Entrada (x)', fontsize=12)
plt.ylabel('Saída (y)', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()