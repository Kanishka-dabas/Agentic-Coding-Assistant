
import streamlit as st

from services.api_client import send_task_streaming, send_resume_streaming

st.set_page_config(page_title="Agentic Coding Assistant", page_icon="🤖")

# "conversations" is a list of {"title": str, "history": list} - one per
# past conversation in THIS tab. "history" is the currently active one.
if "conversations" not in st.session_state:
    st.session_state["conversations"] = []
if "history" not in st.session_state:
    st.session_state["history"] = []
if "pending_approval" not in st.session_state:
    st.session_state["pending_approval"] = None

STEP_LABELS = {
    "input_guard": "Checking input safety",
    "planner": "Planning the approach",
    "retriever": "Searching the codebase",
    "coder": "Writing code",
    "code_guard": "Scanning code for risks",
    "hitl_approval": "Waiting for approval",
    "executor": "Running the code",
    "reflector": "Reflecting on the error",
}


def render_step(s: dict):
    if s.get("blocked"):
        st.write(f"⛔ Blocked: {s.get('block_reason', 'no reason given')}")
        return

    if s.get("plan"):
        st.write(f"📋 {s['result']}")
        for i, step in enumerate(s["plan"], start=1):
            st.write(f"{i}. {step}")
        return

    if s.get("generated_code"):
        st.write(f"💻 {s['result']}")
        st.code(s["generated_code"], language="python")
        return

    if s.get("execution_success") is not None:
        icon = "✅" if s["execution_success"] else "❌"
        st.write(f"{icon} {s['result']}")
        if s.get("execution_stdout"):
            st.code(s["execution_stdout"], language="text")
        if s.get("execution_stderr"):
            st.code(s["execution_stderr"], language="text")
    else:
        st.write(s.get("result", ""))


@st.dialog("Human approval required")
def hitl_dialog(generated_code: str, thread_id: str, steps_seen: list, task: str):
    st.write("The agent wants to run this code:")
    st.code(generated_code, language="python")

    col1, col2 = st.columns(2)
    if col1.button("✅ Approve", use_container_width=True):
        _resume_and_continue(thread_id, "approve", steps_seen, task)
        st.rerun()
    if col2.button("❌ Reject", use_container_width=True):
        _resume_and_continue(thread_id, "reject", steps_seen, task)
        st.rerun()


def _resume_and_continue(thread_id: str, decision: str, steps_seen: list, task: str):
    with st.status("Agent working...", expanded=True) as status:
        try:
            for step in send_resume_streaming(thread_id, decision):
                if step.get("requires_approval"):
                    st.session_state["pending_approval"] = {
                        "task": task,
                        "thread_id": step["thread_id"],
                        "generated_code": step.get("generated_code", ""),
                        "steps_seen": steps_seen,
                    }
                    status.update(label="Waiting for approval", state="running")
                    return
                label = STEP_LABELS.get(step.get("step"), step.get("step", "Working"))
                status.update(label=label)
                steps_seen.append(step)
        except Exception as e:
            steps_seen.append({"step": "error", "result": f"⚠️ Error calling backend: {e}"})
        status.update(label="Done", state="complete")

    st.session_state["history"].append((task, steps_seen))
    st.session_state["pending_approval"] = None


def run_new_task(task: str):
    steps_seen = []
    with st.chat_message("user"):
        st.write(task)

    with st.chat_message("assistant"):
        with st.status("Agent working...", expanded=True) as status:
            try:
                for step in send_task_streaming(task):
                    if step.get("requires_approval"):
                        st.session_state["pending_approval"] = {
                            "task": task,
                            "thread_id": step["thread_id"],
                            "generated_code": step.get("generated_code", ""),
                            "steps_seen": steps_seen,
                        }
                        status.update(label="Waiting for approval", state="running")
                        st.rerun()
                    label = STEP_LABELS.get(step.get("step"), step.get("step", "Working"))
                    status.update(label=label)
                    steps_seen.append(step)
            except Exception as e:
                steps_seen.append({"step": "error", "result": f"⚠️ Error calling backend: {e}"})
            status.update(label="Done", state="complete")

        for s in steps_seen:
            render_step(s)

    st.session_state["history"].append((task, steps_seen))


def archive_current_conversation():
    """Saves the current chat into the in-tab conversations list before
    starting a fresh one, using the first task as a short title."""
    if st.session_state["history"]:
        title = st.session_state["history"][0][0][:35]
        st.session_state["conversations"].append({
            "title": title,
            "history": st.session_state["history"],
        })


with st.sidebar:
    st.header("🤖 Agentic Coding Assistant")

    if st.button("➕ New conversation", use_container_width=True):
        archive_current_conversation()
        st.session_state["history"] = []
        st.session_state["pending_approval"] = None
        st.rerun()

    st.divider()
    st.subheader("This session's chats")
    if st.session_state["conversations"]:
        for i, conv in enumerate(st.session_state["conversations"]):
            if st.button(conv["title"], key=f"conv_{i}", use_container_width=True):
                archive_current_conversation()
                st.session_state["history"] = conv["history"]
                st.session_state["conversations"].pop(i)
                st.session_state["pending_approval"] = None
                st.rerun()
    else:
        st.caption("No past chats in this tab yet.")

st.title("🤖 Agentic Coding Assistant")

if st.session_state["pending_approval"]:
    pending = st.session_state["pending_approval"]
    for user_task, steps in st.session_state["history"]:
        with st.chat_message("user"):
            st.write(user_task)
        with st.chat_message("assistant"):
            for s in steps:
                render_step(s)

    with st.chat_message("user"):
        st.write(pending["task"])
    with st.chat_message("assistant"):
        for s in pending["steps_seen"]:
            render_step(s)

    hitl_dialog(pending["generated_code"], pending["thread_id"], pending["steps_seen"], pending["task"])

else:
    for user_task, steps in st.session_state["history"]:
        with st.chat_message("user"):
            st.write(user_task)
        with st.chat_message("assistant"):
            for s in steps:
                render_step(s)

    task = st.chat_input("Describe a coding task...")
    if task:
        run_new_task(task)