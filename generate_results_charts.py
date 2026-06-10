import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def get_stats():
    results = []
    for file in glob.glob("locust_results/*_stats.csv"):
        name = os.path.basename(file).replace("_stats.csv", "")
        lang, tech = name.split("_")
        df = pd.read_csv(file)
        # Get the 'Aggregated' row
        agg = df[df['Name'] == 'Aggregated'].iloc[0]
        results.append({
            "lang": "Python" if lang == "py" else "Node.js",
            "tech": tech.upper(),
            "avg_latency": agg['Average Response Time'],
            "p95_latency": agg['95%'],
            "failure_rate": agg['Failure Count'] / agg['Request Count'] * 100 if agg['Request Count'] > 0 else 0
        })
    return pd.DataFrame(results)

def plot_all(df):
    if df.empty:
        print("No data found to plot.")
        return

    # 1. Comparativo de Linguagens (Avg Latency)
    plt.figure(figsize=(10, 6))
    pivot_df = df.pivot(index='tech', columns='lang', values='avg_latency')
    pivot_df.plot(kind='bar')
    plt.title('Tempo de Resposta Médio (ms): Python vs Node.js')
    plt.ylabel('ms')
    plt.savefig('comparativo_linguagens.png')
    plt.close()

    # 2. Comparativo Tecnologias Python
    plt.figure(figsize=(8, 6))
    py_df = df[df['lang'] == 'Python']
    plt.bar(py_df['tech'], py_df['avg_latency'], color='blue')
    plt.title('Latência Média por Tecnologia (Python)')
    plt.ylabel('ms')
    plt.savefig('comparativo_tecnologias_python.png')
    plt.close()

    # 3. Comparativo Tecnologias Node.js
    plt.figure(figsize=(8, 6))
    node_df = df[df['lang'] == 'Node.js']
    plt.bar(node_df['tech'], node_df['avg_latency'], color='green')
    plt.title('Latência Média por Tecnologia (Node.js)')
    plt.ylabel('ms')
    plt.savefig('comparativo_tecnologias_node.png')
    plt.close()

    # 4. Comparativo de Falhas
    plt.figure(figsize=(10, 6))
    pivot_fail = df.pivot(index='tech', columns='lang', values='failure_rate')
    pivot_fail.plot(kind='bar')
    plt.title('Taxa de Falhas (%)')
    plt.ylabel('%')
    plt.savefig('comparativo_falhas.png')
    plt.close()

if __name__ == "__main__":
    df = get_stats()
    plot_all(df)
    print("Charts generated successfully.")
