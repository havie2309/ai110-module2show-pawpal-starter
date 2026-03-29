# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I designed four classes: `Task`, `Pet`, `Owner`, and `Scheduler`. `Task` holds a single care activity with a description, time, frequency, and completion status. `Pet` stores pet info and owns a list of tasks. `Owner` manages multiple pets and can retrieve all tasks across them. `Scheduler` acts as the brain — it takes an `Owner` and provides sorting, filtering, conflict detection, and recurrence logic. I used Python dataclasses for `Task` and `Pet` to keep attribute definitions clean and avoid boilerplate `__init__` code.

**b. Design changes**

Initially I considered putting sort and filter logic directly on the `Owner` class, but I moved it to `Scheduler` to keep responsibilities separated. `Owner` should only manage pets, not make scheduling decisions. This made the code easier to test since I could pass an `Owner` into a `Scheduler` and test them independently.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time (HH:MM) as the primary constraint for ordering tasks and conflict detection. Frequency (once/daily/weekly) determines whether a task recurs. I prioritized time-based ordering because a pet owner's most immediate need is knowing *when* to do things throughout the day.

**b. Tradeoffs**

The conflict detection only flags tasks at the *exact same time* (e.g., both at `08:00`). It doesn't detect overlapping durations — for example, a 30-minute walk starting at `08:00` wouldn't conflict with a task at `08:15` even though they'd overlap in reality. This tradeoff is reasonable for this version because tasks don't currently store a duration, and exact-time conflicts are the most common scheduling mistake to catch.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to scaffold the initial class structure from a UML description, generate the Mermaid.js diagram, write the pytest suite, and draft the Streamlit UI layout. The most helpful prompts were specific ones that included context — for example, asking "how should Scheduler retrieve tasks from Owner's pets given this class structure" rather than a vague "help me schedule tasks."

**b. Judgment and verification**

When the AI generated the conflict detection logic, it originally used a nested loop (O(n²)) comparing every pair of tasks. I replaced it with a single-pass dictionary approach that stores the first task seen at each time slot — simpler, faster, and easier to read. I verified it by manually adding two tasks at the same time in `main.py` and confirming the warning printed correctly.

---

## 4. Testing and Verification

**a. What you tested**

I tested: task completion status change, pet task count after addition, chronological sort correctness, daily recurrence date calculation, one-time task producing no recurrence, conflict detection triggering correctly, and no false positives when times are unique. These cover the core behaviors that could silently break scheduling logic.

**b. Confidence**

I'm confident the core scheduling logic is correct — all 7 tests pass. Edge cases I'd test next with more time: tasks with invalid time formats (e.g. `"8:00"` vs `"08:00"`), pets with no tasks, and marking the same task complete twice.

---

## 5. Reflection

**a. What went well**

The "CLI-first" workflow worked really well. Testing the backend with `main.py` before touching the UI meant I caught issues early and the Streamlit integration was clean on the first try.

**b. What you would improve**

I'd add a duration field to `Task` and upgrade conflict detection to check for time-range overlaps rather than exact matches. I'd also add persistent storage so pets and tasks survive a page refresh.

**c. Key takeaway**

AI is most useful as a fast scaffolding tool, not a final decision-maker. It can generate a working structure quickly, but the developer still needs to evaluate whether the design makes sense, verify the logic, and catch subtle bugs the AI introduces confidently.