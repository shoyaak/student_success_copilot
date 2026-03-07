class State:

    def __init__(self, schedule, remaining_tasks):
        self.schedule = schedule
        self.remaining_tasks = remaining_tasks

    def is_goal(self):
        return len(self.remaining_tasks) == 0

    def copy(self):

        new_schedule = self.schedule.copy()
        new_remaining = self.remaining_tasks.copy()

        return State(new_schedule, new_remaining)

    def key(self):

        schedule_tuple = tuple(sorted(self.schedule.items()))
        remaining_tuple = tuple(sorted(self.remaining_tasks.items()))

        return (schedule_tuple, remaining_tuple)