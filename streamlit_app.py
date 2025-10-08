import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Geo-Visualization", layout="wide")
st.title("Industrial Human Resource Geo-Visualization")

# ---------- Data Loading ----------
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PATH = BASE_DIR / "data" / "raw" / "merged_file.csv"

@st.cache_data(show_spinner=False)
def load_data(path_str: str) -> pd.DataFrame:
    df = pd.read_csv(path_str, encoding="utf-8")
    df.columns = df.columns.astype(str).str.strip()
    return df

if not DEFAULT_PATH.exists():
    st.error(f"Default file not found: {DEFAULT_PATH}")
    st.stop()

df = load_data(str(DEFAULT_PATH))
if df.empty:
    st.warning("Empty dataset.")
    st.stop()

# Column types
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

# ---------- Sampling Controls ----------
st.sidebar.header("Sampling")
max_rows = int(len(df))
min_n = 100 if max_rows > 100 else 1
default_n = min(5000, max_rows)

sample_n = st.sidebar.number_input(
    "Rows to use for analysis",
    min_value=min_n,
    max_value=max_rows,
    value=default_n,
    step=100,
    format="%d"
)

sample_method = st.sidebar.radio(
    "Sampling method",
    ["Head (fast)", "Random"],
    horizontal=True
)

use_full_for_summary = st.sidebar.checkbox("Use full data for summary stats", False)

def make_sample(data: pd.DataFrame, n: int, method: str) -> pd.DataFrame:
    if n >= len(data):
        return data
    return data.head(n) if method.startswith("Head") else data.sample(n, random_state=42)

df_sample = make_sample(df, sample_n, sample_method)
st.caption(f"Using **{len(df_sample):,}** of **{len(df):,}** rows for visuals ({sample_method.lower()}).")

# ---------- View Toggles ----------
st.sidebar.header("Views")
show_summary = st.sidebar.checkbox("Summary", True)
show_visuals = st.sidebar.checkbox("Visuals", True)
show_corr = st.sidebar.checkbox("Correlation Heatmap", False)

# ---------- Summary ----------
if show_summary:
    st.subheader("Summary Statistics")
    target_df = df if use_full_for_summary else df_sample
    st.dataframe(target_df.describe(include='all').transpose(), use_container_width=True)

# ---------- Visuals ----------
if show_visuals:
    st.subheader("Visualizations")

    # Numeric scatter
    if len(numeric_cols) >= 2:
        st.markdown("#### Numeric Scatter")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            x_col = st.selectbox("X", numeric_cols, key="xcol")
        with c2:
            y_col = st.selectbox("Y", numeric_cols, index=1 if len(numeric_cols) > 1 else 0, key="ycol")
        with c3:
            color_by = st.selectbox("Color (optional)", ["None"] + numeric_cols + categorical_cols, key="colorby")
            color_arg = None if color_by == "None" else color_by

        fig = px.scatter(
            df_sample,
            x=x_col, y=y_col,
            color=color_arg,
            opacity=0.75,
            template="plotly_white",
            height=420
        )
        fig.update_traces(marker=dict(size=6))
        fig.update_layout(title=f"{x_col} vs {y_col}")
        st.plotly_chart(fig, use_container_width=True)

    # Categorical charts
    if categorical_cols:
        st.markdown("#### Categorical Distribution")
        left, right = st.columns([2, 1])
        with left:
            selected_cat = st.selectbox("Categorical column", categorical_cols, key="catcol")
        with right:
            top_n = st.slider("Top N", min_value=5, max_value=30, value=10, step=1)

        mode = st.radio("Chart Type", ["Bar", "Pie", "Donut"], horizontal=True, key="cat_mode")

        counts = (
            df_sample[selected_cat].astype(str).value_counts(dropna=False)
            .head(top_n)
            .reset_index()
        )
        counts.columns = [selected_cat, "count"]
        counts["full_label"] = counts[selected_cat].astype(str)
        counts["short_label"] = counts["full_label"].str.slice(0, 5)

        if mode == "Bar":
            fig = px.bar(
                counts,
                x="count",
                y="short_label",
                orientation="h",
                text="count",
                template="plotly_white",
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>Count: %{x}",
                customdata=counts[["full_label"]],
                textposition="outside"
            )
            fig.update_layout(
                xaxis_title="Count",
                yaxis_title=selected_cat,
                height=450,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            fig = px.pie(
                counts,
                names="short_label",
                values="count",
                hole=0.5 if mode == "Donut" else 0.0,
                template="plotly_white",
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>Count: %{value} (%{percent})",
                customdata=counts[["full_label"]],
                textinfo="percent+label"
            )
            fig.update_layout(title=f"Top {top_n} {selected_cat}", height=450)
            st.plotly_chart(fig, use_container_width=True)

# ---------- Correlation ----------
if show_corr and len(numeric_cols) >= 2:
    st.subheader("Correlation Heatmap (numeric)")
    corr = df_sample[numeric_cols].corr(numeric_only=True)
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        template="plotly_white",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
