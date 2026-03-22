class RuleEngine:

    def __init__(self):
        self.rules = []
        self.explanations = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def evaluate(self, data):

        self.explanations = []
        score = 0

        for rule in self.rules:

            result = rule(data)

            if result:
                value, explanation = result
                score += value
                self.explanations.append(explanation)

        return score

    def get_explanations(self):
        return self.explanations


# -------- RULES --------

def deadline_rule(data):

    if data["days_to_deadline"] <= 2:
        return 0.8, f"Deadline for '{data['urgent_task']}' is very close"

    return None


def confidence_rule(data):

    if data["confidence"] <= 3:
        return 0.7, "Low confidence may slow down progress"

    return None


def stress_rule(data):

    if data["stress"] >= 7:
        return 0.6, "High stress level detected"

    return None


def workload_rule(data):

    if data["total_hours"] > data["available_hours"]:
        return 0.9, "Workload exceeds available study time"

    return None


# 🔥 НОВОЕ — анализ расписания

def late_task_rule(data):

    if data["late_tasks"]:
        return 1.5, f"Tasks scheduled after deadline: {data['late_tasks']}"

    return None


def overload_day_rule(data):

    if data["heavy_days"]:
        return 0.7, "Some days are overloaded"

    return None


# 🔥 НОВОЕ — выходные 😄

def weekend_rule(data):

    if data["weekend_tasks"] > 0:
        return 0.5, "You planned study sessions on weekend (rest is important!)"

    return None


# -------- BACKWARD CHAINING --------

def check_missing_data(data):

    questions = []

    if "confidence" not in data:
        questions.append("What is your confidence level (1-10)?")

    if "stress" not in data:
        questions.append("What is your stress level (1-10)?")

    return questions


# -------- INTERPRET --------

def interpret_risk(score):

    if score < 1:
        return "Low"
    elif score < 2.5:
        return "Medium"
    else:
        return "High"


# -------- ANALYZE SCHEDULE --------

def analyze_schedule(tasks, schedule):

    late_tasks = []
    overload_days = {}
    weekend_tasks = 0

    for (day, slot), task_name in schedule.items():

        task = next(t for t in tasks if t.name == task_name)

        # дедлайн нарушен
        if day > task.deadline_day:
            late_tasks.append(task_name)

        # перегрузка
        overload_days[day] = overload_days.get(day, 0) + 1

        # выходные (6,7)
        if day >= 6:
            weekend_tasks += 1

    heavy_days = [d for d, c in overload_days.items() if c > 3]

    return {
        "late_tasks": late_tasks,
        "heavy_days": heavy_days,
        "weekend_tasks": weekend_tasks
    }