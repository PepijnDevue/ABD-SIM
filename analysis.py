import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt

    mo.md(f"""
    # Evacuation Analysis

    This document will analyse the effects that the following settings have on the evacuation of HL15-5:

    - **Voting method**: The way clusters vote for the best target exit
    - **Abled to Disabled Ratio**: The ratio of abled to disabled people in the simulation
    - **Mean Morality**: The mean morality of the abled people
    - **Morality std**: The standard deviation of the morality of the abled people
    """)
    return mo, pd, plt


@app.cell(hide_code=True)
def _(mo, pd):
    data = pd.read_csv("evacuation_times.csv")

    _cols = ["abled_to_disabled_ratio", "morality_mean", "morality_std", "voting_method"]

    mo.md(f"""
    ## Data Overview

    {data.drop(columns=["evac_times"]).sample(10).to_markdown(index=False)}

    **Unique Setting Values**

    - **Abled to Disabled Ratio**: `{data["abled_to_disabled_ratio"].unique()}`
    - **Mean Morality**: `{data["morality_mean"].unique()}`
    - **Morality std**: `{data["morality_std"].unique()}`
    - **Voting method**: `{data["voting_method"].unique()}`

    ## Data Analysis
    """)
    return (data,)


@app.cell(hide_code=True)
def _(data, plt):
    # 3 bar plots (one per voting method) of the mean evacuation time for each setting
    def hist_plot(compare: str, y: str):
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(f"{y} per {compare}")
        for i, unique_compare in enumerate(data[compare].unique()):
            subset = data[data[compare] == unique_compare]
            subset.plot(kind="hist", ax=axs[i], y=y, alpha=0.5)
            axs[i].set_title(f"{compare} = {unique_compare}")

        plt.tight_layout()

        plt.show()

    for comp in ["voting_method",
                 "abled_to_disabled_ratio",
                 "morality_mean",
                 "morality_std",]:
        hist_plot(comp, "total_evac_time")
        hist_plot(comp, "avg_evac_time")
        hist_plot(comp, "num_agents_left")
    return comp, hist_plot


@app.cell(hide_code=True)
def _(data, mo, pd):
    # Show average total_evac_time, avg_evac_time, num_agents_left for each setting
    settings = ["voting_method",
                "abled_to_disabled_ratio",
                "morality_mean",
                "morality_std"]

    for setting in settings:
        avgs = pd.DataFrame({
            "total_evac_time": data.groupby(setting)["total_evac_time"].mean(),
            "avg_evac_time": data.groupby(setting)["avg_evac_time"].mean(),
            "num_agents_left": data.groupby(setting)["num_agents_left"].mean()
        })
        avgs = avgs.reset_index()
        mo.output.append(mo.md(f"""**{setting.capitalize()} Analysis**
    
        {avgs.to_markdown()}
        """))
    return avgs, setting, settings


if __name__ == "__main__":
    app.run()
