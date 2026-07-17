from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from utils import clean_race_labels

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "travis_county_complete_defendants_df.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(exist_ok=True)
FIGURE_DIR.mkdir(exist_ok=True)

def load_data():

    print(f"Loading {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    df = clean_race_labels(df)

    print(f"Loaded {len(df):,} rows")

    return df



def summarize_race_population(df):

    summary = (
        df.groupby("race")
        .size()
        .reset_index(name="count")
    )

    summary["percent"] = (
        summary["count"]
        / summary["count"].sum()
        * 100
    ).round(2)

    summary = summary.sort_values(
        "count",
        ascending=False,
    )

    return summary



def plot_population(summary):

    fig, ax = plt.subplots(figsize=(8,5))

    bars = ax.bar(
        summary["race"],
        summary["percent"],
    )

    ax.set_ylabel("Percent of Population")
    ax.set_xlabel("Race")
    ax.set_title("Population Distribution by Race")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(axis="y", alpha=0.25)

    for bar in bars:

        height = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width()/2,
            height,
            f"{height:.2f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR / "population_summary_race.png",
        dpi=300,
    )

    plt.close()
    
    
def run():

    df = load_data()

    summary = summarize_race_population(df)

    print(summary)

    summary.to_csv(
        OUTPUT_DIR / "population_summary.csv",
        index=False,
    )

    plot_population(summary)

    print("\nSaved population_summary.csv")
    print("Saved population_summary_race.png")

    return summary


if __name__ == "__main__":
    run()
    