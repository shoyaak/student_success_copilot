class Task:

    def __init__(self, name, hours, deadline_day):
        self.name = name
        self.hours = hours
        self.deadline_day = deadline_day

    def __repr__(self):
        return f"Task({self.name}, {self.hours}h, deadline={self.deadline_day})"