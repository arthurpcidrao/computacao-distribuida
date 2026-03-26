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
# CÁLCULO DE N MÍNIMO
# =========================
def calcular_n_minimo(k, p, A_alvo, max_n=10000):
    """Retorna o menor n >= k tal que a disponibilidade analítica >= A_alvo.
    Retorna None se não for encontrado dentro de max_n."""
    if p <= 0:
        return None
    for n in range(k, max_n + 1):
        if disponibilidade_analitica(n, k, p) >= A_alvo:
            return n
    return None




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




# =========================
# SEÇÃO EXTRA: CÁLCULO DE N
# =========================
st.divider()
st.header("🔢 Calculadora de N mínimo")
st.markdown("""
Dado um nível de disponibilidade desejado, um quórum **k** e a probabilidade individual **p**,
esta seção calcula o **número mínimo de servidores (n)** necessário para atingir essa disponibilidade.
""")

col_n1, col_n2, col_n3 = st.columns(3)
p_n = col_n1.number_input("Probabilidade de servidor ativo (p)", min_value=0.001, max_value=1.0, value=0.9, step=0.001, format="%.3f", key="p_n")
k_n = col_n2.number_input("Quórum mínimo (k)", min_value=1, value=1, step=1, key="k_n")
A_alvo = col_n3.number_input("Disponibilidade alvo", min_value=0.0, max_value=0.999999999, value=0.99, step=0.001, format="%.9f", key="A_alvo")

n_calculado = calcular_n_minimo(int(k_n), p_n, A_alvo)

if n_calculado is None:
    st.error("Não foi possível encontrar um N viável (até 10.000 servidores). Tente reduzir a disponibilidade alvo ou aumentar p.")
else:
    disp_real = disponibilidade_analitica(n_calculado, int(k_n), p_n)
    st.success(f"Para p = {p_n}, k = {int(k_n)} e disponibilidade ≥ {A_alvo:.9g}:  **N mínimo = {n_calculado}** (disponibilidade real: {disp_real:.9f})")

st.subheader("Tabela padrão: p = 0.5, k = 1")
st.markdown("Número mínimo de servidores necessário para atingir cada nível de disponibilidade com p = 0.5 e k = 1.")

alvos_padrao = [0.9, 0.99, 0.999, 0.9999, 0.99999, 0.999999]
linhas = []
for alvo in alvos_padrao:
    n_min = calcular_n_minimo(1, 0.5, alvo)
    disp = disponibilidade_analitica(n_min, 1, 0.5) if n_min else None
    linhas.append({
        "Disponibilidade alvo": f"{alvo}",
        "N mínimo": n_min if n_min else "—",
        "Disponibilidade real": f"{disp:.9f}" if disp else "—",
    })

df_n = pd.DataFrame(linhas)
st.dataframe(df_n, use_container_width=True, hide_index=True)