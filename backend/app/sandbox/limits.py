"""
Resource limits for sandboxed code execution.

The sandbox uses real container isolation:
  - No network access (--network none)
  - Memory and CPU caps enforced by the Docker daemon/kernel (cgroups)
  - A hard execution timeout
  - A fresh, throwaway container per execution — no state leaks between runs
"""

EXECUTION_TIMEOUT_SECONDS = 30

MAX_OUTPUT_BYTES = 10_000

CONTAINER_MEMORY_LIMIT = "128m"
CONTAINER_CPU_LIMIT = 0.5
CONTAINER_IMAGE = "python:3.12-slim"