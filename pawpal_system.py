from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """Represents a single pet care activity."""
    description: str
    time: str                          # "HH:MM" format
    frequency: str                     # "once", "daily", "weekly"
    pet_name: str
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self):
        """Mark this task as complete and return a new recurrence if applicable."""
        self.completed = True
        if self.frequency == "daily":
            return Task(self.description, self.time, self.frequency,
                        self.pet_name, self.due_date + timedelta(days=1))
        elif self.frequency == "weekly":
            return Task(self.description, self.time, self.frequency,
                        self.pet_name, self.due_date + timedelta(weeks=1))
        return None


@dataclass
class Pet:
    """Represents a pet with its own task list."""
    name: str
    species: str
    age: int
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list:
        """Return all tasks for this pet."""
        return self.tasks


class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str, email: str):
        """Initialize owner with name and email."""
        self.name = name
        self.email = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to the owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """Retrieve all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_pet_names(self) -> list:
        """Return a list of all pet names."""
        return [pet.name for pet in self.pets]


class Scheduler:
    """The brain that organizes and manages tasks across all pets."""

    def __init__(self, owner: Owner):
        """Initialize scheduler with an owner."""
        self.owner = owner

    def get_todays_schedule(self) -> list:
        """Return all tasks sorted by time."""
        return self.sort_by_time(self.owner.get_all_tasks())

    def sort_by_time(self, tasks: list) -> list:
        """Sort a list of tasks chronologically by their time attribute."""
        return sorted(tasks, key=lambda t: t.time)

    def filter_by_pet(self, pet_name: str) -> list:
        """Return only tasks belonging to a specific pet."""
        return [t for t in self.owner.get_all_tasks() if t.pet_name == pet_name]

    def filter_by_status(self, completed: bool) -> list:
        """Return tasks filtered by completion status."""
        return [t for t in self.owner.get_all_tasks() if t.completed == completed]

    def detect_conflicts(self) -> list:
        """Detect tasks scheduled at the same time for any pet."""
        tasks = self.owner.get_all_tasks()
        seen = {}
        conflicts = []
        for task in tasks:
            key = task.time
            if key in seen:
                conflicts.append(
                    f"⚠️ Conflict at {task.time}: '{seen[key].description}' "
                    f"({seen[key].pet_name}) vs '{task.description}' ({task.pet_name})"
                )
            else:
                seen[key] = task
        return conflicts

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and schedule recurrence if needed."""
        new_task = task.mark_complete()
        if new_task:
            # Add the new recurring task to the correct pet
            for pet in self.owner.pets:
                if pet.name == task.pet_name:
                    pet.add_task(new_task)
                    break
        return new_task