from planner.task import Task
from planner.planner import Planner
from planner.astar import astar


tasks = [
    Task("Math", 2, 3),
    Task("Physics", 2, 5)
]

available_slots = [
    (1,1),(1,2),
    (2,1),(2,2),
    (3,1),
    (4,1)
]

planner = Planner(tasks, available_slots)

result, nodes = astar(planner)

print("Nodes expanded:", nodes)

print("Schedule:")

for k,v in result.state.schedule.items():
    print(k, "->", v)