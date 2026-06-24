"""Train a linear regression model to predict risk scores."""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "travis_county_pretrial_analysis_df.csv"
)


def main() -> None:
    """Train and evaluate a risk score prediction model."""

    df = pd.read_csv(DATA_PATH)

    df = df.dropna(subset=["risk_score"])

    feature_columns = [
    "sex",
    "race",
    "ethnicity",
    "zip_code",
    "age_at_booking",
    "age_group",
    "bond_granted_flag",
    "bond_amount",
    "bond_type",
    "bond_status",
    "charge_code",
    "charge_level",
    "judge",
]


    X = df[feature_columns]
    y = df["risk_score"]

    categorical_features = [
    "sex",
    "race",
    "ethnicity",
    "zip_code",
    "age_group",
    "bond_type",
    "bond_status",
    "charge_code",
    "charge_level",
    "judge",
]

    numeric_features = [
    "age_at_booking",
    "bond_granted_flag",
    "bond_amount",
    ]

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
                        (
                            "imputer",
                            SimpleImputer(strategy="most_frequent"),
                        ),
                        (
                            "encoder",
                            OneHotEncoder(handle_unknown="ignore"),
                        ),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", LinearRegression()),
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

    print(f"R²: {r2_score(y_test, predictions):.4f}")
    print(f"MAE: {mean_absolute_error(y_test, predictions):.4f}")

    rmse = mean_squared_error(y_test, predictions) ** 0.5
    print(f"RMSE: {rmse:.4f}")

    feature_names = model.named_steps[
        "preprocessor"
    ].get_feature_names_out()

    coefficients = model.named_steps[
        "regressor"
    ].coef_

    importance_df = (
        pd.DataFrame(
            {
                "feature": feature_names,
                "coefficient": coefficients,
            }
        )
        .assign(abs_coefficient=lambda x: x["coefficient"].abs())
        .sort_values("abs_coefficient", ascending=False)
    )

    print("\nTop 20 most influential features:")
    print(
        importance_df[
            ["feature", "coefficient"]
        ].head(20).to_string(index=False)
    )


if __name__ == "__main__":
    main()

