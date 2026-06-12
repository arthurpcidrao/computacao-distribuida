import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def get_stats():
    results = []
    # Pattern: locust_results/{lang}_{tech}_{users}_stats.csv
    files = glob.glob("locust_results/*_stats.csv")
    print(f"Found {len(files)} files.")
    for file in files:
        filename = os.path.basename(file)
        if filename == "dashboard_data.csv": continue
        
        parts = filename.replace("_stats.csv", "").split("_")
        if len(parts) != 3: 
            print(f"Skipping {filename}: unexpected parts {parts}")
            continue
        
        lang_code, tech, users = parts
        lang = "Python" if lang_code == "py" else "JavaScript"
        
        try:
            df = pd.read_csv(file)
            if 'Name' not in df.columns:
                print(f"Skipping {filename}: no 'Name' column")
                continue
            agg_rows = df[df['Name'] == 'Aggregated']
            if agg_rows.empty:
                print(f"Skipping {filename}: no 'Aggregated' row found")
                continue
            agg = agg_rows.iloc[0]
            
            results.append({
                "Linguagem": lang,
                "Estilo_API": tech.upper(),
                "Carga_Usuarios": int(users),
                "Total Request Count": agg['Request Count'],
                "Failure Count": agg['Failure Count'],
                "Median Response Time": agg['Median Response Time'],
                "95% Response Time": agg['95%'],
                "Average Response Time": agg['Average Response Time'],
                "Average Content Size": agg['Average Content Size'],
                "Requests/s": agg['Requests/s']
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    return pd.DataFrame(results)

def generate_charts(df):
    if df.empty: return
    os.makedirs("charts", exist_ok=True)

    # 1. p95 Comparison per API and Load
    styles = df['Estilo_API'].unique()
    for style in styles:
        plt.figure(figsize=(10, 6))
        style_df = df[df['Estilo_API'] == style]
        pivot = style_df.pivot(index='Carga_Usuarios', columns='Linguagem', values='95% Response Time')
        pivot.plot(kind='bar', ax=plt.gca())
        plt.title(f'p95 Response Time - {style}')
        plt.ylabel('ms')
        plt.savefig(f'charts/p95_{style.lower()}.png')
        plt.close()

    # 2. Average Content Size Comparison
    plt.figure(figsize=(12, 6))
    content_df = df[df['Carga_Usuarios'] == 50] # Compare at baseline load (now 50)
    pivot_content = content_df.pivot(index='Estilo_API', columns='Linguagem', values='Average Content Size')
    pivot_content.plot(kind='bar', ax=plt.gca())
    plt.title('Average Content Size (Bytes) - Load 50')
    plt.ylabel('Bytes')
    plt.savefig('charts/content_size.png')
    plt.close()

    # 3. Combined p95 at High Load (50)
    plt.figure(figsize=(12, 6))
    high_load = df[df['Carga_Usuarios'] == 50]
    if not high_load.empty:
        pivot_high = high_load.pivot(index='Estilo_API', columns='Linguagem', values='95% Response Time')
        pivot_high.plot(kind='bar', ax=plt.gca())
        plt.title('p95 Response Time at Max Load (50 users)')
        plt.ylabel('ms')
        plt.savefig('charts/p95_combined_high.png')
        plt.close()

def main():
    df = get_stats()
    if not df.empty:
        df.to_csv("locust_results/dashboard_data.csv", index=False)
        generate_charts(df)
        print("Consolidation complete. Results in locust_results/dashboard_data.csv and charts/")
    else:
        print("No results found to consolidate.")

if __name__ == "__main__":
    main()