#!/usr/bin/env python3
"""
Script para gerar 4 gráficos a partir dos CSVs dos testes Locust.

Gráficos:
1. P95 por quantidade de usuários (4 barras: python+redis, python-redis, ruby+redis, ruby-redis)
2. Taxa de falha por quantidade de usuários (mesma estrutura)
3. P95 com Redis apenas (2 barras: python, ruby)
4. P95 sem Redis apenas (2 barras: python, ruby)
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Configurar estilo
plt.style.use('seaborn-v0_8-darkgrid')
colors = ['#2ecc71', '#e74c3c', '#3498db', '#f39c12']  # Verde, Vermelho, Azul, Laranja

# Quantidade de usuários
users = [50, 200, 300]

# Dicionário para armazenar dados
data = {
    'python_redis': {'p95': [], 'failures': []},
    'python_noredis': {'p95': [], 'failures': []},
    'ruby_redis': {'p95': [], 'failures': []},
    'ruby_noredis': {'p95': [], 'failures': []},
}

# Ler CSVs
results_dir = 'locust/results'

for user_count in users:
    files = {
        'python_redis': f'{results_dir}/python_redis_{user_count}users_stats.csv',
        'python_noredis': f'{results_dir}/python_noredis_{user_count}users_stats.csv',
        'ruby_redis': f'{results_dir}/ruby_redis_{user_count}users_stats.csv',
        'ruby_noredis': f'{results_dir}/ruby_noredis_{user_count}users_stats.csv',
    }
    
    for config, filepath in files.items():
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            # P95 está na penúltima coluna antes do final
            p95_value = float(df.iloc[0, df.columns.get_loc('95%')])
            failures = int(df.iloc[0]['Failure Count'])
            total_requests = int(df.iloc[0]['Request Count'])
            failure_rate = (failures / total_requests * 100) if total_requests > 0 else 0
            
            data[config]['p95'].append(p95_value)
            data[config]['failures'].append(failure_rate)
        else:
            print(f"⚠️ Arquivo não encontrado: {filepath}")
            data[config]['p95'].append(0)
            data[config]['failures'].append(0)

# ============ GRÁFICO 1: P95 por Usuários (4 barras) ============
fig, ax = plt.subplots(figsize=(12, 6))

x = range(len(users))
width = 0.2

bars1 = ax.bar([i - 1.5*width for i in x], data['python_redis']['p95'], width, label='Python + Redis', color=colors[0])
bars2 = ax.bar([i - 0.5*width for i in x], data['python_noredis']['p95'], width, label='Python sem Redis', color=colors[1])
bars3 = ax.bar([i + 0.5*width for i in x], data['ruby_redis']['p95'], width, label='Ruby + Redis', color=colors[2])
bars4 = ax.bar([i + 1.5*width for i in x], data['ruby_noredis']['p95'], width, label='Ruby sem Redis', color=colors[3])

ax.set_xlabel('Quantidade de Usuários', fontsize=12, fontweight='bold')
ax.set_ylabel('P95 (ms)', fontsize=12, fontweight='bold')
ax.set_title('P95 por Quantidade de Usuários - Todos os Cenários', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(users)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('chart_1_p95_all.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 1 salvo: chart_1_p95_all.png")
plt.close()

# ============ GRÁFICO 2: Taxa de Falha por Usuários (4 barras) ============
fig, ax = plt.subplots(figsize=(12, 6))

bars1 = ax.bar([i - 1.5*width for i in x], data['python_redis']['failures'], width, label='Python + Redis', color=colors[0])
bars2 = ax.bar([i - 0.5*width for i in x], data['python_noredis']['failures'], width, label='Python sem Redis', color=colors[1])
bars3 = ax.bar([i + 0.5*width for i in x], data['ruby_redis']['failures'], width, label='Ruby + Redis', color=colors[2])
bars4 = ax.bar([i + 1.5*width for i in x], data['ruby_noredis']['failures'], width, label='Ruby sem Redis', color=colors[3])

ax.set_xlabel('Quantidade de Usuários', fontsize=12, fontweight='bold')
ax.set_ylabel('Taxa de Falha (%)', fontsize=12, fontweight='bold')
ax.set_title('Taxa de Falha por Quantidade de Usuários - Todos os Cenários', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(users)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('chart_2_failures_all.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 2 salvo: chart_2_failures_all.png")
plt.close()

# ============ GRÁFICO 3: P95 COM Redis (2 barras) ============
fig, ax = plt.subplots(figsize=(10, 6))

width = 0.35

bars1 = ax.bar([i - width/2 for i in x], data['python_redis']['p95'], width, label='Python + Redis', color=colors[0])
bars2 = ax.bar([i + width/2 for i in x], data['ruby_redis']['p95'], width, label='Ruby + Redis', color=colors[2])

ax.set_xlabel('Quantidade de Usuários', fontsize=12, fontweight='bold')
ax.set_ylabel('P95 (ms)', fontsize=12, fontweight='bold')
ax.set_title('P95 com Redis - Python vs Ruby', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(users)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('chart_3_p95_with_redis.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 3 salvo: chart_3_p95_with_redis.png")
plt.close()

# ============ GRÁFICO 4: P95 SEM Redis (2 barras) ============
fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar([i - width/2 for i in x], data['python_noredis']['p95'], width, label='Python sem Redis', color=colors[1])
bars2 = ax.bar([i + width/2 for i in x], data['ruby_noredis']['p95'], width, label='Ruby sem Redis', color=colors[3])

ax.set_xlabel('Quantidade de Usuários', fontsize=12, fontweight='bold')
ax.set_ylabel('P95 (ms)', fontsize=12, fontweight='bold')
ax.set_title('P95 sem Redis - Python vs Ruby', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(users)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('chart_4_p95_without_redis.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico 4 salvo: chart_4_p95_without_redis.png")
plt.close()

print("")
print("✅ Todos os gráficos gerados com sucesso!")
print("")
print("Arquivos gerados:")
print("  - chart_1_p95_all.png")
print("  - chart_2_failures_all.png")
print("  - chart_3_p95_with_redis.png")
print("  - chart_4_p95_without_redis.png")
