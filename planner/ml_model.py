import random

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# -------- DATASET GENERATION --------

def generate_dataset(n=200):

    X = []
    y = []

    for _ in range(n):

        confidence = random.randint(1, 10)
        stress = random.randint(1, 10)
        workload = random.randint(1, 10)
        available_time = random.randint(1, 10)

        # simple logic for labeling
        risk_score = 0

        if confidence < 4:
            risk_score += 1
        if stress > 7:
            risk_score += 1
        if workload > available_time:
            risk_score += 1

        if risk_score == 0:
            label = 0  # Low
        elif risk_score == 1:
            label = 1  # Medium
        else:
            label = 2  # High

        X.append([confidence, stress, workload, available_time])
        y.append(label)

    return X, y


# -------- TRAIN MODEL --------

def train_model():

    X, y = generate_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2
    )

    model = LogisticRegression(max_iter=200)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)

    print("\n--- ML MODEL ---")
    print("Accuracy:", round(acc, 2))

    return model


# -------- PREDICT --------

def predict_risk(model, data):

    x = [[
        data["confidence"],
        data["stress"],
        data["total_hours"],
        data["available_hours"]
    ]]

    prediction = model.predict(x)[0]

    if prediction == 0:
        return "Low"
    elif prediction == 1:
        return "Medium"
    else:
        return "High"