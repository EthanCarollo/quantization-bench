#!/usr/bin/env python3
"""Score only one problem's candidates inside a disposable sandbox container."""

import json
import multiprocessing
import queue as queue_module
import sys
import zlib
import base64
import pickle

from testing_util import run_test


RESULT_PREFIX = "__LIVE_CODE_BENCH_RESULT__"
TIMEOUT_SECONDS = 6


def decode_cases(value):
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        packed = base64.b64decode(value.encode("utf-8"))
        return json.loads(pickle.loads(zlib.decompress(packed)))


def build_sample(row):
    public = decode_cases(row["public_test_cases"])
    private = decode_cases(row["private_test_cases"])
    tests = public + private
    metadata = json.loads(row["metadata"])
    return {
        "input_output": json.dumps(
            {
                "inputs": [case["input"] for case in tests],
                "outputs": [case["output"] for case in tests],
                "fn_name": metadata.get("func_name"),
            }
        )
    }


def run_child(sample, code, queue):
    try:
        results, metadata = run_test(sample, test=code, debug=False, timeout=TIMEOUT_SECONDS)
        queue.put({"completed": True, "passed": bool(results) and all(value is True for value in results)})
    except BaseException as exc:
        queue.put({"completed": False, "passed": False, "grader_error": type(exc).__name__})


def check_one(sample, code):
    testcase_count = len(json.loads(sample["input_output"])["inputs"])
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=run_child, args=(sample, code, queue))
    process.start()
    process.join(timeout=(TIMEOUT_SECONDS + 1) * testcase_count + 5)
    if process.is_alive():
        process.kill()
        process.join()
        queue.close()
        return {"completed": True, "passed": False, "grader_error": "global_timeout"}
    try:
        result = queue.get(timeout=3)
    except queue_module.Empty:
        queue.close()
        return {"completed": True, "passed": False, "grader_error": "worker_exit_without_result"}
    queue.close()
    return result


def main():
    job = json.load(sys.stdin)
    sample = build_sample(job["row"])
    candidates = [check_one(sample, code) for code in job["codes"]]
    print(RESULT_PREFIX + json.dumps({"question_id": job["question_id"], "candidates": candidates}))


if __name__ == "__main__":
    main()
