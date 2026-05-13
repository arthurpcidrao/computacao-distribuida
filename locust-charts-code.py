# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import os
# from matplotlib.patches import Rectangle

# # 1. Configurações e Carregamento
# csv_file = 'testes-locust - Página1.csv'
# base_output_dir = './images/'

# if not os.path.exists(base_output_dir):
#     os.makedirs(base_output_dir)

# try:
#     df = pd.read_csv(csv_file)
#     df.columns = [
#         'instancias', 'usuarios', 'tipo', 'endpoint', 'requests', 'fails',
#         'median_ms', 'p95_ms', 'p99_ms', 'avg_ms', 'min_ms', 'max_ms',
#         'avg_size', 'rps', 'failures_s'
#     ]
    
#     # Cálculo da Taxa de Falha em porcentagem
#     df['failure_rate'] = (df['fails'] / df['requests']) * 100
    
# except FileNotFoundError:
#     print(f"Erro: O arquivo '{csv_file}' não foi encontrado.")
#     exit()

# sns.set_theme(style="whitegrid")

# def gerar_graficos_por_endpoint(df_subset, endpoint_name):
#     # Obter o tamanho médio de resposta para este endpoint (formatado)
#     avg_resp_size = df_subset['avg_size'].mean()
    
#     # Tratamento do nome do endpoint para pastas
#     folder_name = endpoint_name.replace('/', 'root').replace('?', '_').replace('=', '_')
#     path = os.path.join(base_output_dir, folder_name)
    
#     if not os.path.exists(path):
#         os.makedirs(path)
    
#     # --- GRÁFICO: RPS vs INSTÂNCIAS ---
#     plt.figure(figsize=(10, 6))
#     ax_rps = sns.barplot(
#         data=df_subset, 
#         x='instancias', 
#         y='rps', 
#         hue='usuarios', 
#         palette='viridis'
#     )
    
#     plt.title(f'Endpoint: {endpoint_name} (Size: {avg_resp_size:.0f} bytes)\nRPS vs Número de Instâncias', fontsize=12, fontweight='bold')
#     plt.xlabel('Número de Instâncias do WordPress', fontsize=10)
#     plt.ylabel('Requisições por Segundo (RPS)', fontsize=10)
#     plt.legend(title='Usuários Simultâneos', bbox_to_anchor=(1.05, 1), loc='upper left')
    
#     for p in ax_rps.patches:
#         if isinstance(p, Rectangle) and p.get_height() > 0:
#             ax_rps.annotate(format(p.get_height(), '.1f'), 
#                             (p.get_x() + p.get_width() / 2., p.get_height()), 
#                             ha='center', va='center', 
#                             xytext=(0, 7), textcoords='offset points', fontsize=8)
    
#     plt.tight_layout()
#     plt.savefig(os.path.join(path, 'rps_vs_instancias.png'))
#     plt.close()

#     # --- OUTROS GRÁFICOS: MÉTRICAS vs USUÁRIOS ---
#     # Adicionado p95_ms e failure_rate (Taxa de Falha)
#     metrics = {
#         'median_ms': 'Tempo de Resposta (Mediana ms)',
#         'p95_ms': 'Tempo de Resposta (P95 ms)',
#         'failure_rate': 'Taxa de Falha (%)'
#     }

#     for metric, label in metrics.items():
#         plt.figure(figsize=(10, 6))
#         ax = sns.barplot(
#             data=df_subset, 
#             x='usuarios', 
#             y=metric, 
#             hue='instancias', 
#             palette='magma'
#         )
        
#         plt.title(f'Endpoint: {endpoint_name} (Size: {avg_resp_size:.0f} bytes)\n{label}', fontsize=12, fontweight='bold')
#         plt.xlabel('Usuários Simultâneos', fontsize=10)
#         plt.ylabel(label, fontsize=10)
#         plt.legend(title='Instâncias WP', bbox_to_anchor=(1.05, 1), loc='upper left')
        
#         for p in ax.patches:
#             if isinstance(p, Rectangle) and p.get_height() >= 0:
#                 # Formatação dinâmica: 1 casa decimal para taxa, inteiro para milissegundos
#                 fmt = '.2f' if metric == 'failure_rate' else '.0f'
#                 ax.annotate(format(p.get_height(), fmt), 
#                             (p.get_x() + p.get_width() / 2., p.get_height()), 
#                             ha='center', va='center', 
#                             xytext=(0, 7), textcoords='offset points', fontsize=8)

#         plt.tight_layout()
#         plt.savefig(os.path.join(path, f'{metric}_vs_usuarios.png'))
#         plt.close()

# # 2. Execução Principal
# if __name__ == "__main__":
#     unique_endpoints = df['endpoint'].unique()
#     print(f"Gerando gráficos para {len(unique_endpoints)} endpoints...")

#     for ep in unique_endpoints:
#         df_endpoint = df[df['endpoint'] == ep]
#         gerar_graficos_por_endpoint(df_endpoint, ep)
#         print(f"✓ Pasta para endpoint '{ep}' processada.")

#     print(f"\nSucesso! Gráficos salvos na pasta: {base_output_dir}")


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.patches import Rectangle

