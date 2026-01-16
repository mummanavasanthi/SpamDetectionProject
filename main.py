from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

app = FastAPI(title="SMS & Email Spam Detection")

# ✅ Static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


# ✅ Load dataset safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "spam.csv")

try:
    df = pd.read_csv(CSV_PATH, encoding="latin-1")
    df = df[["v1", "v2"]]
    df.columns = ["label", "message"]
except Exception as e:
    print("❌ Dataset error:", e)
    df = None


# ✅ Train Model
accuracy = 0

if df is not None:
    X = df["message"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english")),
        ("clf", MultinomialNB())
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
else:
    model = None


class PredictRequest(BaseModel):
    input_type: str
    text: str


@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


@app.post("/predict")
def predict(data: PredictRequest):
    try:
        if model is None:
            return JSONResponse(content={"error": "Model not loaded! Check spam.csv file."}, status_code=500)

        text = data.text.strip()
        input_type = data.input_type.lower().strip()

        if not text:
            return {"error": "Text is empty!"}

        # ✅ Rule layer (Email spam detection)
        spam_keywords = [
            "apply now", "shortlisted", "internship", "stipend",
            "certificate", "lor", "hiring team", "incentives",
            "click here", "limited time", "monthly stipend",
            "opportunity", "warm regards", "register now", "delegate program"
        ]

        lower_text = text.lower()
        keyword_matches = sum(1 for k in spam_keywords if k in lower_text)

        if input_type == "email" and keyword_matches >= 2:
            return {
                "prediction": "SPAM",
                "accuracy": round(accuracy * 100, 2),
                "probability": 95.0,
                "type": "EMAIL"
            }

        # ✅ ML prediction
        pred = model.predict([text])[0]

        proba = model.predict_proba([text])[0]
        classes = list(model.classes_)
        spam_index = classes.index("spam")
        spam_prob = round(proba[spam_index] * 100, 2)

        if pred == "spam":
            return {
                "prediction": "SPAM",
                "accuracy": round(accuracy * 100, 2),
                "probability": spam_prob,
                "type": input_type.upper()
            }
        else:
            return {
                "prediction": "NOT SPAM",
                "accuracy": round(accuracy * 100, 2),
                "probability": spam_prob,
                "type": input_type.upper()
            }

    except Exception as e:
        print("❌ Prediction error:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
