import requests
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

pgn = Path("benchmarks/games/baseline.pgn").read_text(encoding="utf-8")

def benchmark_api_request(pgn: str):
    start = time.perf_counter()

    response = requests.post(
        "http://127.0.0.1:8000/analyses",
        json={"pgn": pgn},
        timeout=60,
    )

    end = time.perf_counter()

    status = response.status_code
    assert status == 200

    elapsed = end - start
    position_count = len(response.json()["Positions"])

    assert position_count == 57

    return status, elapsed, position_count

for i in range(3):
    #concurrent
    with ThreadPoolExecutor(max_workers=2) as executor:
        start = time.perf_counter()    
        first_future = executor.submit(benchmark_api_request, pgn)
        second_future = executor.submit(benchmark_api_request, pgn)
        first_result = first_future.result()
        second_result = second_future.result()
        end = time.perf_counter()    
        pair_elapsed_time = end - start
        pair_throughput = 2 / pair_elapsed_time
    print (f"----------Concurrent run #{i+1}----------")
    print (f"First result: {first_result}")
    print (f"Second result: {second_result}")
    print(f"Pair elapsed seconds: {pair_elapsed_time}")
    print (f"Requests per second: {pair_throughput}")

for i in range(3):
    #sequential
    with ThreadPoolExecutor(max_workers=2) as executor:
        start = time.perf_counter()    
        first_future = executor.submit(benchmark_api_request, pgn)
        first_result = first_future.result()
        second_future = executor.submit(benchmark_api_request, pgn)
        second_result = second_future.result()
        end = time.perf_counter()    
        pair_elapsed_time = end - start
        pair_throughput = 2 / pair_elapsed_time
    print (f"----------Sequential run #{i+1}----------")
    print (f"First result: {first_result}")
    print (f"Second result: {second_result}")
    print(f"Pair elapsed seconds: {pair_elapsed_time}")
    print (f"Requests per second: {pair_throughput}")