# 1. Configurações e Carregamento
csv_file = 'testes-locust - Página1.csv'
base_output_dir = './images/'

if not os.path.exists(base_output_dir):
    os.makedirs(base_output_dir)

try:
    df = pd.read_csv(csv_file)
    df.columns = [
        'modelo', 'instancias', 'usuarios', 'tipo', 'endpoint', 'requests', 'fails',
        'median_ms', 'p95_ms', 'p99_ms', 'avg_ms', 'min_ms', 'max_ms',
        'avg_size', 'rps'
    ]
    df['failure_rate'] = (df['fails'] / df['requests']) * 100
    
except FileNotFoundError:
    print(f"Erro: O arquivo '{csv_file}' não foi encontrado.")
    exit()

sns.set_theme(style="whitegrid")

def gerar_comparativo_rotas(df_main):
    path = os.path.join(base_output_dir, "comparativo_geral")
    if not os.path.exists(path):
        os.makedirs(path)

    def rotular_rota(row):
        if row['modelo'] == 'Híbrido':
            return 'Híbrido'
        return row['endpoint'].replace('/?p=', 'Rota ')

    df_comp = df_main.copy()
    df_comp['identificador_rota'] = df_comp.apply(rotular_rota, axis=1)

    metrics = {
        'median_ms': 'Tempo de Resposta (Mediana ms)',
        'p95_ms': 'Tempo de Resposta (P95 ms)'
    }

    for metric, label in metrics.items():
        plt.figure(figsize=(12, 7))
        ordem_x = ['Rota 21', 'Rota 28', 'Rota 13', 'Híbrido']
        
        # Adicionado errorbar=None para remover os traços cinzas
        ax = sns.barplot(
            data=df_comp,
            x='identificador_rota',
            y=metric,
            hue='usuarios',
            order=ordem_x,
            palette='deep',
            errorbar=None
        )

        plt.title(f'Comparativo de Desempenho: Rotas vs Híbrido\n{label}', fontsize=14, fontweight='bold')
        plt.xlabel('Cenário / Rota', fontsize=12)
        plt.ylabel(label, fontsize=12)
        plt.legend(title='Usuários Simultâneos', loc='upper right')

        for p in ax.patches:
            if isinstance(p, Rectangle):
                height = p.get_height()
                if height > 0:
                    ax.annotate(format(height, '.0f'), 
                                (p.get_x() + p.get_width() / 2., height), 
                                ha='center', va='center', 
                                xytext=(0, 9), textcoords='offset points', 
                                fontsize=9, fontweight='bold')

        plt.tight_layout()
        plt.savefig(os.path.join(path, f'comparativo_{metric}.png'))
        plt.close()

def gerar_graficos_por_endpoint(df_subset, endpoint_name):
    folder_name = endpoint_name.replace('/', 'root').replace('?', '_').replace('=', '_')
    path = os.path.join(base_output_dir, folder_name)
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    # RPS vs INSTÂNCIAS - Adicionado errorbar=None
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_subset, x='instancias', y='rps', hue='usuarios', palette='viridis', errorbar=None)
    plt.title(f'Endpoint: {endpoint_name}\nRPS vs Instâncias', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(path, 'rps_vs_instancias.png'))
    plt.close()

    # MÉTRICAS vs USUÁRIOS
    metrics = {'median_ms': 'Mediana (ms)', 'p95_ms': 'P95 (ms)', 'failure_rate': 'Falha (%)'}
    for metric, label in metrics.items():
        plt.figure(figsize=(10, 6))
        df_plot = df_subset.copy()
        df_plot['config'] = df_plot.apply(
            lambda x: f"{int(x['instancias'])} Inst" if x['modelo'] != 'Híbrido' else "Híbrido", axis=1
        )
        
        # Adicionado errorbar=None
        ax = sns.barplot(data=df_plot, x='usuarios', y=metric, hue='config', palette='Set2', errorbar=None)
        plt.title(f'Endpoint: {endpoint_name}\n{label}', fontsize=12, fontweight='bold')
        
        for p in ax.patches:
            if isinstance(p, Rectangle):
                height = p.get_height()
                if height >= 0:
                    fmt = '.2f' if metric == 'failure_rate' else '.0f'
                    ax.annotate(format(height, fmt), 
                                (p.get_x() + p.get_width() / 2., height), 
                                ha='center', va='center', 
                                xytext=(0, 7), textcoords='offset points', fontsize=8)

        plt.tight_layout()
        plt.savefig(os.path.join(path, f'{metric}_vs_usuarios.png'))
        plt.close()

if __name__ == "__main__":
    print("Gerando comparativo geral entre rotas e híbrido...")
    gerar_comparativo_rotas(df)

    unique_endpoints = [ep for ep in df['endpoint'].unique() if ep != 'Aggregated']
    for ep in unique_endpoints:
        df_endpoint = df[(df['endpoint'] == ep) | (df['modelo'] == 'Híbrido')]
        gerar_graficos_por_endpoint(df_endpoint, ep)
        print(f"✓ Endpoint '{ep}' processado.")

    print(f"\nSucesso! Verifique a pasta: {base_output_dir}")