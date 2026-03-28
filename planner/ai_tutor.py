class AITutor:

    def explain_plan(self, schedule):
        explanations = []

        day_map = {
            1: "Monday", 2: "Tuesday", 3: "Wednesday",
            4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
        }

        # grouping by days
        days = {}
        for (day, slot), subject in schedule.items():
            days.setdefault(day, []).append(subject)

        for day, subjects in days.items():
            unique_subjects = set(subjects)

            if len(unique_subjects) == 1:
                explanations.append(
                    f"{day_map[day]} is focused on {list(unique_subjects)[0]}, "
                    f"which helps deep concentration and reduces context switching."
                )
            else:
                explanations.append(
                    f"{day_map[day]} mixes subjects, which helps maintain engagement "
                    f"and prevents fatigue."
                )

        explanations.append(
            "Overall, the plan distributes workload across the week to avoid overload."
        )

        return explanations

    def generate_advice(self, risk, data):
        advice = []

        if risk["final"] == "High":
            advice.append("Your schedule is overloaded. Consider reducing task volume.")
            advice.append("Start with the most urgent task earlier in the week.")

        elif risk["final"] == "Medium":
            advice.append("Your plan is feasible but requires discipline.")
            advice.append("Avoid procrastination to stay on track.")

        else:
            advice.append("Your plan is well-balanced. Maintain consistency.")

        # personalization
        if data.get("stress", 0) > 7:
            advice.append("High stress detected — include short breaks between sessions.")

        if data.get("confidence", 10) < 4:
            advice.append("Low confidence — start with easier tasks to build momentum.")

        return advice

    def explain_workload(self, data):
        explanations = []

        if data["total_hours"] > data["available_hours"]:
            explanations.append(
                "The required study hours exceed available time slots, which increases risk."
            )

        if data["days_to_deadline"] < 2:
            explanations.append(
                "Deadlines are very close, requiring more intensive scheduling."
            )

        if data.get("stress", 0) > 7:
            explanations.append(
                "High stress levels may reduce productivity and focus."
            )

        return explanations