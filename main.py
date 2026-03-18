from datetime import date
from planner.task import Task
from planner.planner import Planner
from planner.astar import astar
from planner.ml_model import train_model, predict_risk

from planner.rule_engine import RuleEngine
from planner.rule_engine import (
    deadline_rule,
    confidence_rule,
    stress_rule,
    workload_rule,
    check_missing_data,
    interpret_risk
)


# -------- FORMAT SCHEDULE --------

def format_schedule(schedule):

    days_map = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }

    grouped = {}

    for (day, slot), task in schedule.items():

        if day not in grouped:
            grouped[day] = []

        grouped[day].append((slot, task))

    for day in sorted(grouped.keys()):

        print(days_map[day] + ":")

        for slot, task in sorted(grouped[day]):
            print(f"  Slot {slot} → {task}")

        print()

def combine_risk(rule_score, ml_risk):

    # переводим ML в число
    ml_map = {
        "Low": 0,
        "Medium": 1,
        "High": 2
    }

    ml_value = ml_map[ml_risk]

    # нормализуем rule_score (примерно)
    if rule_score < 1:
        rule_value = 0
    elif rule_score < 2:
        rule_value = 1
    else:
        rule_value = 2

    # комбинируем
    final_value = round((rule_value * 0.6 + ml_value * 0.4))

    # обратно в label
    reverse_map = {
        0: "Low",
        1: "Medium",
        2: "High"
    }

    return reverse_map[final_value]


# -------- MAIN --------

def main():

    # --- INPUT DATA ---

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

    # --- PLANNER ---

    planner = Planner(tasks, available_slots)

    result, nodes = astar(planner)

    print("Nodes expanded:", nodes)
    print()

    print("Schedule:")
    format_schedule(result.state.schedule)


    # --- RULE ENGINE ---

    print("\n--- RULE ENGINE ---")

    engine = RuleEngine()

    engine.add_rule(deadline_rule)
    engine.add_rule(confidence_rule)
    engine.add_rule(stress_rule)
    engine.add_rule(workload_rule)

    # TEST DATA
    data = {
        "days_to_deadline": 1,
        "confidence": 2,
        "stress": 8,
        "total_hours": 6,
        "available_hours": 4
    }

    # BACKWARD CHAINING
    questions = check_missing_data(data)

    if questions:
        print("Need more info:")
        for q in questions:
            print("-", q)

    # FORWARD CHAINING
    score = engine.evaluate(data)

    print("\nRule-based score:", score)

    print("Reasons:")
    for e in engine.get_explanations():
        print("-", e)

    risk_level = interpret_risk(score)

    print("\nFinal Risk Level:", risk_level)

    # -------- ML --------

    model = train_model()

    ml_risk = predict_risk(model, data)

    print("\nML Predicted Risk:", ml_risk)

    final_risk = combine_risk(score, ml_risk)

    print("\n--- FINAL DECISION ---")
    print("Final Combined Risk:", final_risk)



# -------- RUN --------

if __name__ == "__main__":
    main()


