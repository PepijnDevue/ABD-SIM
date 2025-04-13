import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    mo.md(f"""
    # Evacuation Analysis

    This document will analyse the effects that the following settings have on the evacuation of HL15-5:

    - **Voting method**: The way clusters vote for the best target exit
    - **Abled to Disabled Ratio**: The ratio of abled to disabled people in the simulation
    - **Mean Morality**: The mean morality of the abled people
    - **Morality std**: The standard deviation of the morality of the abled people
    """)
    return mo, pd, plt, sns


@app.cell(hide_code=True)
def _(mo, pd):
    data = pd.read_csv("sim_data.csv")

    mo.md(f"""
    ## Data Overview

    **Unique Setting Values**

    - **Abled to Disabled Ratio**: `{data["abled_to_disabled_ratio"].unique()}`
    - **Mean Morality**: `{data["morality_mean"].unique()}`
    - **Morality std**: `{data["morality_std"].unique()}`
    - **Voting method**: `{data["voting_method"].unique()}`
    """)
    return (data,)


@app.cell(hide_code=True)
def _(data):
    data
    return


@app.cell(hide_code=True)
def _(data, plt, sns):
    _df = data
    _df = _df.groupby(["morality_mean", "morality_std"], dropna=False).mean(numeric_only=True)
    _df = _df[["avg_evac_time", "total_evac_time", "num_agents_left"]]
    _df = _df.reset_index()

    def _():
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
        metrics = ["avg_evac_time", "total_evac_time", "num_agents_left"]
    
        for ax, metric in zip(axes, metrics):
            pivot = _df.pivot(index="morality_std", columns="morality_mean", values=metric)
            sns.heatmap(pivot, annot=True, fmt=".2f", cmap="viridis", ax=ax)
            ax.set_title(metric.replace("_", " ").title())
            ax.set_xlabel("Morality Mean")
            ax.set_ylabel("Morality Std")
    
        plt.suptitle("Evacuation Metrics by Morality Mean and Std", fontsize=26)
        plt.show()

    _()
    return


@app.cell(hide_code=True)
def _(data, plt, sns):
    _fig, _axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    _metrics = ["avg_evac_time", "total_evac_time", "num_agents_left"]

    for _ax, _metric in zip(_axes, _metrics):
        sns.boxplot(data=data, x="abled_to_disabled_ratio", y=_metric, ax=_ax)
        _ax.set_title(_metric.replace("_", " ").title())
        _ax.set_xlabel("Abled to Disabled Ratio")
        _ax.set_ylabel(_metric.replace("_", " ").title())
        _ax.grid(True)

    plt.suptitle("Evacuation Metric Distributions by Abled to Disabled Ratio", fontsize=26)
    plt.show()
    return


@app.cell(hide_code=True)
def _(data, mo, plt, sns):
    # Create a correlation matrix of the data using seaborn

    sns.heatmap(data.drop(columns=["evac_times", "num_agents", "voting_method"]).corr(), annot=True, cmap="coolwarm", center=0)
    plt.show()

    mo.md(f"""
    ## Correlation Matrix
    """)

    return


if __name__ == "__main__":
    app.run()
