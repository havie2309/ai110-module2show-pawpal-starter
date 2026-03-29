import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# --- Fixtures ---
@pytest.fixture
def sample_owner():
    owner = Owner("Alex", "alex@email.com")
    buddy = Pet("Buddy", "Dog", 3)
    whiskers = Pet("Whiskers", "Cat", 5)
    buddy.add_task(Task("Evening Walk",    "18:00", "daily",  "Buddy"))
    buddy.add_task(Task("Morning Walk",    "08:00", "daily",  "Buddy"))
    whiskers.add_task(Task("Breakfast",   "08:00", "daily",  "Whiskers"))
    whiskers.add_task(Task("Vet Checkup", "14:00", "once",   "Whiskers"))
    owner.add_pet(buddy)
    owner.add_pet(whiskers)
    return owner


# --- Task Tests ---
def test_mark_complete_changes_status():
    """mark_complete() should set completed to True."""
    task = Task("Walk", "08:00", "once", "Buddy")
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_count():
    """Adding a task to a Pet should increase task count by 1."""
    pet = Pet("Buddy", "Dog", 3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", "08:00", "daily", "Buddy"))
    assert len(pet.tasks) == 1


# --- Sorting Tests ---
def test_sort_by_time_returns_chronological_order(sample_owner):
    """Tasks should be sorted earliest to latest."""
    scheduler = Scheduler(sample_owner)
    sorted_tasks = scheduler.get_todays_schedule()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)


# --- Recurrence Tests ---
def test_daily_task_creates_next_day_recurrence():
    """Completing a daily task should produce a new task for tomorrow."""
    today = date.today()
    task = Task("Walk", "08:00", "daily", "Buddy", due_date=today)
    new_task = task.mark_complete()
    assert new_task is not None
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False


def test_once_task_has_no_recurrence():
    """Completing a 'once' task should not create a new task."""
    task = Task("Vet Visit", "14:00", "once", "Whiskers")
    new_task = task.mark_complete()
    assert new_task is None


# --- Conflict Detection Tests ---
def test_conflict_detection_flags_same_time(sample_owner):
    """Scheduler should detect two tasks at 08:00."""
    scheduler = Scheduler(sample_owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) > 0
    assert "08:00" in conflicts[0]


def test_no_conflict_when_times_differ():
    """No conflicts should be reported when all task times are unique."""
    owner = Owner("Sam", "sam@email.com")
    pet = Pet("Max", "Dog", 2)
    pet.add_task(Task("Walk",      "07:00", "daily", "Max"))
    pet.add_task(Task("Feeding",   "12:00", "daily", "Max"))
    pet.add_task(Task("Playtime",  "17:00", "daily", "Max"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []