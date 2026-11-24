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
    assert status == 200, f"Response status code is {status}"

    elapsed = end - start
    position_count = len(response.json()["Positions"])

    assert position_count == 57, f"Response position count is {position_count}"

    return status, elapsed, position_count


def concurrency_batch_function(concurrency):
    futures = []
    results = []
    failures = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        start = time.perf_counter()
        for i in range(concurrency):
            futures.append(executor.submit(benchmark_api_request, pgn))
        for future in futures:
            try:
                result = future.result()
            except Exception as error:
                failures.append(error)
            else:
                results.append(result)
        end = time.perf_counter()

    elapsed_time = end - start
    successful_throughput = len(results) / elapsed_time

    return results, failures, elapsed_time, successful_throughput


# print(" ")
# print("----------Concurrent requests 8, 16, and 4----------")
# print("---------------------")
# print("8 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(8)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
# print("16 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(16)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
# print("4 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(4)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")

# print(" ")
# print("----------Concurrent requests 16, 4, and 8----------")
# print("---------------------")
# print("16 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(16)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
# print("4 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(4)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
# print("8 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(8)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")

# print(" ")
# print("----------Concurrent requests 4, 8, 16, and 32----------")
# print("---------------------")
# print("4 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(4)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
# print("8 concurrent request")
# print("---------------------")
# temp = concurrency_batch_function(8)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
# print("16 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(16)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
# print("32 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(32)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
# print("32 concurrent requests")
# print("---------------------")
# temp = concurrency_batch_function(32)
# print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")
# print("---------------------")
print("32 concurrent requests - 16 slot condition")
print("---------------------")
temp = concurrency_batch_function(32)
print(f"Results: {temp[0]}\nNumber of failures: {len(temp[1])}\nFailures: {temp[1]}\nElapsed seconds: {temp[2]}\nRequests per second: {temp[3]}")