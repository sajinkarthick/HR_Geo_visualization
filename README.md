Industrial HR Quick EDA (Streamlit + Plotly)
An interactive Exploratory Data Analysis (EDA) dashboard built with Streamlit and Plotly for quick insights into industrial HR datasets.

Features

Fast & Interactive: Built with Plotly for smooth, responsive charts.
Sample Size Control: Enter the number of rows to analyze for speed.
Summary Statistics: Quick overview of numeric and categorical data.
Visualizations:

Numeric Scatter Plot with optional color grouping.
Categorical Distribution (Bar, Pie, Donut) with top-N filter.


Correlation Heatmap: Toggle on/off for numeric features.
Hover Tooltips: Full category names even when labels are truncated.

project/
│
├── data/
│   └── raw/
│       └── merged_file.csv   # Your dataset
│
├── app.py                    # Main Streamlit app
└── README.md                 # This file

git clone https://github.com/your-username/industrial-hr-eda.git
cd industrial-hr-eda

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
