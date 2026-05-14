#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Configurar estilo
plt.style.use('seaborn-v0_8-darkgrid')
colors = ['#2ecc71', '#e74c3c', '#3498db', '#f39c12']

def _annotate_bars(ax, bars, fmt="{:.0f}", fontsize=9, color='black'):
    # Recalcula limites e define deslocamento proporcional ao eixo Y
    ax.relim()
    ax.autoscale_view()
    ylim = ax.get_ylim()
    y_offset = (ylim[1] - ylim[0]) * 0.02 if (ylim[1] - ylim[0]) > 0 else 1

    for bar in bars:
        h = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2
        text = fmt.format(h)
        ax.annotate(text,
                    xy=(x, h),
                    xytext=(x, h + y_offset),
                    textcoords='data',
                    ha='center', va='bottom', fontsize=fontsize,
                    bbox=dict(facecolor=color, edgecolor='none', alpha=0.85))

# Quantidade de usuários
users = ["5", "30", "80"]
categ_user = ["baixo", "medio", "alto"]
data = {
    'python_redis': {'p95': [], 'failures': []},
    'python_noredis': {'p95': [], 'failures': []},
    'ruby_redis': {'p95': [], 'failures': []},
    'ruby_noredis': {'p95': [], 'failures': []},
}
results_dir = 'locust/results'

for user_count in categ_user:
    files = {
        'python_redis': f'{results_dir}/python_redis_{user_count}_users_stats.csv',
        'python_noredis': f'{results_dir}/python_noredis_{user_count}_users_stats.csv',
        'ruby_redis': f'{results_dir}/ruby_redis_{user_count}_users_stats.csv',
        'ruby_noredis': f'{results_dir}/ruby_noredis_{user_count}_users_stats.csv',
    }
    for config, filepath in files.items():
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            # Locust csv files often have "Aggregated" as the last line or specific columns
            # We want the '95%' column for the 'Aggregated' row (usually the last row)
            agg_row = df[df['Name'] == 'Aggregated']
            if not agg_row.empty:
                p95_value = float(agg_row['95%'].values[0])
                failures = int(agg_row['Failure Count'].values[0])
                total_requests = int(agg_row['Request Count'].values[0])
                failure_rate = (failures / total_requests * 100) if total_requests > 0 else 0
                data[config]['p95'].append(p95_value)
                data[config]['failures'].append(failure_rate)
            else:
                data[config]['p95'].append(0)
                data[config]['failures'].append(0)
        else:
            print(f"⚠️ Arquivo não encontrado: {filepath}")
            data[config]['p95'].append(0)
            data[config]['failures'].append(0)

# GRÁFICO 1
fig, ax = plt.subplots(figsize=(12, 6))
x = list(range(len(users)))
width = 0.2
bars1 = ax.bar([i - 1.5*width for i in x], data['python_redis']['p95'], width, label='Python + Redis', color=colors[0])
bars2 = ax.bar([i - 0.5*width for i in x], data['python_noredis']['p95'], width, label='Python sem Redis', color=colors[1])
bars3 = ax.bar([i + 0.5*width for i in x], data['ruby_redis']['p95'], width, label='Ruby + Redis', color=colors[2])
bars4 = ax.bar([i + 1.5*width for i in x], data['ruby_noredis']['p95'], width, label='Ruby sem Redis', color=colors[3])
ax.set_ylabel('P95 (ms)')
ax.set_title('P95 por Usuários')
ax.set_xticks(x)
ax.set_xticklabels(users)
ax.legend()
_annotate_bars(ax, bars1, color=colors[0])
_annotate_bars(ax, bars2, color=colors[1])
_annotate_bars(ax, bars3, color=colors[2])
_annotate_bars(ax, bars4, color=colors[3])
plt.savefig('chart_1_p95_all.png')
plt.close()

# GRÁFICO 2
fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar([i - 1.5*width for i in x], data['python_redis']['failures'], width, label='Python + Redis', color=colors[0])
bars2 = ax.bar([i - 0.5*width for i in x], data['python_noredis']['failures'], width, label='Python sem Redis', color=colors[1])
bars3 = ax.bar([i + 0.5*width for i in x], data['ruby_redis']['failures'], width, label='Ruby + Redis', color=colors[2])
bars4 = ax.bar([i + 1.5*width for i in x], data['ruby_noredis']['failures'], width, label='Ruby sem Redis', color=colors[3])
ax.set_ylabel('Taxa de Falha (%)')
ax.set_title('Taxa de Falha por Usuários')
ax.set_xticks(x)
ax.set_xticklabels(users)
ax.legend()
_annotate_bars(ax, bars1, fmt="{:.1f}%", color=colors[0])
_annotate_bars(ax, bars2, fmt="{:.1f}%", color=colors[1])
_annotate_bars(ax, bars3, fmt="{:.1f}%", color=colors[2])
_annotate_bars(ax, bars4, fmt="{:.1f}%", color=colors[3])
plt.savefig('chart_2_failures_all.png')
plt.close()

# GRÁFICO 3
fig, ax = plt.subplots(figsize=(10, 6))
width_2 = 0.35
bars1 = ax.bar([i - width_2/2 for i in x], data['python_redis']['p95'], width_2, label='Python + Redis', color=colors[0])
bars2 = ax.bar([i + width_2/2 for i in x], data['ruby_redis']['p95'], width_2, label='Ruby + Redis', color=colors[2])
ax.set_ylabel('P95 (ms)')
ax.set_title('P95 com Redis')
ax.set_xticks(x)
ax.set_xticklabels(users)
ax.legend()
_annotate_bars(ax, bars1, color=colors[0])
_annotate_bars(ax, bars2, color=colors[2])
plt.savefig('chart_3_p95_with_redis.png')
plt.close()

# GRÁFICO 4
fig, ax = plt.subplots(figsize=(10, 6))
bars1 = ax.bar([i - width_2/2 for i in x], data['python_noredis']['p95'], width_2, label='Python sem Redis', color=colors[1])
bars2 = ax.bar([i + width_2/2 for i in x], data['ruby_noredis']['p95'], width_2, label='Ruby sem Redis', color=colors[3])
ax.set_ylabel('P95 (ms)')
ax.set_title('P95 sem Redis')
ax.set_xticks(x)
ax.set_xticklabels(users)
ax.legend()
_annotate_bars(ax, bars1, color=colors[1])
_annotate_bars(ax, bars2, color=colors[3])
plt.savefig('chart_4_p95_without_redis.png')
plt.close()

print("✅ Todos os gráficos gerados com sucesso!")
