"""
Retry limiter guardrail - caps how many times the coder/reflector loop
can run before escalating to a human, so a persistently-failing task
can't loop forever burning LLM calls and cost.
"""

MAX_RETRIES = 3

def has_retries_left(retry_count:int)->bool:
    return retry_count < MAX_RETRIES