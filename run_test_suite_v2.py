import subprocess
import time
import pandas as pd
import os
import signal
import sys

# Configuration
APIS = [
    {"cwd": "APIs/python", "cmd": ["uv", "run", "python", "rest_api.py"], "name": "Py-REST"},
    {"cwd": "APIs/python", "cmd": ["uv", "run", "python", "graphql_api.py"], "name": "Py-GraphQL"},
    {"cwd": "APIs/python", "cmd": ["uv", "run", "python", "grpc_api.py"], "name": "Py-gRPC"},
    {"cwd": "APIs/python", "cmd": ["uv", "run", "python", "soap_api.py"], "name": "Py-SOAP"},
    {"cwd": "APIs/javascript", "cmd": ["node", "rest_api.js"], "name": "JS-REST"},
    {"cwd": "APIs/javascript", "cmd": ["node", "graphql_api.js"], "name": "JS-GraphQL"},
    {"cwd": "APIs/javascript", "cmd": ["node", "grpc_api.js"], "name": "JS-gRPC"},
    {"cwd": "APIs/javascript", "cmd": ["node", "soap_api.js"], "name": "JS-SOAP"},
]

def start_apis():
    processes = []
    print("Starting all APIs...")
    for api in APIS:
        log_file = open(f"{api['name']}.log", "w")
        p = subprocess.Popen(api['cmd'], cwd=api['cwd'], stdout=log_file, stderr=subprocess.STDOUT)
        processes.append((p, log_file))
        print(f"  Started {api['name']} (PID: {p.pid})")
    
    print("Waiting 60 seconds for all APIs to be ready...")
    time.sleep(60)
    return processes

def stop_apis(processes):
    print("Stopping all APIs...")
    for p, log in processes:
        try:
            # Try to terminate gracefully
            p.terminate()
            p.wait(timeout=5)
        except:
            p.kill()
        log.close()
    print("All APIs stopped.")

def run_prepopulate():
    print("Prepopulating data...")
    try:
        subprocess.run(["uv", "run", "python", "prepopulate_data.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Prepopulation failed: {e}")
        return False

def run_locust(users, spawn_rate, duration_sec):
    print(f"\n>>> Running Locust: Users={users}, Rate={spawn_rate}, Duration={duration_sec}s")
    base_name = "locust_results"
    
    for ext in ["_stats.csv", "_failures.csv"]:
        if os.path.exists(base_name + ext):
            os.remove(base_name + ext)

    cmd = [
        "uv", "run", "locust",
        "-f", "locustfile.py",
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "--run-time", f"{duration_sec}s",
        "--csv", base_name,
        "--only-summary"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Locust run failed: {e}")
        return None

    stats_file = base_name + "_stats.csv"
    if os.path.exists(stats_file):
        return pd.read_csv(stats_file)
    return None

def main():
    api_procs = start_apis()
    
    try:
        if not run_prepopulate():
            print("Aborting due to prepopulation failure.")
            return

        target_users = 100
        spawn_rate = 50
        duration = 120 # 2 minutes
        current_users = target_users
        
        while True:
            df = run_locust(current_users, spawn_rate, duration)
            if df is None:
                print("Failed to get results.")
                break
                
            total_row = df[df['Name'] == 'Aggregated']
            if total_row.empty:
                print("Aggregated stats not found.")
                break
                
            req_count = total_row['Request Count'].values[0]
            fail_count = total_row['Failure Count'].values[0]
            fail_rate = (fail_count / req_count) * 100 if req_count > 0 else 0
            
            print(f"Result: Users={current_users}, Failure Rate={fail_rate:.2f}%")
            
            if fail_rate > 5:
                print("Error rate > 5%. Retrying with fewer users...")
                current_users = int(current_users * 0.6)
                if current_users < 10: break
                continue
            elif fail_rate == 0 and current_users < 1000:
                print("0% errors. Pushing to higher load...")
                current_users = int(current_users * 1.5)
                continue
            else:
                print("Test successful. Saving final results.")
                os.rename("locust_results_stats.csv", "final_stats.csv")
                os.rename("locust_results_failures.csv", "final_failures.csv")
                break
        
        print("Generating charts...")
        subprocess.run(["uv", "run", "python", "generate_results_charts.py"], check=True)
        
    finally:
        stop_apis(api_procs)

if __name__ == "__main__":
    main()
