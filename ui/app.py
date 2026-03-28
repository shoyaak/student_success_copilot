from main import choose_search_algorithm
import streamlit as st

from planner.task import Task
from planner.planner import Planner
from planner.astar import astar

from planner.rule_engine import analyze_schedule

from planner.rule_engine import (
    RuleEngine,
    deadline_rule,
    confidence_rule,
    stress_rule,
    workload_rule,
    interpret_risk
)

from planner.ml_model import train_model, predict_risk

from planner.ai_tutor import AITutor


st.set_page_config(page_title="AI Study Planner", layout="wide")

st.title("📚 AI Study Planner")


# -------- SESSION STATE --------

if "tasks_data" not in st.session_state:
    st.session_state.tasks_data = [
        {"name": "", "hours": 2, "deadline": 3}
    ]

if "schedule" not in st.session_state:
    st.session_state.schedule = None


# -------- TASKS --------

st.header("📝 Tasks")

# add task button
if st.button("➕ Add Task"):
    st.session_state.tasks_data.append(
        {"name": "", "hours": 2, "deadline": 3}
    )

tasks = []

for i, t in enumerate(st.session_state.tasks_data):

    col1, col2, col3 = st.columns(3)

    t["name"] = col1.text_input("Task", value=t["name"], key=f"name_{i}")
    t["hours"] = col2.number_input("Hours", 1, 10, t["hours"], key=f"hours_{i}")
    t["deadline"] = col3.slider(
        "Deadline (1 = Mon ... 7 = Sun)",
        1, 7,
        t["deadline"],
        key=f"deadline_{i}"
    )

    if t["name"]:
        tasks.append(Task(t["name"], t["hours"], t["deadline"]))


# -------- CALENDAR --------

st.header("📅 Weekly Calendar")

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
times = ["09:00", "11:00", "13:00", "15:00"]

if "calendar" not in st.session_state:
    st.session_state.calendar = {
        (d, t): False
        for d in range(len(days))
        for t in range(len(times))
    }

calendar = st.session_state.calendar
available_slots = []

# header
cols = st.columns(len(days) + 1)
cols[0].write("")
for i, day in enumerate(days):
    cols[i+1].write(f"**{day}**")

# grid
for t_idx, time in enumerate(times):

    cols = st.columns(len(days) + 1)
    cols[0].write(f"**{time}**")

    for d_idx in range(len(days)):

        key = f"{d_idx}_{t_idx}"

        label = "🟩" if calendar[(d_idx, t_idx)] else "⬜"

        if cols[d_idx+1].button(label, key=key):
            calendar[(d_idx, t_idx)] = not calendar[(d_idx, t_idx)]

        if calendar[(d_idx, t_idx)]:
            available_slots.append((d_idx+1, t_idx+1))

st.header("🧠 Your State")

col1, col2 = st.columns(2)

confidence = col1.slider("Confidence level", 1, 10, 5)
stress = col2.slider("Stress level", 1, 10, 5)

# -------- ACTION BUTTONS --------

col1, col2, col3 = st.columns(3)

generate = col1.button("🚀 Generate Plan")
reset = col2.button("🧹 Reset")
regenerate = col3.button("🔄 Regenerate")


# reset
if reset:
    st.session_state.schedule = None


