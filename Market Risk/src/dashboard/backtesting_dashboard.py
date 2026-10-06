import pandas as pd
import streamlit as st


def render_backtesting_dashboard():

    st.header("Phase 8 — VaR Backtesting")

    results_path = (
        "data/risk/backtest_results.csv"
    )

    try:
        results = pd.read_csv(
            results_path,
            index_col=0,
        )

    except FileNotFoundError:

        st.warning(
            "Backtesting results not found. "
            "Run Phase 8 notebook first."
        )

        return

    st.subheader("Backtesting Summary")

    st.dataframe(
        results,
        use_container_width=True,
    )

    st.subheader("Model Conclusions")

    for model, row in results.iterrows():

        st.markdown(f"### {model}")

        st.write(
            f"Exceptions: "
            f"{row.get('Exceptions', 'N/A')}"
        )

        st.write(
            f"Expected Exceptions: "
            f"{row.get('Expected Exceptions', 'N/A')}"
        )

        st.write(
            f"Exception Ratio: "
            f"{row.get('Exception Ratio', 'N/A')}"
        )

        st.write(
            f"Kupiec: "
            f"{row.get('Kupiec Conclusion', 'N/A')}"
        )

        st.write(
            f"Christoffersen Independence: "
            f"{row.get('Christoffersen Independence Conclusion', 'N/A')}"
        )

        st.write(
            f"Conditional Coverage: "
            f"{row.get('Christoffersen Conditional Coverage Conclusion', 'N/A')}"
        )

        st.write(
            f"Basel Zone: "
            f"{row.get('Basel Zone', 'N/A')}"
        )