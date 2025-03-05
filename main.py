import streamlit as st
import pandas as pd
import os

from io import BytesIO

st.set_page_config(page_title="Data Sweeper", layout="wide")

st.markdown(
    """
    <style>
        .main { background-color: #1E1E2F; color: #FFFFFF; }
        .block-container { padding: 3rem 2rem; border-radius: 12px; background-color: #282A36; color: #F8F8F2; }
        h1, h2, h3, h4, h5, h6 { color: #FF5555; }
        .stButton>button { border-radius: 8px; background-color: #6272A4; color: white; padding: 0.75rem 1.5rem; }
        .stButton>button:hover { background-color: #FF79C6; }
        .stDownloadButton>button { background-color: #BD93F9; color: white; }
        .stDownloadButton>button:hover { background-color: #FF5555; }
        .stDataFrame, .stTable { border-radius: 10px; background-color: #44475A; color: white; }
        .stRadio>label, .stCheckbox>label { color: #FF5555; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Data Sweeper: Clean, Convert & Visualize Your Data")
st.write("Say goodbye to messy data. Upload, clean, visualize, and convert your files with just a few clicks.")

uploaded_files = st.file_uploader("Drop your files here (CSV or Excel) and let Data Sweeper handle the rest:", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        df = pd.read_csv(file) if file_extension == ".csv" else pd.read_excel(file)

        st.write(f"### Processing: {file.name} ({file.size / 1024:.2f} KB)")
        st.dataframe(df.head())

        st.subheader("Data Cleaning & Transformation")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Remove Duplicates from {file.name}"):
                df.drop_duplicates(inplace=True)
                st.success("Duplicate rows removed successfully!")
            
            if st.button(f"Rename Columns for {file.name}"):
                new_column_names = st.text_area("Enter new column names, separated by commas:")
                if new_column_names:
                    df.columns = [col.strip() for col in new_column_names.split(",")]
                    st.success("Column names updated!")
        
        with col2:
            missing_value_strategy = st.selectbox(
                f"Handle Missing Values for {file.name}",
                ["Do Nothing", "Fill with Mean", "Fill with Median", "Drop Rows"]
            )
            if missing_value_strategy != "Do Nothing":
                if missing_value_strategy == "Fill with Mean":
                    df.fillna(df.mean(), inplace=True)
                elif missing_value_strategy == "Fill with Median":
                    df.fillna(df.median(), inplace=True)
                elif missing_value_strategy == "Drop Rows":
                    df.dropna(inplace=True)
                st.success(f"Missing values handled using: {missing_value_strategy}")
        
        st.subheader("Data Visualization")
        numeric_cols = df.select_dtypes(include=['number']).columns
        chart_type = st.selectbox("Select a chart type to explore your data:", ["Bar Chart", "Line Chart", "Pie Chart"], key=file.name)
        selected_col = st.selectbox("Choose a numeric column to visualize:", numeric_cols, key=file.name+"col")
        
        if selected_col:
            if chart_type == "Bar Chart":
                fig = px.bar(df, x=df.index, y=selected_col, title=f"{selected_col} Distribution", color_discrete_sequence=["#FFB86C"])
            elif chart_type == "Line Chart":
                fig = px.line(df, x=df.index, y=selected_col, title=f"Trend of {selected_col}", color_discrete_sequence=["#8BE9FD"])
            elif chart_type == "Pie Chart":
                fig = px.pie(df, names=df.index, values=selected_col, title=f"{selected_col} Proportions", color_discrete_sequence=["#FF5555", "#50FA7B", "#BD93F9"])
            st.plotly_chart(fig)
        
        st.subheader("Convert & Download")
        conversion_type = st.radio(f"Choose a format to convert {file.name}:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert & Download {file.name}"):
            buffer = BytesIO()
            file_name = file.name.replace(file_extension, ".csv" if conversion_type == "CSV" else ".xlsx")
            mime_type = "text/csv" if conversion_type == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            df.to_csv(buffer, index=False) if conversion_type == "CSV" else df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            st.download_button("Download", data=buffer, file_name=file_name, mime=mime_type)

st.success("All files processed successfully")
