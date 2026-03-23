import streamlit as st
import numpy as np
import altair as alt
import pandas as pd
from math import comb

# =========================
# FUNÇÃO ANALÍTICA
# =========================
def disponibilidade_analitica(n, k, p):
    # Casos especiais (mais eficientes)
    if k == 1:
        return 1 - (1 - p) ** n
    if k == n:
        return p ** n

    return sum(
        comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
        for i in range(k, n + 1)
    )




# =========================
# SIMULAÇÃO
# =========================
def simulacao(n, k, p, rodadas=10000):
    sucessos = 0

    for _ in range(rodadas):
        servidores = np.random.rand(n) <= p
        ativos = np.sum(servidores)

        if ativos >= k:
            sucessos += 1

    return sucessos / rodadas




# =========================
# UI
# =========================
st.title("Disponibilidade em Sistemas Distribuídos (Modelo n, k)")

st.markdown(r"""
### 📌 Disponibilidade do sistema (modelo quorum)

A disponibilidade de um sistema replicado com **n servidores** e quorum **k** é:

$$
A(n,k,p) = \sum_{i=k}^{n} \binom{n}{i} p^i (1 - p)^{n-i}
$$

Onde:
- $n$ = número total de servidores  
- $k$ = mínimo necessário para o sistema funcionar  
- $p$ = probabilidade de um servidor estar ativo  
""")

st.markdown(r"""
### 📊 Casos especiais

#### 🔹 Leitura ($k = 1$)

$$
A = 1 - (1 - p)^n
$$

#### 🔹 Atualização ($k = n$)

$$
A = p^n
$$
""")

st.sidebar.header("Parâmetros")

n = st.sidebar.slider("Número de servidores (n)", 1, 50, 10)
k = st.sidebar.slider("Quórum mínimo (k)", 1, n, 5)
p = st.sidebar.slider("Probabilidade de servidor ativo (p)", 0.0, 1.0, 0.9)

rodadas = st.sidebar.slider("Número de simulações", 1000, 100000, 10000, step=1000)





# =========================
# RESULTADOS
# =========================
analitico = disponibilidade_analitica(n, k, p)
simulado = simulacao(n, k, p, rodadas)

st.subheader("Resultados")

col1, col2 = st.columns(2)
col1.metric("Disponibilidade Analítica", f"{100 * analitico:.3f}%")
col2.metric("Disponibilidade Simulada", f"{100 * simulado:.3f}%")





# =========================
# GRÁFICO 1: p vs disponibilidade
# =========================
st.subheader("Disponibilidade vs p")

p_values = np.linspace(0, 1, 50)

df1 = pd.DataFrame({
    "p": p_values,
    "Disponibilidade": [disponibilidade_analitica(n, k, pv) for pv in p_values]
})

linha = alt.Chart(df1).mark_line().encode(
    x=alt.X("p:Q", title="p"),
    y=alt.Y("Disponibilidade:Q", title="Disponibilidade"),
    tooltip=["p", "Disponibilidade"]
)

ponto_atual = pd.DataFrame({
    "p": [p],
    "Disponibilidade": [analitico]
})

ponto = alt.Chart(ponto_atual).mark_point(size=100).encode(
    x="p:Q",
    y="Disponibilidade:Q",
    tooltip=["p", "Disponibilidade"]
)

chart1 = (linha + ponto).interactive()

st.altair_chart(chart1, use_container_width=True)




# =========================
# GRÁFICO 2: comparação k
# =========================
st.subheader("Comparação para diferentes k")

k_values = [1, max(1, n//2), n]
labels = ["k=1", "k=n/2", "k=n"]

data = []

for kv, label in zip(k_values, labels):
    for pv in p_values:
        data.append({
            "p": pv,
            "Disponibilidade": disponibilidade_analitica(n, kv, pv),
            "Caso": label
        })

df2 = pd.DataFrame(data)

chart2 = alt.Chart(df2).mark_line().encode(
    x=alt.X("p:Q", title="p"),
    y=alt.Y("Disponibilidade:Q", title="Disponibilidade"),
    color="Caso:N",
    tooltip=["p", "Disponibilidade", "Caso"]
).interactive()

st.altair_chart(chart2, use_container_width=True)




# =========================
# INTERPRETAÇÃO
# =========================
st.subheader("Interpretação")

st.markdown(f"""
- **k = 1** → Alta disponibilidade (qualquer servidor ativo já mantém o sistema)
- **k = {n}** → Baixa disponibilidade (todos precisam estar ativos)
- **k = {n//2}** → Equilíbrio entre disponibilidade e consistência
""")