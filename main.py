from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date

# --- Setup ---
owner = Owner(name="Alex", email="alex@email.com")

buddy = Pet(name="Buddy", species="Dog", age=3)
whiskers = Pet(name="Whiskers", species="Cat", age=5)

# --- Add Tasks (intentionally out of order to test sorting) ---
buddy.add_task(Task("Evening Walk",    "18:00", "daily",  "Buddy"))
buddy.add_task(Task("Morning Walk",    "08:00", "daily",  "Buddy"))
buddy.add_task(Task("Flea Medication", "09:00", "weekly", "Buddy"))

whiskers.add_task(Task("Breakfast",   "08:00", "daily",  "Whiskers"))  # conflict with Buddy!
whiskers.add_task(Task("Vet Checkup", "14:00", "once",   "Whiskers"))

owner.add_pet(buddy)
owner.add_pet(whiskers)

scheduler = Scheduler(owner)

# --- Today's Schedule (sorted) ---
print("=" * 40)
print("       🐾 TODAY'S SCHEDULE")
print("=" * 40)
for task in scheduler.get_todays_schedule():
    status = "✅" if task.completed else "⬜"
    print(f"  {status} [{task.time}] {task.pet_name}: {task.description} ({task.frequency})")

# --- Conflict Detection ---
print("\n--- Conflict Check ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(c)
else:
    print("No conflicts found.")

# --- Filter: Incomplete tasks only ---
print("\n--- Incomplete Tasks ---")
for task in scheduler.filter_by_status(completed=False):
    print(f"  ⬜ [{task.time}] {task.pet_name}: {task.description}")

# --- Test Recurring Task ---
print("\n--- Recurring Task Test ---")
morning_walk = buddy.tasks[1]  # "Morning Walk"
new_task = scheduler.mark_task_complete(morning_walk)
print(f"Completed: '{morning_walk.description}' — status: {morning_walk.completed}")
if new_task:
    print(f"New recurrence created: '{new_task.description}' on {new_task.due_date}")