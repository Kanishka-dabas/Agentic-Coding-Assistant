from app.memory.checkpointer import checkpointer

def list_sessions(limit : int = 20)->list[dict]:

    seen_threads = {}

    for checkpoint_tuple in checkpointer.list(None , limit=limit*5):
        thread_id =  checkpoint_tuple.config["configurable"]["thread_id"]
        if thread_id in seen_threads:
            continue

        state = checkpoint_tuple.checkpoint.get("channel_values",{})
        seen_threads[thread_id] = {
            "thread_id": thread_id,
            "task": state.get("task", "(unknown task)"),
            "last_step": state.get("current_step", ""),
        }
        if len(seen_threads) >= limit:
            break

    return list(seen_threads.values())    