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
    days = data.get("days_to_deadline", 10)

    if days <= 1:
        return 1.0, f"Deadline for '{data.get('urgent_task', 'task')}' is critical"
    elif days <= 3:
        return 0.5, f"Deadline for '{data.get('urgent_task', 'task')}' is close"

    return None


def confidence_rule(data):
    conf = data.get("confidence", 10)

    if conf <= 3:
        return 0.7, "Low confidence may slow down progress"
    elif conf <= 6:
        return 0.3, "Moderate confidence"

    return None


def stress_rule(data):
    stress = data.get("stress", 0)

    if stress >= 8:
        return 0.8, "High stress level detected"
    elif stress >= 5:
        return 0.4, "Moderate stress"

    return None


def workload_rule(data):
    total = data.get("total_hours", 0)
    available = data.get("available_hours", 1)

    diff = total - available

    if diff > 3:
        return 1.0, "Severely overloaded schedule"
    elif diff > 0:
        return 0.5, "Workload slightly exceeds available time"

    return None


def late_task_rule(data):
    late = data.get("late_tasks", [])

    if len(late) >= 2:
        return 1.5, f"Multiple late tasks: {late}"
    elif late:
        return 0.8, f"Task scheduled after deadline: {late}"

    return None


def overload_day_rule(data):
    heavy = data.get("heavy_days", [])

    if heavy:
        return 0.5, "Some days are overloaded"

    return None


def weekend_rule(data):
    weekend = data.get("weekend_tasks", 0)

    if weekend > 0:
        return 0.3, "Study sessions planned on weekend"

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
    elif score < 2:
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

        if day > task.deadline_day:
            late_tasks.append(task_name)

        overload_days[day] = overload_days.get(day, 0) + 1

        if day >= 6:
            weekend_tasks += 1

    heavy_days = [d for d, c in overload_days.items() if c > 3]

    return {
        "late_tasks": late_tasks,
        "heavy_days": heavy_days,
        "weekend_tasks": weekend_tasks
    }