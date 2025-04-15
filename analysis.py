import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt

    mo.md(f"""
    # Evacuation Analysis

    This document will analyse the effects that the following settings have on the evacuation of HL15-5:

    **Input variables:**

    - **Voting method**: The way clusters vote for the best target exit
    - **Abled to Disabled Ratio**: The ratio of abled to disabled people in the simulation
    - **Mean Morality**: The mean morality of the abled people
    - **Morality std**: The standard deviation of the morality of the abled people

    **Metric values:**

    - **Average Evacuation Time**: The time a student needs to evacuate on average
    - **Total Evacuation Time**: The time all students need to evacuate (excluding those left behind)
    - **Number of Students Left Behind**: The amount of students that remained helpless and were left behind
    """)
    return alt, mo, pd


@app.cell(hide_code=True)
def _(mo, pd):
    data = pd.read_csv("sim_data.csv")

    mo.md(f"""
    **Unique Setting Values**

    - **Abled to Disabled Ratio**: `{data["abled_to_disabled_ratio"].unique()}`
    - **Mean Morality**: `{data["morality_mean"].unique()}`
    - **Morality std**: `{data["morality_std"].unique()}`
    - **Voting method**: `{data["voting_method"].unique()}`
    """)
    return (data,)


@app.cell(hide_code=True)
def _(data, mo):
    mo.output.append(mo.md("""
    ## Data Exploration

    Here we can see the data we are working with
    """))
    mo.output.append(data)
    return


