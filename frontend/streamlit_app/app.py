import streamlit as st

from services.api_client import send_task_streaming , send_resume_streaming , get_sessions

st.set_page_config(page_title ="Agentic Coding Assistant" , page_icon="🤖")
st.title("🤖 Agentic Coding Assistant")
st.caption("STEP_2 : Streaming")

with st.sidebar:
    st.header("Session History")
    try:
        sessions = get_sessions()
        if sessions:
            for sess in sessions:
                st.write(f"**{sess['task'][:40]}**")
                st.caption(f"Last step: {sess['last_step']}")
                st.divider()
        else:
            st.caption("No past sessions yet.")
    except Exception as e:
        st.caption(f"Could not load sessions: {e}")

if "history" not in st.session_state:
    st.session_state['history'] = []

if "pending_approval" not in st.session_state:
    st.session_state['pending_approval'] = None


def render_step(s:dict):
    """Renders one step dict. Falls back to plain text if execution
    fields aren't present"""
    st.write(f"**Step: {s['step']}**")

    if s.get('blocked'):
        st.write(f"⛔ Blocked: {s.get('block_reason', 'no reason given')}")
        return

    if s.get('plan'):
        st.write(f"📋 {s['result']}")
        for i , step in enumerate (s['plan'] , start=1):
            st.write(f"{i} . {step}")
        return  

    if s.get('retry_count') is not None:
        st.write(f"🔄 {s['result']}")
        return

    if s.get('generated_code'):
        st.write(f"💻 {s['result']}")
        st.code(s['generated_code'], language='python')
        return  

    if s.get('execution_success') is not None:
        icon = "✅" if s["execution_success"] else "❌"
        st.write(f"{icon} {s['result']}")
        if s.get('execution_stdout'):
            st.code(s['execution_stdout'] , language='text')
        if s.get('execution_stderr'):
            st.code(s['execution_stderr'] , language = 'text')
    else :
        st.write(s.get('result',""))        
    


for user_task , steps in st.session_state.history:
    with st.chat_message("user"):
        st.write(user_task)
    with st.chat_message("assistant"):
        for s in steps:
            render_step(s)

if st.session_state['pending_approval']:
    pending = st.session_state['pending_approval']

    with st.chat_message("user"):
        st.write(pending['task'])

    with st.chat_message("assistant"):
        for s in pending['steps_seen']:
            render_step(s)

        st.write("### 🧑‍💻 Human approval required")
        st.code(pending['generated_code'], language='python')

        col1, col2 = st.columns(2)
        approve_clicked = col1.button("✅ Approve")
        reject_clicked = col2.button("❌ Reject")

        if approve_clicked or reject_clicked:
            decision = "approve" if approve_clicked else "reject"
            steps_seen = pending['steps_seen']
            trace_placeholder = st.empty()

            try:
                for step in send_resume_streaming(pending['thread_id'], decision):
                    if step.get('requires_approval'):
                        st.session_state['pending_approval'] = {
                            "task": pending['task'],
                            "thread_id": step['thread_id'],
                            "generated_code": step.get('generated_code', ''),
                            "steps_seen": steps_seen,
                        }
                        st.rerun()

                    steps_seen.append(step)
                    with trace_placeholder.container():
                        for s in steps_seen:
                            render_step(s)
            except Exception as e:
                steps_seen.append({"step": "error", "result": f"⚠️ Error calling backend: {e}"})

            st.session_state.history.append((pending['task'], steps_seen))
            st.session_state['pending_approval'] = None
            st.rerun()

else:
    task = st.chat_input("Describe a coding task...")

    if task:
        with st.chat_message("user"):
            st.write(task)

        steps_seen = []
        with st.chat_message("assistant"):
            trace_placeholder = st.empty()
            try:
                for step in send_task_streaming(task):
                    if step.get('requires_approval'):
                        st.session_state['pending_approval'] = {
                            "task": task,
                            "thread_id": step['thread_id'],
                            "generated_code": step.get('generated_code', ''),
                            "steps_seen": steps_seen.copy(),
                        }
                        st.rerun()

                    steps_seen.append(step)
                    with trace_placeholder.container():
                        for s in steps_seen:
                            render_step(s)
            except Exception as e:
                steps_seen.append({"step": "error", "result": f"⚠️ Error calling backend: {e}"})

            st.session_state.history.append((task, steps_seen))