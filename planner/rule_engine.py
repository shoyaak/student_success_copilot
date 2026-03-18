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
        return 0.8, "Deadline is very close"

    return None


def confidence_rule(data):

    if data["confidence"] <= 3:
        return 0.7, "Low confidence increases risk"

    return None


def stress_rule(data):

    if data["stress"] >= 7:
        return 0.6, "High stress level detected"

    return None


def workload_rule(data):

    if data["total_hours"] > data["available_hours"]:
        return 0.9, "Workload exceeds available time"

    return None


# -------- BACKWARD CHAINING --------

def check_missing_data(data):

    questions = []

    if "confidence" not in data:
        questions.append("What is your confidence level (1-10)?")

    if "stress" not in data:
        questions.append("What is your stress level (1-10)?")

    return questions


# -------- RISK INTERPRETATION --------

def interpret_risk(score):

    if score < 1:
        return "Low"
    elif score < 2:
        return "Medium"
    else:
        return "High"