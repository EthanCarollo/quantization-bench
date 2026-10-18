#!/usr/bin/env python3
"""Small llama-server lifecycle helper for local GGUF benchmark runners."""

import json
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


LLAMA_CPP = Path.home() / ".cache" / "roleplay-bench" / "llama.cpp"
SERVER = LLAMA_CPP / "build" / "bin" / "llama-server"


class LlamaServer:
    def __init__(
        self,
        model_path: Path,
        *,
        port: int = 8080,
        context_size: int = 8192,
        parallel: int = 1,
        gpu_layers: int | str | None = None,
        log_path: Path | None = None,
    ) -> None:
        self.model_path = model_path.resolve()
        self.port = port
        self.context_size = context_size
        self.parallel = parallel
        self.gpu_layers = gpu_layers
        self.log_path = log_path or Path.home() / ".cache" / "quantization-bench" / f"llama-server-{port}.log"
        self.process: subprocess.Popen | None = None
        self._log_file = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/v1"

    def start(self, timeout_seconds: int = 900) -> None:
        if not SERVER.is_file():
            raise SystemExit(f"Missing llama-server at {SERVER}; finish the CUDA build first.")
        if not self.model_path.is_file():
            raise SystemExit(f"Missing GGUF model: {self.model_path}")
        if self.gpu_layers is None:
            # Let llama.cpp choose the largest layer count that fits the local GPU.
            # A size-based layer limit went stale across machines with different VRAM.
            self.gpu_layers = "auto"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log_file = self.log_path.open("w", encoding="utf-8")
        command = [
            str(SERVER),
            "--model", str(self.model_path),
            "--host", "127.0.0.1",
            "--port", str(self.port),
            "--n-gpu-layers", str(self.gpu_layers),
            "--ctx-size", str(self.context_size),
            "--parallel", str(self.parallel),
            "--fit", "on",
            "--batch-size", "512",
            "--ubatch-size", "512",
            "--reasoning", "off",
        ]
        self.process = subprocess.Popen(
            command,
            cwd=LLAMA_CPP,
            stdout=self._log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=os.environ.copy(),
        )
        deadline = time.monotonic() + timeout_seconds
        health_url = f"http://127.0.0.1:{self.port}/health"
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(
                    f"llama-server exited with status {self.process.returncode}; see {self.log_path}"
                )
            try:
                with urllib.request.urlopen(health_url, timeout=2) as response:
                    if response.status == 200:
                        return
            except (OSError, urllib.error.URLError):
                time.sleep(2)
        raise TimeoutError(f"llama-server did not become ready within {timeout_seconds}s; see {self.log_path}")

    def stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGTERM)
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait(timeout=10)
        if self._log_file is not None:
            self._log_file.close()

    def chat_completion(self, payload: dict, timeout_seconds: int = 3600) -> dict:
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer local"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[-1000:]
            raise RuntimeError(f"llama-server returned HTTP {exc.code}: {detail}") from exc

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.stop()
