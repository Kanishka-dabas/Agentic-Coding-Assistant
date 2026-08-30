"""
Executes agent-generated Python code inside an isolated, throwaway Docker
container - no network access, memory/CPU capped, hard timeout.
"""

import subprocess
import uuid
import os

from app.sandbox.limits import (
    EXECUTION_TIMEOUT_SECONDS,
    MAX_OUTPUT_BYTES,
    CONTAINER_MEMORY_LIMIT,
    CONTAINER_CPU_LIMIT,
    CONTAINER_IMAGE,
)

HOST_SANDBOX_PATH = os.getenv("SANDBOX_HOST_PATH", "/tmp")
CONTAINER_SANDBOX_PATH = "/sandbox_tmp"


def run_code(code: str) -> dict:
    run_id = str(uuid.uuid4())
    container_dir = os.path.join(CONTAINER_SANDBOX_PATH, run_id)
    host_dir = os.path.join(HOST_SANDBOX_PATH, run_id)

    os.makedirs(container_dir, exist_ok=True)
    script_path = os.path.join(container_dir, "generated_script.py")
    with open(script_path, "w") as f:
        f.write(code)

    docker_cmd = [
        "docker", "run",
        "--rm",
        "--network", "none",
        "--memory", CONTAINER_MEMORY_LIMIT,
        "--cpus", str(CONTAINER_CPU_LIMIT),
        "-v", f"{host_dir}:/sandbox:ro",
        "-w", "/sandbox",
        CONTAINER_IMAGE,
        "python", "generated_script.py",
    ]

    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT_SECONDS,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[:MAX_OUTPUT_BYTES],
            "stderr": result.stderr[:MAX_OUTPUT_BYTES],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution exceeded {EXECUTION_TIMEOUT_SECONDS}s timeout - killed.",
            "timed_out": True,
        }