@app.cell(hide_code=True)
def _(alt, data, mo):
    def _corr_plot():
        corr_matrix = data.drop(columns=["evac_times", "num_agents", "voting_method"]).corr()

        corr_matrix_melted = corr_matrix.reset_index().melt(id_vars='index')
        corr_matrix_melted.columns = ['x', 'y', 'corr']

        x_vars = ["abled_to_disabled_ratio", "morality_mean", "morality_std"]
        y_vars = ["avg_evac_time", "total_evac_time", "num_agents_left"]
        corr_matrix_filtered = corr_matrix_melted[
            corr_matrix_melted["x"].isin(x_vars) &
            corr_matrix_melted["y"].isin(y_vars)
        ]

        heatmap = alt.Chart(corr_matrix_filtered).mark_rect().encode(
            x=alt.X('x:N', title=None, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('y:N', title=None, axis=alt.Axis(labelAngle=-45)),
            color=alt.Color('corr:Q', title=None, scale=alt.Scale(scheme="blueorange", domain=[-1, 1]))
        )

        text = alt.Chart(corr_matrix_filtered).mark_text(
            align='center',
            baseline='middle',
            fontSize=12
        ).encode(
            x=alt.X('x:O'),
            y=alt.Y('y:O'),
            text=alt.Text("corr:Q", format=".2f")
        )

        chart = (heatmap + text).properties(
            width=350,
            height=350,
            title="Correlation Heatmap"
        )

        return mo.ui.altair_chart(chart)

    mo.output.append(mo.md(f"""
    ## Correlation

    Before diving deeper into links and effects, a little correlation research has to be done. We will simply plot a correlation heatmap with the inputs on the x-axis and metrics on the y-axis.
    """))
    mo.output.append(_corr_plot())
    mo.output.append(mo.md(f"""
    As the correlation matrix shows, we can expect evacutions with more disabled persons to be less efficient and effective, however we cannot expect much influence and effect from the morality parameters.
    """))
    return


@app.cell(hide_code=True)
def _(alt, data, mo):
    def _morality_map():
        _df = data.groupby(["morality_mean", "morality_std"], dropna=False).mean(numeric_only=True)
        _df = _df[["avg_evac_time", "total_evac_time", "num_agents_left"]].reset_index()

        charts = []
        for metric in ["avg_evac_time", "total_evac_time", "num_agents_left"]:
            xmin = _df[metric].min()
            xmax = _df[metric].max()

            heatmap = alt.Chart(_df).mark_circle().encode(
                x=alt.X('morality_mean:O', title='Morality Mean', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('morality_std:O', title='Morality Std'),
                size=alt.Size(metric+":O", legend=None, scale=alt.Scale(range=[500, 3000], zero=False)),
                color=alt.Color(metric+":Q", title=None, scale=alt.Scale(scheme="blues"))
            )

            text = alt.Chart(_df).mark_text(
                align='center',
                baseline='middle',
                fontSize=8
            ).encode(
                x=alt.X('morality_mean:O'),
                y=alt.Y('morality_std:O'),
                text=alt.Text(metric + ":Q", format=".2f")
            )

            chart = (heatmap + text).properties(
                width=230,
                height=230,
                title=metric.replace('_', ' ').title()
            )

            charts.append(chart)

        # Concatenate the charts horizontally
        final_chart = alt.hconcat(*charts).resolve_scale(
            size='independent',
            color='independent'
        ).properties(
            title=alt.TitleParams(
                text="Evacuation Metrics by Morality Mean and Std",
                anchor="middle"
            )
        )

        return mo.ui.altair_chart(final_chart)

    mo.vstack([
        mo.md(f"""
        ## Morality Metrics
    
        Morality is normally distributed across all students and is defined by two parameters:
    
        - **Morality Mean:** The middle of the bell curve
        - **Morality Std:** The standard deviation of the bell curve
    
        To visualise the impact of these two parameters on the three metrics, they are plotted as pseudo-3d chart.
        """),
        _morality_map(),
        mo.md(f"""
        As expected, the morality has no clear influence on the metrics.
        """)
    ])
    return


@app.cell(hide_code=True)
def _(alt, data, mo):
    def _plot_distribution(x:str):
        _metrics = ["avg_evac_time", "total_evac_time", "num_agents_left"]
        x_title = x.replace("_", " ").title()

        charts = []
        for metric in _metrics:
            metric_title = metric.replace("_", " ").title()

            chart = alt.Chart(data).mark_boxplot(size=60).encode(
                x=alt.X(x+":O", title=x_title, axis=alt.Axis(labelAngle=0)),
                y=alt.Y(metric+":Q", title=metric_title, scale=alt.Scale(domainMin=data[metric].min()))
            ).properties(
                width=270,
                height=270,
                title=metric_title
            )

            charts.append(chart)

        final_chart = alt.hconcat(*charts).properties(
            title=alt.TitleParams(
                text=f"Distribution of {x_title}",
                anchor="middle"
            )
        )

        return mo.ui.altair_chart(final_chart)

    mo.output.append(mo.md("""
    ## Abled to Disabled Ratio Metrics

    The ratio of abled to disabled persons in the simulation is a very important parameter. It is expected that the more disabled persons are in the simulation, the less efficient and effective the evacuation will be.
    """))
    mo.output.append(_plot_distribution("abled_to_disabled_ratio"))
    mo.output.append(mo.md("""
    Indeed the evacuation times quite drastically decrease when the amount of disabled persons decreases. Also the amount of students left behind decreases.

    ## Voting Method Metrics

    Now this is an intresting one, there are no real heuristics about what kind of voting method would yield the best results in these circumstances. What is also interesting is the amount of disabled persons left behind, given the voting only takes place in clusters (where no disabled persons are present), there should be no effect.
    """))
    mo.output.append(_plot_distribution("voting_method"))
    mo.output.append(mo.md("""
    As expected, the voting method has no effect on the amount of disabled persons left behind. However, there might be something to say about its effect on the evacuation times.

    Plurality voting looks like the worst choice of voting, the average evacuation time lies higher than other methods. This can be explained as it is the only one that tunnelvisions on a single exits. Where the other voting methods look at multiple exits and thusly can find an exit that the group as collective is okay with. Whether or not cumulative voting would be better than approval voting or the other way around is hard to say. However, one might argue that, as approval voting is slightly better than cumulative voting, it might be the best choice. Also approval voting is a more realistic voting system for clusters in an evacuation, it follows the natural flow of conversation and does not involve much maths.
    """))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Conclusion

        In this document we have seen the effects of the input parameters on the evacuation metrics. The most important parameter is the ratio of abled to disabled persons. More disabled persons means less abled persons to help them which directly leads to more time needed to evacuate and more people left behind. The morality parameters have no clear effect on the metrics. The voting method has a slight effect on the evacuation times, however it is hard to say which one is the best. Plurality voting is the worst choice, while approval voting and cumulative voting are better. However, it is hard to say which one is the best. Approval voting might be the best choice as it is slightly better than cumulative voting and is a more realistic voting system for clusters in an evacuation.
        """
    )
    return


if __name__ == "__main__":
    app.run()
