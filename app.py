from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="West Africa Power Explorer", page_icon="⚡", layout="wide")
DATA = Path(__file__).parent / "data"


@st.cache_data
def load():
    return (
        pd.read_csv(DATA / "scenarios.csv"),
        pd.read_csv(DATA / "ng_sensitivity.csv"),
        pd.read_csv(DATA / "price_duration.csv"),
        pd.read_csv(DATA / "gh_sensitivity.csv")
    )

scenarios, ng_data, prices, gh_data = load()



header_left, header_right = st.columns([3, 2])

with header_left:
    st.title("⚡ West Africa Power Explorer")


with header_right:
    st.markdown(
        """
        <div style="text-align: right; padding-top: 18px;">
            <div style="
                font-size: 18px;
                font-weight: 700;
                color: #2563EB;
                letter-spacing: 0.3px;
            ">
                Micheal Kehinde Temitope
            </div>
            <div style="
                font-size: 12px;
                font-weight: 600;
                color: #0D9488;
                letter-spacing: 1.5px;
                margin-top: 5px;
            ">
                Project Developer
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.caption("Hourly 2023 three-region electricity-system optimization • Linopy / HiGHS • Research portfolio")
st.markdown("Explore how electricity transmission between **Nigeria**, **Benin/Togo**, and **Ghana** affects system costs, CO₂ emissions and supply adequacy. All displayed numerical results are from the supplied model output workbook; no new optimization is performed here.")




view = st.sidebar.radio(
    "Explore",
    [
        "Project Overview",
        "Scenario comparison",
        "Transmission Explorer",
        "Price duration curves",
        "Method and limitations"
    ],
    index=0,
    key="portfolio_view"
)



if view == "Project Overview":

    st.markdown(
        "### Exploring the Operational Value of Cross-Border "
        "Electricity Transmission"
    )

    st.write(
        "This independent research project investigates how "
        "cross-border electricity transmission capacity affects "
        "electricity-system operating costs, supply reliability, "
        "operational CO₂ emissions and electricity prices in "
        "Nigeria, Benin/Togo and Ghana."
    )


    # ----------------------------------------
    # HOMEPAGE NETWORK OVERVIEW
    # ----------------------------------------

    st.subheader("Modeled Electricity Network")

    st.caption(
        "S1 baseline: a simplified three-region representation. "
        "Connection labels indicate transfer-capacity limits, "
        "not actual electricity flows."
    )

    import plotly.graph_objects as go

    fig_home_network = go.Figure()

    fig_home_network.add_trace(go.Scatter(
        x=[0, 1, 2],
        y=[0, 0, 0],
        mode="lines",
        line=dict(color="#94a3b8", width=5),
        hoverinfo="skip",
        showlegend=False
    ))

    fig_home_network.add_trace(go.Scatter(
        x=[0, 1, 2],
        y=[0, 0, 0],
        mode="markers+text",
        marker=dict(
            size=48,
            color=["#2563eb", "#059669", "#d97706"]
        ),
        text=["Nigeria", "Benin/Togo", "Ghana"],
        textposition="bottom center",
        hoverinfo="text",
        showlegend=False
    ))

    fig_home_network.add_annotation(
        x=0.5,
        y=0.22,
        text="NG–BT: 200 MW",
        showarrow=False
    )

    fig_home_network.add_annotation(
        x=1.5,
        y=0.22,
        text="GH–BT: 250 MW",
        showarrow=False
    )

    fig_home_network.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=20, b=45),
        xaxis=dict(visible=False, range=[-0.3, 2.3]),
        yaxis=dict(visible=False, range=[-0.5, 0.5]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig_home_network, width="stretch")

    st.subheader("Research Question")

    st.info(
        "How does increasing cross-border transmission capacity "
        "between Nigeria, Benin/Togo and Ghana influence "
        "electricity-system operation and the economic value "
        "of regional power exchange?"
    )

    st.subheader("Model at a Glance")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Modeled regions", "3")
    c2.metric("Simulation hours", "8,760")
    c3.metric("Generation assets", "15")
    c4.metric("Core scenarios", "4")


    # ----------------------------------------
    # HEADLINE RESEARCH RESULTS
    # ----------------------------------------

    st.subheader("Headline Results: S0 vs S1")

    st.caption(
        "Comparison of the disconnected system (S0) with "
        "the baseline interconnected system (S1), using "
        "previously solved 2023 optimization results."
    )

    s0 = scenarios.loc[
        scenarios["scenario"] == "S0"
    ].iloc[0]

    s1 = scenarios.loc[
        scenarios["scenario"] == "S1"
    ].iloc[0]

    objective_reduction = (
        s0["operating_cost_billion_usd"]
        - s1["operating_cost_billion_usd"]
    )

    objective_reduction_pct = (
        objective_reduction
        / s0["operating_cost_billion_usd"]
    ) * 100

    ens_reduction = s0["ens_gwh"] - s1["ens_gwh"]

    co2_increase = s1["co2_mt"] - s0["co2_mt"]

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Annual operating objective reduction",
        f"${objective_reduction:.3f} bn",
        f"{objective_reduction_pct:.1f}% lower than S0",
        delta_color="off"
    )

    r2.metric(
        "Reduction in energy not served",
        f"{ens_reduction:,.2f} GWh",
        "S1: 0 GWh unserved",
        delta_color="off"
    )

    r3.metric(
        "Change in operational CO₂",
        f"+{co2_increase:.3f} Mt",
        "S1 relative to S0",
        delta_color="off"
    )

    st.caption(
        "Operating objective includes modeled generation "
        "operating costs and penalties for unserved demand. "
        "It excludes transmission investment costs."
    )

    st.warning(
        "S0 has lower operational CO₂ emissions but leaves "
        "substantial electricity demand unserved. The "
        "emissions increase in S1 should therefore not be "
        "interpreted independently of improved reliability."
    )

    st.divider()

    st.subheader("Modeling Approach")

    st.write(
        "The study uses a linear programming electricity "
        "dispatch model implemented in Python with Linopy "
        "and solved using HiGHS. It represents hourly "
        "electricity-system operation over the year 2023."
    )

    st.write(
        "The model includes generation dispatch, electricity "
        "demand, energy not served and bidirectional "
        "transmission between the modeled regions."
    )


    # ----------------------------------------
    # ECONOMIC INTERPRETATION
    # ----------------------------------------

    st.subheader("How to Interpret the Economic Results")

    with st.expander(
        "What does the operating objective represent?",
        expanded=True
    ):
        st.write(
            "The reported annual operating objective includes "
            "modeled generation operating costs and penalties "
            "associated with energy not served. It does not "
            "include transmission investment expenditure."
        )

        st.write(
            "Consequently, a reduction in the objective should "
            "not automatically be interpreted as an equivalent "
            "reduction in fuel expenditure or as net economic profit."
        )

    with st.expander(
        "Why does S0 have lower CO₂ emissions?"
    ):
        st.write(
            "S0 represents a disconnected electricity system "
            "in which approximately 1,206.26 GWh of electricity "
            "demand remains unserved. Some of its lower "
            "operational emissions may therefore reflect "
            "electricity that was not generated."
        )

        st.write(
            "Comparisons of emissions across scenarios must "
            "therefore account for differences in electricity "
            "supply reliability."
        )

    with st.expander(
        "Are the identified transmission capacities optimal?"
    ):
        st.write(
            "No. The sensitivity analysis identifies "
            "conditional operating-cost saturation regions "
            "under the modeled assumptions."
        )

        st.write(
            "Nigeria–BT approaches saturation around 710 MW "
            "when Ghana–BT is fixed at 250 MW. Ghana–BT "
            "approaches saturation around 300 MW when "
            "Nigeria–BT is fixed at 200 MW."
        )

        st.write(
            "These values are not investment-optimal "
            "capacities because transmission capital costs "
            "and other investment-related considerations "
            "are excluded."
        )

    st.subheader("Key Research Findings")

    st.markdown(
        """
        - **Reliability:** The disconnected S0 scenario has
          approximately 1,206 GWh of energy not served,
          while S1–S3 eliminate modeled unmet demand.

        - **Operating costs:** Regional interconnection
          substantially reduces the optimized annual
          operating objective relative to S0.

        - **Transmission reinforcement:** Additional Nigeria–BT
          capacity provides greater marginal operational
          benefits at the S1 baseline than additional
          Ghana–BT capacity.

        - **Capacity saturation:** Conditional operating-cost
          benefits approach zero near 710 MW for Nigeria–BT
          and approximately 300 MW for Ghana–BT.
        """
    )

    st.warning(
        "Interpretation: Lower operational CO₂ emissions in "
        "the disconnected scenario must be considered alongside "
        "its substantial unmet electricity demand. "
        "The analysis evaluates operational outcomes and does "
        "not include transmission investment costs."
    )

    st.subheader("Explore the Results")

    st.write(
        "Use the sidebar to compare the four modeled scenarios, "
        "investigate transmission-capacity sensitivities, "
        "explore electricity-price duration curves and "
        "review the model assumptions and limitations."
    )


    # ----------------------------------------
    # HOMEPAGE QUICK NAVIGATION
    # ----------------------------------------

    st.markdown("**Choose an area to explore:**")

    def navigate_to(page):
        st.session_state["portfolio_view"] = page

    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        st.button(
            "📊 Compare Scenarios",
            on_click=navigate_to,
            args=("Scenario comparison",),
            use_container_width=True
        )

    with nav2:
        st.button(
            "⚡ Explore Transmission",
            on_click=navigate_to,
            args=("Transmission Explorer",),
            use_container_width=True
        )

    with nav3:
        st.button(
            "📖 Model Methodology",
            on_click=navigate_to,
            args=("Method and limitations",),
            use_container_width=True
        )

elif view == "Scenario comparison":
    st.subheader("Validated transmission scenarios")
    
    # Descriptive names for the transmission scenarios
    scenario_names = {
        "S0": "S0 — No Interconnection",
        "S1": "S1 — Baseline Interconnection",
        "S2": "S2 — 50% Capacity Expansion",
        "S3": "S3 — Reference Capacity Scenario"
    }

    # Explanation displayed below the scenario selector
    scenario_descriptions = {
        "S0": (
            "No interconnection: NG–BT = 0 MW and "
            "GH–BT = 0 MW."
        ),
        "S1": (
            "Baseline interconnection: NG–BT = 200 MW "
            "and GH–BT = 250 MW."
        ),
        "S2": (
            "Both transmission capacities are increased "
            "by 50% relative to S1: NG–BT = 300 MW "
            "and GH–BT = 375 MW."
        ),
        "S3": (
            "Reference capacity scenario: NG–BT = 335 MW "
            "and GH–BT = 655.2 MW."
        )
    }

    chosen = st.selectbox(
        "Choose a solved scenario",
        options=scenarios.scenario.tolist(),
        index=1,
        format_func=lambda s: scenario_names.get(s, s)
    )

    st.caption(scenario_descriptions.get(chosen, ""))
    
    # Explain emissions in scenarios with unmet demand
    if chosen == "S0":
        st.warning(
            "⚠️ Interpretation of S0 emissions: "
            "Although S0 has lower operational CO₂ emissions "
            "than S1, the disconnected system leaves "
            "1,206.26 GWh of electricity demand unserved. "
            "Part of the lower emissions may therefore reflect "
            "electricity that was not generated. "
            "S0 should not be interpreted as environmentally "
            "superior without accounting for unmet demand."
        )


    record = scenarios.set_index("scenario").loc[chosen]
    base = scenarios.set_index("scenario").loc["S1"]
    
    # ----------------------------------------
    # KPI INDICATORS
    # ----------------------------------------

    c1, c2, c3 = st.columns(3)

    # Calculate differences relative to S1
    cost_diff = (
        record.operating_cost_billion_usd
        - base.operating_cost_billion_usd
    ) * 1000

    co2_diff = record.co2_mt - base.co2_mt
    ens_diff = record.ens_gwh - base.ens_gwh

    # Avoid showing meaningless differences for S1
    if chosen == "S1":
        cost_delta = None
        co2_delta = None
        ens_delta = None
    else:
        cost_delta = f"{cost_diff:+,.2f} million USD vs S1"
        co2_delta = f"{co2_diff:+.3f} Mt relative to S1"
        ens_delta = f"{ens_diff:+,.2f} GWh vs S1"

    # Annual operating objective
    c1.metric(
        label="Annual operating objective",
        value=f"${record.operating_cost_billion_usd:.3f} bn",
        delta=cost_delta,
        delta_color="inverse"
    )

    # Operational CO2 emissions
    c2.metric(
        label="Operational CO₂ emissions",
        value=f"{record.co2_mt:.3f} Mt",
        delta=co2_delta,
        delta_color="off"
    )

    # Energy not served
    c3.metric(
        label="Energy not served (ENS)",
        value=f"{record.ens_gwh:,.2f} GWh",
        delta=ens_delta,
        delta_color="inverse"
    )


    # Explain the currently selected transmission scenario
    scenario_explanations = {
        "S0": "No interconnection between the modeled regions.",
        "S1": "Baseline interconnection configuration.",
        "S2": "Both transmission corridors expanded by 50% relative to S1.",
        "S3": "Reference transmission-capacity configuration."
    }

    st.info(
        f"**Selected scenario: {scenario_names.get(chosen, chosen)}**\n\n"
        f"NG–BT capacity: **{record.ng_bt_mw:g} MW** | "
        f"GH–BT capacity: **{record.gh_bt_mw:g} MW**\n\n"
        f"{scenario_explanations.get(chosen, '')}"
    )

    left,right=st.columns(2)
    with left:
        fig=px.bar(scenarios,x="scenario",y="operating_cost_billion_usd",labels={"scenario":"Scenario","operating_cost_billion_usd":"Operating cost (billion USD)"},title="Annual operating cost")
        st.plotly_chart(fig,use_container_width=True)
    
    with right:
        fig = px.scatter(
            scenarios,
            x="operating_cost_billion_usd",
            y="co2_mt",
            color="scenario",
            hover_name="scenario",
            hover_data={
                "ng_bt_mw": True,
                "gh_bt_mw": True,
                "ens_gwh": ":.2f"
            },
            labels={
                "operating_cost_billion_usd": "Operating cost (billion USD)",
                "co2_mt": "Operational CO₂ emissions (Mt)",
                "scenario": "Scenario"
            },
            title="Cost–emissions trade-off"
        )

        fig.update_traces(marker=dict(size=13))

        fig.update_layout(
            showlegend=True,
            legend_title_text="Scenario",
            hovermode="closest",
            height=450,
            
            yaxis=dict(
                range=[17.35, 18.9],
                tickmode="linear",
                tick0=17.4,
                dtick=0.2,
                showgrid=True,
                gridcolor="lightgray",
                tickformat=".1f",
                title="Operational CO₂ emissions (Mt)"
                
            )

        )

        st.plotly_chart(fig, use_container_width=True)


    
    # ----------------------------------------
    # CO2 EMISSIONS VS ENERGY NOT SERVED
    # ----------------------------------------

    st.subheader("Emissions and Electricity Supply Reliability")

    st.markdown(
        "This chart compares operational CO₂ emissions "
        "with energy not served (ENS) across the four "
        "transmission scenarios."
    )

    fig_reliability = px.scatter(
        scenarios,
        x="ens_gwh",
        y="co2_mt",
        color="scenario",
        size_max=18,
        hover_data={
            "operating_cost_billion_usd": ":.3f",
            "ng_bt_mw": True,
            "gh_bt_mw": True
        },
        labels={
            "ens_gwh": "Energy not served (GWh/year)",
            "co2_mt": "Operational CO₂ emissions (Mt/year)",
            "scenario": "Transmission scenario"
        },
        title="Operational CO₂ Emissions vs Energy Not Served"
    )
 

    fig_reliability.update_layout(
        height=480,
        hovermode="closest",
        yaxis=dict(
            range=[17.35, 18.9],
            tickmode="linear",
            tick0=17.4,
            dtick=0.2,
            tickformat=".1f",
            showgrid=True,
            gridcolor="lightgray",
            title="Operational CO₂ emissions (Mt/year)"
        )
    )

    st.plotly_chart(
        fig_reliability,
        use_container_width=True
    )

    st.info(
        "Interpretation: S0 has lower operational CO₂ emissions, "
        "but 1,206.26 GWh of demand remains unserved. "
        "S1–S3 eliminate modeled ENS, although operational "
        "emissions are higher. Therefore, lower emissions "
        "in S0 should not be interpreted independently "
        "of electricity supply reliability."
    )



elif view == "Transmission Explorer":

    st.subheader("Interactive Transmission Capacity Explorer")

    st.markdown(
        "Investigate how changing the transfer capacity of an "
        "individual transmission corridor affects electricity-system "
        "operation. Results are retrieved from previously solved "
        "hourly optimization cases."
    )

    # ----------------------------------------
    # SELECT TRANSMISSION CORRIDOR
    # ----------------------------------------

    corridor = st.radio(
        "Select transmission corridor",
        [
            "Nigeria–Benin/Togo",
            "Ghana–Benin/Togo"
        ],
        horizontal=True
    )

    if corridor == "Nigeria–Benin/Togo":
        sensitivity = ng_data.copy()
        capacity_column = "ng_bt_mw"
        baseline_capacity = 200.0
        fixed_capacity = "Ghana–BT = 250 MW"
        corridor_short = "NG–BT"
        saturation = "~710 MW"

    else:
        sensitivity = gh_data.copy()
        capacity_column = "gh_bt_mw"
        baseline_capacity = 250.0
        fixed_capacity = "Nigeria–BT = 200 MW"
        corridor_short = "GH–BT"
        saturation = "~300 MW"

    st.caption(
        f"Selected corridor: **{corridor}**. "
        f"The other corridor is held fixed at "
        f"**{fixed_capacity}**."
    )

    # ----------------------------------------
    # SELECT SOLVED CAPACITY
    # ----------------------------------------

    available_capacities = sorted(
        sensitivity[capacity_column].unique().tolist()
    )

    selected_capacity = st.select_slider(
        f"Select {corridor_short} transmission capacity",
        options=available_capacities,
        value=baseline_capacity,
        format_func=lambda x: f"{x:g} MW"
    )

    # ----------------------------------------
    # INTERACTIVE NETWORK DIAGRAM
    # ----------------------------------------

    import plotly.graph_objects as go

    st.subheader("West Africa Transmission Network")

    st.caption(
        "Simplified three-region network. Lines represent "
        "modeled transfer-capacity limits, not actual power flows."
    )

    # Use the existing selected capacity.
    # Move this diagram BELOW the select_slider and its result lookup
    # so selected_capacity is already defined.

    if corridor == "Nigeria–Benin/Togo":
        ng_display = selected_capacity
        gh_display = 250.0
    else:
        ng_display = 200.0
        gh_display = selected_capacity

    fig_network = go.Figure()

    # Connection between Nigeria and Benin/Togo
    fig_network.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 0],
        mode="lines",
        line=dict(
            color="#2563eb" if corridor == "Nigeria–Benin/Togo"
            else "#94a3b8",
            width=7 if corridor == "Nigeria–Benin/Togo" else 3
        ),
        hovertemplate=f"NG–BT: {ng_display:g} MW<extra></extra>",
        showlegend=False
    ))

    # Connection between Benin/Togo and Ghana
    fig_network.add_trace(go.Scatter(
        x=[1, 2],
        y=[0, 0],
        mode="lines",
        line=dict(
            color="#d97706" if corridor == "Ghana–Benin/Togo"
            else "#94a3b8",
            width=7 if corridor == "Ghana–Benin/Togo" else 3
        ),
        hovertemplate=f"GH–BT: {gh_display:g} MW<extra></extra>",
        showlegend=False
    ))

    # Three regional nodes
    fig_network.add_trace(go.Scatter(
        x=[0, 1, 2],
        y=[0, 0, 0],
        mode="markers+text",
        marker=dict(
            size=58,
            color=["#2563eb", "#059669", "#d97706"],
            line=dict(color="white", width=2)
        ),
        text=["Nigeria", "Benin/Togo", "Ghana"],
        textposition="bottom center",
        textfont=dict(size=14),
        hoverinfo="text",
        showlegend=False
    ))

    fig_network.add_annotation(
        x=0.5, y=0.25,
        text=f"NG–BT: {ng_display:g} MW",
        showarrow=False,
        font=dict(size=14)
    )

    fig_network.add_annotation(
        x=1.5, y=0.25,
        text=f"GH–BT: {gh_display:g} MW",
        showarrow=False,
        font=dict(size=14)
    )

    fig_network.update_layout(
        height=290,
        margin=dict(l=20, r=20, t=30, b=50),
        xaxis=dict(visible=False, range=[-0.35, 2.35]),
        yaxis=dict(visible=False, range=[-0.6, 0.6]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig_network, width="stretch")

    sensitivity_indexed = sensitivity.set_index(
        capacity_column
    )

    result = sensitivity_indexed.loc[selected_capacity]
    baseline = sensitivity_indexed.loc[baseline_capacity]

    # ----------------------------------------
    # CALCULATE CHANGES RELATIVE TO BASELINE
    # ----------------------------------------

    cost_change = (
        result["operating_cost_billion_usd"]
        - baseline["operating_cost_billion_usd"]
    ) * 1000

    co2_change = result["co2_mt"] - baseline["co2_mt"]

    ens_change = result["ens_gwh"] - baseline["ens_gwh"]

    price_change = (
        result["bt_price_usd_mwh"]
        - baseline["bt_price_usd_mwh"]
    )

    is_baseline = selected_capacity == baseline_capacity

    # ----------------------------------------
    # DISPLAY KPI INDICATORS
    # ----------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Annual operating objective",
        f"${result['operating_cost_billion_usd']:.6f} bn",
        None if is_baseline else
        f"{cost_change:+.3f} M USD vs baseline",
        delta_color="inverse"
    )

    c2.metric(
        "Operational CO₂ emissions",
        f"{result['co2_mt']:.4f} Mt",
        None if is_baseline else
        f"{co2_change:+.4f} Mt vs baseline",
        delta_color="off"
    )

    c3.metric(
        "Energy not served",
        f"{result['ens_gwh']:.2f} GWh",
        None if is_baseline else
        f"{ens_change:+.2f} GWh vs baseline",
        delta_color="inverse"
    )

    c4.metric(
        "Benin/Togo marginal price",
        f"${result['bt_price_usd_mwh']:.2f}/MWh",
        None if is_baseline else
        f"{price_change:+.2f} USD/MWh",
        delta_color="off"
    )

    # Explain Ghana–BT operating-cost saturation
    if corridor == "Ghana–Benin/Togo" and selected_capacity >= 300:
        st.info(
            "Ghana–BT operating-cost saturation: "
            "With Nigeria–BT fixed at 200 MW, the modeled "
            "annual operating cost becomes almost constant "
            "around 300 MW of Ghana–BT capacity. "
            "Further reinforcement produces negligible "
            "additional operating-cost savings. "
            "Small differences may be hidden by KPI rounding. "
            "This is not an investment-optimal capacity."
        )

    st.divider()

    # ----------------------------------------
    # OPERATING COST SENSITIVITY
    # ----------------------------------------

    fig_cost = px.line(
        sensitivity,
        x=capacity_column,
        y="operating_cost_billion_usd",
        markers=True,
        title=f"{corridor_short}: Operating Cost Sensitivity",
        labels={
            capacity_column: "Transfer capacity (MW)",
            "operating_cost_billion_usd":
                "Annual operating objective (billion USD)"
        }
    )

    fig_cost.add_vline(
        x=selected_capacity,
        line_dash="dash",
        line_color="orange"
    )

    fig_cost.update_layout(height=450)

    st.plotly_chart(
        fig_cost,
        use_container_width=True
    )

    # ----------------------------------------
    # EMISSIONS SENSITIVITY
    # ----------------------------------------

    fig_emissions = px.line(
        sensitivity,
        x=capacity_column,
        y="co2_mt",
        markers=True,
        title=f"{corridor_short}: Operational CO₂ Emissions",
        labels={
            capacity_column: "Transfer capacity (MW)",
            "co2_mt": "Operational CO₂ emissions (Mt)"
        }
    )

    fig_emissions.add_vline(
        x=selected_capacity,
        line_dash="dash",
        line_color="orange"
    )

    fig_emissions.update_layout(height=450)

    st.plotly_chart(
        fig_emissions,
        use_container_width=True
    )

    # ----------------------------------------
    # MARGINAL OPERATIONAL VALUE
    # ----------------------------------------

    st.subheader("Marginal Value of Transmission Reinforcement")

    st.markdown(
        "This chart shows the average annual operating-cost "
        "saving per additional MW of transmission capacity "
        "between consecutive solved configurations."
    )

    # Sort sensitivity results by transmission capacity
    marginal_data = sensitivity.sort_values(
        capacity_column
    ).copy()

    # Convert operating objective from billion USD to USD
    marginal_data["cost_usd"] = (
        marginal_data["operating_cost_billion_usd"] * 1e9
    )

    # Calculate consecutive capacity increments
    marginal_data["capacity_change_mw"] = (
        marginal_data[capacity_column].diff()
    )

    # Calculate annual operating-cost reduction
    marginal_data["cost_saving_usd"] = (
        -marginal_data["cost_usd"].diff()
    )

    # Average savings per additional MW
    marginal_data["marginal_value_usd_mw_year"] = (
        marginal_data["cost_saving_usd"]
        / marginal_data["capacity_change_mw"]
    )

    # Remove first row (no previous capacity for comparison)
    marginal_data = marginal_data.dropna(
        subset=["marginal_value_usd_mw_year"]
    )

    # Plot marginal operational value
    fig_mv = px.line(
        marginal_data,
        x=capacity_column,
        y="marginal_value_usd_mw_year",
        markers=True,
        title=f"{corridor_short}: Marginal Operational Value",
        labels={
            capacity_column: "Transfer capacity (MW)",
            "marginal_value_usd_mw_year":
                "Average marginal value (USD/MW-year)"
        }
    )

    fig_mv.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    fig_mv.update_layout(
        height=470,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_mv,
        use_container_width=True
    )

    st.caption(
        "Each plotted value represents the average annual "
        "operating-cost saving per MW over the preceding "
        "capacity interval. It is not a pointwise shadow price."
    )

    # ----------------------------------------
    # BASELINE CORRIDOR VALUE COMPARISON
    # ----------------------------------------

    st.subheader("Which Transmission Corridor Has Greater Value?")

    st.markdown(
        "The following values represent the previously calculated "
        "annual marginal operational value of transmission capacity "
        "at the S1 baseline configuration."
    )

    ng_value = 240485.76
    gh_value = 460.01

    value_data = pd.DataFrame({
        "Corridor": [
            "Nigeria–Benin/Togo",
            "Ghana–Benin/Togo"
        ],
        "Marginal value (USD/MW-year)": [
            ng_value,
            gh_value
        ]
    })

    fig_comparison = px.bar(
        value_data,
        x="Corridor",
        y="Marginal value (USD/MW-year)",
        color="Corridor",
        text="Marginal value (USD/MW-year)",
        title="Annual Marginal Operational Value at S1"
    )

    fig_comparison.update_traces(
        texttemplate="$%{text:,.2f}",
        textposition="outside"
    )

    fig_comparison.update_layout(
        showlegend=False,
        height=450,
        yaxis_title="Marginal value (USD/MW-year)"
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )

    st.info(
        f"At the S1 baseline, NG–BT has approximately "
        f"{ng_value / gh_value:,.0f} times the annual "
        "marginal operational value of GH–BT. "
        "These values describe local operating-cost benefits, "
        "not investment profitability."
    )

    # ----------------------------------------
    # INTERPRETATION
    # ----------------------------------------

    st.info(
        f"**Operating-cost saturation:** The {corridor_short} "
        f"corridor approaches operating-cost saturation "
        f"at approximately {saturation}, conditional on "
        f"{fixed_capacity}. "
        "These thresholds are not investment-optimal "
        "capacities because transmission CAPEX is excluded."
    )

    st.caption(
        "Only previously solved capacities are available. "
        "Results from separate corridor sensitivity sweeps "
        "cannot be combined to predict simultaneous changes "
        "to both corridors."
    )

    with st.expander("View underlying sensitivity data"):
        st.dataframe(
            sensitivity,
            hide_index=True,
            use_container_width=True
        )

elif view == "Price duration curves":
    st.subheader("Benin/Togo price duration curves")
    pick=st.multiselect("Scenarios",["S1","S2","S3"],default=["S1","S2","S3"])
    if pick:
        long=prices.melt(id_vars="hour_rank",value_vars=pick,var_name="Scenario",value_name="Marginal price (USD/MWh)")
        fig=px.line(long,x="hour_rank",y="Marginal price (USD/MWh)",color="Scenario",title="Sorted hourly marginal-price outputs")
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.info("Select at least one scenario.")
    st.caption("Prices are duration-sorted, not chronological hourly timestamps.")

else:
    st.subheader("Model Methodology and Limitations")
    st.markdown("""
### 1. Research Scope

The model represents electricity-system operation across three
aggregated West African regions:

- **Nigeria (NG)**
- **Benin/Togo (BT)**
- **Ghana (GH)**

The analysis covers **2023**, using 8,760 hourly time steps
and 15 aggregated generation assets.

Two transmission corridors are represented:
Nigeria–Benin/Togo and Ghana–Benin/Togo.

### 2. Optimization Approach

The electricity-system model is formulated as a continuous
linear programming problem using **Linopy** and solved with
**HiGHS**.

It determines cost-minimizing hourly generation dispatch,
cross-border electricity transfers and energy not served,
subject to modeled operational constraints.

The annual objective includes generation operating costs
and penalties for unmet electricity demand.

### 3. Transmission Modeling

Transmission is represented using bidirectional power
transfers subject to shared corridor-capacity limits.

The application investigates how changes in transmission
capacity affect operating costs, operational CO₂ emissions,
supply reliability and modeled marginal electricity prices.

The individual corridor sensitivity analyses keep the other
corridor at its S1 baseline capacity.

### 4. Results and Data Provenance

The application displays previously solved optimization
results stored in four CSV files:

- `scenarios.csv`: four core transmission scenarios.
- `ng_sensitivity.csv`: Nigeria–BT capacity sensitivity.
- `gh_sensitivity.csv`: Ghana–BT capacity sensitivity.
- `price_duration.csv`: sorted marginal-price results.

The scenario, Nigeria–BT sensitivity and price-duration
datasets were exported from the research results workbook.
The Ghana–BT sensitivity dataset was extracted from
previously solved notebook outputs.

The application does not perform new optimization runs
when visitors change a scenario or capacity selection.

### 5. Important Limitations

- Transmission investment costs are excluded.
- The reported objective is not a net investment benefit.
- Identified saturation capacities are conditional
  operating-cost results, not investment optima.
- The model uses three aggregated regions rather than
  a detailed physical transmission network.
- Results from separate corridor sweeps cannot be combined
  to estimate untested simultaneous capacity changes.
- S0 leaves substantial demand unserved, which must be
  considered when comparing operational CO₂ emissions.

### 6. Future Development

Potential extensions include investment-cost modeling,
additional transmission configurations, more detailed
network representation and live optimization.

These extensions have not yet been implemented in the
current interactive portfolio.
    """)

st.divider()
st.caption("Independent research portfolio • Data-source and software-license audit required before public redistribution")
