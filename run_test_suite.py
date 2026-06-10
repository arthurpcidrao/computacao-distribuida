import subprocess
import time
import os

TESTS = [
    {"name": "py_rest", "class": "PythonRestUser", "host": "http://localhost:8001"},
    {"name": "node_rest", "class": "NodeRestUser", "host": "http://localhost:8011"},
    {"name": "py_graphql", "class": "PythonGraphQLUser", "host": "http://localhost:8002"},
    {"name": "node_graphql", "class": "NodeGraphQLUser", "host": "http://localhost:8012"},
    {"name": "py_grpc", "class": "PythonGrpcUser", "host": "localhost:50051"},
    {"name": "node_grpc", "class": "NodeGrpcUser", "host": "localhost:50052"},
    {"name": "py_soap", "class": "PythonSoapUser", "host": "http://localhost:8003/soap?wsdl"},
    {"name": "node_soap", "class": "NodeSoapUser", "host": "http://localhost:8013/soap?wsdl"},
]

RUN_TIME = "2m"
USERS = 50
SPAWN_RATE = 10

def run_test(test):
    print(f"Running test for {test['name']}...")
    csv_prefix = f"locust_results/{test['name']}"
    cmd = [
        "locust",
        "-f", "locustfile.py",
        "--headless",
        "-u", str(USERS),
        "-r", str(SPAWN_RATE),
        "-t", RUN_TIME,
        "--host", test['host'],
        "--csv", csv_prefix,
        test['class']
    ]
    subprocess.run(cmd)
    print(f"Finished test for {test['name']}.\n")

def main():
    if not os.path.exists("locust_results"):
        os.makedirs("locust_results")
    
    for test in TESTS:
        run_test(test)
        time.sleep(5) # Cooldown

if __name__ == "__main__":
    main()
