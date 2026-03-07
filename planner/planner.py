from planner.state import State


class Planner:

    def __init__(self, tasks, available_slots):

        self.tasks = tasks
        self.available_slots = available_slots

        self.deadline_penalty = 20
        self.weekend_penalty = 5
        self.overload_penalty = 3

    def get_initial_state(self):

        remaining = {}

        for task in self.tasks:
            remaining[task.name] = task.hours

        return State({}, remaining)

    def get_actions(self, state):

        actions = []

        for (day, slot) in self.available_slots:

            if (day, slot) in state.schedule:
                continue

            for task, hours in state.remaining_tasks.items():

                if hours > 0:
                    actions.append(("Apple", task, day, slot))

        return actions

    def apply_action(self, state, action):

        _, task, day, slot = action

        new_state = state.copy()

        new_state.schedule[(day, slot)] = task

        new_state.remaining_tasks[task] -= 1

        if new_state.remaining_tasks[task] == 0:
            del new_state.remaining_tasks[task]

        return new_state

    def compute_cost(self, state):

        cost = 0

        day_load = {}

        for (day, slot), task in state.schedule.items():

            if day not in day_load:
                day_load[day] = 0

            day_load[day] += 1

            if day >= 6:
                cost += self.weekend_penalty

            task_deadline = None

            for t in self.tasks:
                if t.name == task:
                    task_deadline = t.deadline_day

            if day > task_deadline:
                cost += self.deadline_penalty

        for day, load in day_load.items():

            if load > 3:
                cost += self.overload_penalty

        return cost

    def heuristic(self, state):

        remaining_hours = sum(state.remaining_tasks.values())

        return remaining_hours