import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler  # noqa: F401
from datetime import date

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling for busy owners.")

# ── Session state: persist Owner across reruns ────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ── Section 1: Owner Setup ────────────────────────────────────────────────────
st.header("1. Owner Setup")
with st.form("owner_form"):
    col1, col2 = st.columns(2)
    owner_name  = col1.text_input("Your name",  value="Alex")
    owner_email = col2.text_input("Your email", value="alex@email.com")
    submitted = st.form_submit_button("Save Owner")
    if submitted:
        st.session_state.owner     = Owner(owner_name, owner_email)
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.success(f"Owner **{owner_name}** saved!")

if st.session_state.owner is None:
    st.info("Fill in your name and click **Save Owner** to get started.")
    st.stop()

owner     = st.session_state.owner
scheduler = st.session_state.scheduler

# ── Section 2: Add a Pet ──────────────────────────────────────────────────────
st.header("2. Add a Pet")
with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    pet_name    = col1.text_input("Pet name",   value="Buddy")
    pet_species = col2.selectbox("Species",     ["Dog", "Cat", "Bird", "Other"])
    pet_age     = col3.number_input("Age",       min_value=0, max_value=30, value=3)
    add_pet = st.form_submit_button("Add Pet")
    if add_pet:
        new_pet = Pet(name=pet_name, species=pet_species, age=int(pet_age))
        owner.add_pet(new_pet)
        st.success(f"🐶 **{pet_name}** added!")

if owner.pets:
    st.write("**Your pets:**", ", ".join(owner.get_pet_names()))
    # Delete a pet
    with st.expander("🗑️ Remove a pet"):
        pet_to_delete = st.selectbox("Select pet to remove", owner.get_pet_names(), key="delete_pet")
        if st.button("Delete Pet"):
            owner.pets = [p for p in owner.pets if p.name != pet_to_delete]
            st.success(f"Removed **{pet_to_delete}**.")
            st.rerun()

# ── Section 3: Add a Task ─────────────────────────────────────────────────────
st.header("3. Add a Task")
if not owner.pets:
    st.warning("Add at least one pet before scheduling tasks.")
else:
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        task_pet   = col1.selectbox("Pet",        owner.get_pet_names())
        task_desc  = col2.text_input("Task",       value="Morning Walk")
        col3, col4 = st.columns(2)
        task_time  = col3.text_input("Time (HH:MM)", value="08:00")
        task_freq  = col4.selectbox("Frequency",  ["once", "daily", "weekly"])
        add_task = st.form_submit_button("Add Task")
        if add_task:
            new_task = Task(
                description=task_desc,
                time=task_time,
                frequency=task_freq,
                pet_name=task_pet,
                due_date=date.today()
            )
            for pet in owner.pets:
                if pet.name == task_pet:
                    pet.add_task(new_task)
            st.success(f"✅ Task **{task_desc}** added for {task_pet} at {task_time}!")

# ── Section 4: Today's Schedule ───────────────────────────────────────────────
st.header("4. Today's Schedule")

all_tasks = scheduler.get_todays_schedule()

if not all_tasks:
    st.info("No tasks yet. Add pets and tasks above.")
else:
    # Conflict warnings
    conflicts = scheduler.detect_conflicts()
    for c in conflicts:
        st.warning(c)

    # Filter controls
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

    # Display table
    if filtered:
        rows = []
        for t in filtered:
            rows.append({
                "Status":    "✅ Done" if t.completed else "⬜ Pending",
                "Time":      t.time,
                "Pet":       t.pet_name,
                "Task":      t.description,
                "Frequency": t.frequency,
                "Due":       str(t.due_date),
            })
        st.table(rows)

        # Mark complete buttons
        st.subheader("Mark a task complete")
        pending = [t for t in filtered if not t.completed]
        if pending:
            task_labels = [f"[{t.time}] {t.pet_name}: {t.description}" for t in pending]
            chosen = st.selectbox("Select task", task_labels)
            if st.button("✅ Mark Complete"):
                idx = task_labels.index(chosen)
                new_recurring = scheduler.mark_task_complete(pending[idx])
                if new_recurring:
                    st.success(f"Done! Next **{new_recurring.description}** scheduled for {new_recurring.due_date}.")
                else:
                    st.success("Task marked complete!")
                st.rerun()
        else:
            st.success("🎉 All tasks complete!")
    else:
        st.info("No tasks match your filters.")