# generate
if generate or regenerate:

    if not tasks:
        st.warning("Add tasks")

    elif not available_slots:
        st.warning("Select slots")

    else:

        planner = Planner(tasks, available_slots)
        result, nodes = astar(planner)

        if result is None:
            st.error("❌ Not enough time")
        else:
            st.session_state.schedule = result.state.schedule

            # -------- BUILD DATA --------

            total_hours = sum(t.hours for t in tasks)
            available_hours = len(available_slots)

            if len(tasks) == 0:
              st.stop()

            urgent_task = min(tasks, key=lambda t: t.deadline_day).name
            min_deadline = min(t.deadline_day for t in tasks)

            data = {
                "days_to_deadline": min_deadline - 1,
                "confidence": confidence,
                "stress": stress,
                "total_hours": total_hours,
                "available_hours": available_hours,
                "urgent_task": urgent_task
            }

            analysis = analyze_schedule(tasks, st.session_state.schedule)
            data.update(analysis)
            st.session_state.data = data


            # -------- RULE ENGINE --------

            engine = RuleEngine()
            engine.add_rule(deadline_rule)
            engine.add_rule(confidence_rule)
            engine.add_rule(stress_rule)
            engine.add_rule(workload_rule)

            rule_score = engine.evaluate(data)
            rule_risk = interpret_risk(rule_score)


            # -------- ML --------

            model = train_model()
            ml_risk = predict_risk(model, data)


            # -------- COMBINE --------

            def combine_risk(rule_score, ml_risk):

                ml_map = {"Low": 0, "Medium": 1, "High": 2}
                ml_val = ml_map[ml_risk]

                if rule_score < 1:
                    rule_val = 0
                elif rule_score < 2:
                    rule_val = 1
                else:
                    rule_val = 2

                final_val = round(rule_val * 0.6 + ml_val * 0.4)

                return ["Low", "Medium", "High"][final_val]


            final_risk = combine_risk(rule_score, ml_risk)


            # сохраняем в state
            st.session_state.risk = {
                "rule": rule_risk,
                "ml": ml_risk,
                "final": final_risk,
                "reasons": engine.get_explanations()
            }
            st.success("Plan generated!")
            st.write("Nodes expanded:", nodes)


# -------- OUTPUT --------

if st.session_state.schedule:

    st.subheader("📅 Schedule")

    schedule = st.session_state.schedule

    cols = st.columns(len(days) + 1)
    cols[0].write("")
    for i, day in enumerate(days):
        cols[i+1].write(f"**{day}**")

    for t_idx, time in enumerate(times):

        cols = st.columns(len(days) + 1)
        cols[0].write(f"**{time}**")

        for d_idx in range(len(days)):

            if (d_idx+1, t_idx+1) in schedule:
                cols[d_idx+1].success(schedule[(d_idx+1, t_idx+1)])
            elif calendar[(d_idx, t_idx)]:
                cols[d_idx+1].info("Free")
            else:
                cols[d_idx+1].write("")

def generate_summary(final_risk, reasons):

    if final_risk == "High":
        return {
            "title": "🔴 You are at risk!",
            "text": "Your workload is too high and deadlines are close.",
            "advice": "Reduce tasks or start earlier."
        }

    elif final_risk == "Medium":
        return {
            "title": "🟡 Be careful",
            "text": "Your plan is possible but requires consistency.",
            "advice": "Stay disciplined and monitor progress."
        }

    else:
        return {
            "title": "🟢 You are on track!",
            "text": "Your study plan looks balanced and manageable.",
            "advice": "Keep going and stay consistent."
        }
    

# -------- RISK OUTPUT --------

if "risk" in st.session_state:

  st.divider()
  st.header("⚠ Risk Analysis")

  risk = st.session_state.risk

  summary = generate_summary(risk["final"], risk["reasons"]) # type: ignore

  st.subheader(summary["title"])
  st.write(summary["text"])


  col1, col2, col3 = st.columns(3)

  col1.metric("Rule", risk["rule"])
  col2.metric("ML", risk["ml"])
  col3.metric("Final", risk["final"])


  st.subheader("📌 Why?")

  for r in risk["reasons"]:
      st.write(f"- {r}")


  st.subheader("💡 What should you do?")

  if risk["final"] == "High":
      st.error(summary["advice"])
  elif risk["final"] == "Medium":
      st.warning(summary["advice"])
  else:
      st.success(summary["advice"])

st.subheader("🔍 Search Strategy")

algo, reason = choose_search_algorithm(tasks, available_slots)

st.write(f"**Selected algorithm:** {algo}")
st.write(f"**Reason:** {reason}")


# -------- AI INTEGRATION --------
if "schedule" in st.session_state and "risk" in st.session_state:

    from planner.ai_tutor import AITutor

    tutor = AITutor()

    st.divider()
    st.header("🧠 AI Tutor")

    schedule = st.session_state.schedule
    risk = st.session_state.risk
    data = st.session_state.data

    st.subheader("📊 Plan Explanation")
    for e in tutor.explain_plan(schedule):
        st.write(f"- {e}")

    st.subheader("⚙️ Workload Insights")
    for w in tutor.explain_workload(data):
        st.write(f"- {w}")

    st.subheader("💡 Smart Advice")
    for a in tutor.generate_advice(risk, data):
        st.write(f"- {a}")

else:
    st.divider()
    st.header("🧠 AI Tutor")
    st.info("Generate a plan to see AI Tutor insights")