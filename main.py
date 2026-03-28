from datetime import date
from planner.task import Task
from planner.planner import Planner
from planner.astar import astar
from planner.bfs import bfs
from planner.ml_model import train_model, predict_risk
from planner.ai_tutor import AITutor

from planner.rule_engine import RuleEngine
from planner.rule_engine import (
    deadline_rule,
    confidence_rule,
    stress_rule,
    workload_rule,
    late_task_rule,
    overload_day_rule,
    weekend_rule,
    analyze_schedule,
    check_missing_data,
    interpret_risk
)



# -------- UI HELPERS --------

def section(title):
    print("\n" + "=" * 40)
    print(title)
    print("=" * 40)


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
        grouped.setdefault(day, []).append((slot, task))

    for day in sorted(grouped):
        print(f"\n📅 {days_map[day]}")
        for slot, task in sorted(grouped[day]):
            print(f"  ⏰ Slot {slot:<2} | {task}")


def combine_risk(rule_score, ml_risk):

    ml_map = {
        "Low": 0,
        "Medium": 1,
        "High": 2
    }

    ml_value = ml_map.get(ml_risk, 1)

    if rule_score < 1:
        rule_value = 0
    elif rule_score < 2:
        rule_value = 1
    else:
        rule_value = 2

    final_value = round((rule_value * 0.6 + ml_value * 0.4))

    reverse_map = {
        0: "Low",
        1: "Medium",
        2: "High"
    }

    return reverse_map[final_value]


# -------- DEMO SCENARIO --------

def run_scenario(name, data, engine):
    print(f"\n--- {name} ---")

    score = engine.evaluate(data)
    risk = interpret_risk(score)

    print(f"Score: {round(score, 2)}")
    print(f"Risk: {risk}")

    print("Reasons:")
    for e in engine.get_explanations():
        print("  •", e)

def choose_search_algorithm(tasks, available_slots):

    complexity = len(tasks) * len(available_slots)

    if complexity <= 10:
        return "BFS", "Problem is small, BFS is sufficient"
    else:
        return "ASTAR", "Problem is complex, A* is more efficient due to heuristic"


# -------- MAIN --------

def main():

    print("\n🎓 Student Success Copilot (CLI Demo)")
    print("Note: Full version available in Streamlit UI\n")

    # -------- INPUT DATA --------

    section("INPUT DATA")

    tasks = [
        Task("Math", 2, 3),
        Task("Physics", 2, 5)
    ]

    for t in tasks:
        print(f"- {t.name} | hours: {t.hours} | deadline: day {t.deadline_day}")

    available_slots = [
        (1, 1), (1, 2),
        (2, 1), (2, 2),
        (3, 1),
        (4, 1)
    ]

    print(f"\nAvailable slots: {len(available_slots)}")


    # -------- PLANNER --------

    section("SEARCH STRATEGY")

    algo, reason = choose_search_algorithm(tasks, available_slots)

    print(f"Selected algorithm: {algo}")
    print(f"Reason: {reason}")

    section("PLANNER")

    planner = Planner(tasks, available_slots)

    if algo == "BFS":
        result, nodes = bfs(planner)
    else:
        result, nodes = astar(planner)

    
    if not result:
        print("❌ No valid schedule found")
        return

    print(f"Nodes expanded: {nodes}")

    section("SCHEDULE")
    format_schedule(result.state.schedule)

    # -------- BASE DATA --------

    data = {
        "days_to_deadline": 1,
        "confidence": 5,
        "stress": 5,
        "total_hours": sum(t.hours for t in tasks),
        "available_hours": len(result.state.schedule),
        "urgent_task": min(tasks, key=lambda t: t.deadline_day).name,
    }

    analysis = analyze_schedule(tasks, result.state.schedule)
    data.update(analysis)

    print("\n📊 User Profile:")
    print(f"Stress level: {data['stress']}/10")
    print(f"Confidence: {data['confidence']}/10")

    # -------- RULE ENGINE --------

    section("RULE-BASED ANALYSIS")

    engine = RuleEngine()

    engine.add_rule(deadline_rule)
    engine.add_rule(confidence_rule)
    engine.add_rule(stress_rule)
    engine.add_rule(workload_rule)

    engine.add_rule(late_task_rule)
    engine.add_rule(overload_day_rule)
    engine.add_rule(weekend_rule)

    questions = check_missing_data(data)

    if questions:
        print("⚠️ Missing data:")
        for q in questions:
            print("-", q)

    score = engine.evaluate(data)

    print(f"\nScore: {round(score,2)}")

    print("\n🧠 Why this decision was made:")
    for e in engine.get_explanations():
        print(f"  • {e}")

    risk_level = interpret_risk(score)

    print(f"\nRule-based Risk Level: {risk_level}")

    # -------- DEMO (LOW / MED / HIGH) --------

    section("RULE ENGINE DEMO")

    data_low = data.copy()
    data_low.update({
        "days_to_deadline": 5,
        "confidence": 9,
        "stress": 2
    })

    data_medium = data.copy()
    data_medium.update({
        "days_to_deadline": 2,
        "confidence": 5,
        "stress": 5
    })

    data_high = data.copy()
    data_high.update({
        "days_to_deadline": 1,
        "confidence": 2,
        "stress": 9,
        "total_hours": 10,
        "available_hours": 4,
        "late_tasks": ["Math"],
        "heavy_days": [1, 2],
        "weekend_tasks": 2
    })

    run_scenario("LOW RISK", data_low, engine)
    run_scenario("MEDIUM RISK", data_medium, engine)
    run_scenario("HIGH RISK", data_high, engine)

    # -------- ML --------

    section("ML PREDICTION")

    model = train_model()
    ml_risk = predict_risk(model, data)

    print(f"ML Predicted Risk: {ml_risk}")

    # -------- FINAL --------

    section("FINAL DECISION")

    final_risk = combine_risk(score, ml_risk)

    print("\n🎯 SYSTEM OUTPUT")
    print(f"Predicted Risk Level: {final_risk}")

    if final_risk == "High":
        print("⚠️ Recommendation: Reduce workload or prioritize urgent tasks")
    elif final_risk == "Medium":
        print("⚡ Recommendation: Monitor stress and adjust schedule")
    else:
        print("✅ Recommendation: Current plan is manageable")

    # -------- AI TUTOR --------

    section("AI TUTOR")

    tutor = AITutor()

    schedule = result.state.schedule
    risk = {"final": final_risk}

    print("\n📊 Plan Explanation:")
    for e in tutor.explain_plan(schedule):
        print(f"  • {e}")

    print("\n⚙️ Workload Insights:")
    for w in tutor.explain_workload(data):
        print(f"  • {w}")

    print("\n💡 Smart Advice:")
    for a in tutor.generate_advice(risk, data):
        print(f"  • {a}")

if __name__ == "__main__":
    main()




