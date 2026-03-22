import random

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# -------- DATASET --------

def generate_dataset(n=300):

    X = []
    y = []

    for _ in range(n):

        confidence = random.randint(1, 10)
        stress = random.randint(1, 10)
        workload = random.randint(1, 10)
        available_time = random.randint(1, 10)

        # 🔥 более реалистичная формула
        risk_score = (
            (10 - confidence) * 0.3 +
            stress * 0.4 +
            max(0, workload - available_time) * 0.6
        )

        if risk_score < 3:
            label = 0
        elif risk_score < 6:
            label = 1
        else:
            label = 2

        X.append([confidence, stress, workload, available_time])
        y.append(label)

    return X, y


# -------- TRAIN --------

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