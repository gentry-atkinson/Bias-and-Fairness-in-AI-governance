"""Train a Random Forest regressor to predict ORAS risk scores."""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "travis_county_complete_defendants_df.csv"
)


def main():

    df = pd.read_csv(DATA_PATH, low_memory=False)

    prior = pd.read_csv(
    PROJECT_ROOT / "data/interim/prior_booking_counts_by_defendant.csv"
)

    df = df.merge(
        prior,
        on="person_mni",
        how="left",
    )

    mental = pd.read_csv(
    PROJECT_ROOT / "data/interim/mental_health_features.csv"
    )

    df = df.merge(
        mental,
        on="person_mni",
        how="left",

    )

    df["prior_booking_count"] = df["prior_booking_count"].fillna(0)
    df["three_or_more_prior_bookings"] = (
        df["three_or_more_prior_bookings"]
        .fillna(False)
        .astype(bool)
    )

    df["has_mental_health_flag"] = (
    df["has_mental_health_flag"]
    .fillna(0)
    .astype(int)
)

    df["mental_health_event_count"] = (
        df["mental_health_event_count"]
        .fillna(0)
    )

    feature_columns = [
        "sex",
        "race",
        "ethnicity",
        "age_at_booking",
        "interview_officer",
        "officer_recommendation",
        "attorney_recommendation",
        "attorney_bond",
        "bond_recommendation",
        "charge_code",
        "charge_level",
        "tcud_score",
        "tcud_event",
        "tcud_event_disposition",
        "tcud_score_max",
        "tcud_event_count",
        "prior_booking_count",
        "three_or_more_prior_bookings",
        "has_mental_health_flag",
        "mental_health_event_count",
    ]

    X = df[feature_columns].copy()
    y = df["risk_score"]

    categorical_features = [
        "sex",
        "race",
        "ethnicity",
        "interview_officer",
        "officer_recommendation",
        "attorney_recommendation",
        "attorney_bond",
        "bond_recommendation",
        "charge_code",
        "charge_level",
        "tcud_event",
        "tcud_event_disposition",
    ]

    numeric_features = [
        "age_at_booking",
        "tcud_score",
        "tcud_score_max",
        "tcud_event_count",
        "prior_booking_count",
        "three_or_more_prior_bookings",
        "has_mental_health_flag",
        "mental_health_event_count",
    ]

    for col in categorical_features:
        X[col] = X[col].fillna("MISSING").astype(str)

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                SimpleImputer(strategy="median"),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100,
                    max_depth=20,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\nRandom Forest Results")
    print("---------------------")
    print(f"R²: {r2_score(y_test, predictions):.4f}")
    print(f"MAE: {mean_absolute_error(y_test, predictions):.4f}")

    rmse = mean_squared_error(y_test, predictions) ** 0.5
    print(f"RMSE: {rmse:.4f}")


if __name__ == "__main__":
    main()