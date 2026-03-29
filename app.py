import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
PRIORITY_COLOR = {"high": "#ffcccc", "medium": "#fff8cc", "low": "#ccffcc"}

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

col_title, col_reset = st.columns([6, 1])
col_title.title("🐾 PawPal+")
col_title.caption("Smart pet care scheduling for busy owners.")
if col_reset.button("🔄 Reset", help="Clear all data and start over"):
    if "owner" in st.session_state and st.session_state.owner:
        import os
        if os.path.exists("data.json"):
            os.remove("data.json")
    st.session_state.clear()
    st.rerun()

# ── Session state: try loading from JSON first ────────────────────────────────
if "owner" not in st.session_state:
    loaded = Owner.load_from_json()
    st.session_state.owner = loaded
    st.session_state.scheduler = Scheduler(loaded) if loaded else None

# ── Section 1: Owner Setup ────────────────────────────────────────────────────
st.header("1. Owner Setup")
with st.form("owner_form"):
    col1, col2 = st.columns(2)
    owner_name  = col1.text_input("Your name",  value=st.session_state.owner.name if st.session_state.owner else "Alex")
    owner_email = col2.text_input("Your email", value=st.session_state.owner.email if st.session_state.owner else "alex@email.com")
    if st.form_submit_button("Save Owner"):
        st.session_state.owner     = Owner(owner_name, owner_email)
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.success(f"Owner **{owner_name}** saved!")

if st.session_state.owner is None:
    st.info("Fill in your name and click **Save Owner** to get started.")
    st.stop()

owner     = st.session_state.owner
scheduler = st.session_state.scheduler

# ── Section 2: Pets ───────────────────────────────────────────────────────────
st.header("2. Pets")
with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    pet_name    = col1.text_input("Pet name",  value="Buddy")
    pet_species = col2.selectbox("Species",    ["Dog", "Cat", "Bird", "Other"])
    pet_age     = col3.number_input("Age",      min_value=0, max_value=30, value=3)
    if st.form_submit_button("Add Pet"):
        owner.add_pet(Pet(name=pet_name, species=pet_species, age=int(pet_age)))
        owner.save_to_json()
        st.success(f"🐶 **{pet_name}** added!")

if owner.pets:
    st.write("**Your pets:**")
    for i, pet in enumerate(owner.pets):
        col_info, col_del = st.columns([5, 1])
        col_info.markdown(f"🐾 **{pet.name}** — {pet.species}, {pet.age} yrs")
        if col_del.button("🗑️", key=f"del_pet_{i}", help=f"Remove {pet.name}"):
            owner.pets.pop(i)
            owner.save_to_json()
            st.rerun()

# ── Section 3: Tasks ──────────────────────────────────────────────────────────
st.header("3. Tasks")
if not owner.pets:
    st.warning("Add at least one pet before scheduling tasks.")
else:
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        task_pet  = col1.selectbox("Pet",           owner.get_pet_names())
        task_desc = col2.text_input("Task",          value="Morning Walk")
        col3, col4, col5 = st.columns(3)
        task_time = col3.text_input("Time (HH:MM)",  value="08:00")
        task_freq = col4.selectbox("Frequency",     ["once", "daily", "weekly"])
        task_prio = col5.selectbox("Priority",      ["high", "medium", "low"], index=1)
        submitted = st.form_submit_button("Add Task")

    if submitted:
        new_task = Task(task_desc, task_time, task_freq, task_pet, date.today(), priority=task_prio)
        for pet in owner.pets:
            if pet.name == task_pet:
                pet.add_task(new_task)
        owner.save_to_json()
        st.success(f"✅ **{task_desc}** added for {task_pet} at {task_time}!")

    # Task list with delete buttons
    all_tasks_flat = [(pet, i, t) for pet in owner.pets for i, t in enumerate(pet.tasks)]
    if all_tasks_flat:
        st.write("**Current tasks:**")
        for global_idx, (pet, idx, task) in enumerate(all_tasks_flat):
            col_info, col_del = st.columns([5, 1])
            status = "✅" if task.completed else "⬜"
            badge  = PRIORITY_BADGE[task.priority]
            emoji  = task.get_emoji()
            col_info.markdown(
                f"{status} {emoji} **[{task.time}]** {pet.name}: {task.description} "
                f"_{task.frequency}_ — {badge}"
            )
            if col_del.button("🗑️", key=f"del_task_{global_idx}", help="Remove task"):
                pet.tasks.pop(idx)
                owner.save_to_json()
                st.rerun()

# ── Section 4: Today's Schedule ───────────────────────────────────────────────
st.header("4. Today's Schedule")
all_tasks = scheduler.get_todays_schedule()

if not all_tasks:
    st.info("No tasks yet. Add pets and tasks above.")
else:
    for c in scheduler.detect_conflicts():
        st.warning(c)

    col1, col2 = st.columns(2)
    filter_pet    = col1.selectbox("Filter by pet",    ["All"] + owner.get_pet_names())
    filter_status = col2.selectbox("Filter by status", ["All", "Incomplete", "Complete"])

    filtered = all_tasks
    if filter_pet != "All":
        filtered = [t for t in filtered if t.pet_name == filter_pet]
    if filter_status == "Incomplete":
        filtered = [t for t in filtered if not t.completed]
    elif filter_status == "Complete":
        filtered = [t for t in filtered if t.completed]

    if filtered:
        # Color-coded schedule rows
        for task in filtered:
            color  = PRIORITY_COLOR[task.priority]
            badge  = PRIORITY_BADGE[task.priority]
            emoji  = task.get_emoji()
            status = "✅ Done" if task.completed else "⬜ Pending"
            st.markdown(
                f"<div style='background:{color};padding:8px 12px;border-radius:8px;margin-bottom:6px;'>"
                f"{emoji} <b>[{task.time}]</b> {task.pet_name}: {task.description} "
                f"<span style='float:right'>{badge} &nbsp; {status} &nbsp; <i>{task.frequency}</i></span>"
                f"</div>",
                unsafe_allow_html=True
            )

        # Mark complete
        st.subheader("Mark a task complete")
        pending = [t for t in filtered if not t.completed]
        if pending:
            labels = [f"[{t.time}] {t.pet_name}: {t.description}" for t in pending]
            chosen = st.selectbox("Select task", labels)
            if st.button("✅ Mark Complete"):
                new = scheduler.mark_task_complete(pending[labels.index(chosen)])
                owner.save_to_json()
                if new:
                    st.success(f"Done! Next **{new.description}** scheduled for {new.due_date}.")
                else:
                    st.success("Task marked complete!")
                st.rerun()
        else:
            st.success("🎉 All tasks complete!")
    else:
        st.info("No tasks match your filters.")

# ── Footer: save reminder ─────────────────────────────────────────────────────
st.divider()
st.caption("💾 Data auto-saves to `data.json` — your pets and tasks persist between sessions!")