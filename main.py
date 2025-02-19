# Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

# Set up the App
st.set_page_config(page_title="🧹 Data Sweeper", layout="wide", page_icon="🧹")
st.title("🧹Advanced Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# Custom CSS for styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stFileUploader>div>div>button {
        background-color: #008CBA;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
    }
    .stFileUploader>div>div>button:hover {
        background-color: #007B9E;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for global settings
st.sidebar.header("Settings")
st.sidebar.write("Customize your data cleaning and conversion experience.")

# Data Cleaning Options
st.sidebar.subheader("Data Cleaning Options")
remove_duplicates = st.sidebar.checkbox("Remove Duplicates")
fill_missing_values = st.sidebar.checkbox("Fill Missing Values")
standardize_columns = st.sidebar.checkbox("Standardize Column Names")
remove_columns = st.sidebar.checkbox("Remove Columns")

# Conversion Options
conversion_type = st.sidebar.radio(
    "Convert File to:",
    ["CSV", "Excel"]
)

if st.sidebar.button("Convert and Download"):
    if 'df' in st.session_state:
        df = st.session_state.df
        buffer = BytesIO()
        if conversion_type == "CSV":
            df.to_csv(buffer, index=False)
            st.download_button("Download CSV", data=buffer.getvalue(), file_name="converted_file.csv", mime="text/csv")
        else:
            df.to_excel(buffer, index=False)
            st.download_button("Download Excel", data=buffer.getvalue(), file_name="converted_file.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("No data loaded to convert.")

# File Uploader
uploaded_files = st.file_uploader(
    "Upload your files (CSV or Excel):",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    help="You can upload multiple files at once."
)

# Initialize session state for cleaned data and balloons trigger
if "cleaned_data" not in st.session_state:
    st.session_state.cleaned_data = {}
if "show_balloons" not in st.session_state:
    st.session_state.show_balloons = False

# Process each uploaded file
if uploaded_files:
    for file in uploaded_files:
        st.divider()
        st.subheader(f"📄 File: {file.name}")

        # Load the file into a DataFrame
        try:
            file_ext = os.path.splitext(file.name)[-1].lower()
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error loading file: {e}")
            continue

        # Display file info
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")
        st.write(f"**Total Rows:** {len(df)}")
        st.write(f"**Total Columns:** {len(df.columns)}")

        # Show a preview of the data
        with st.expander("👀 Preview Data"):
            st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🧹 Data Cleaning Options")
        cleaning_options = st.multiselect(
            f"Select cleaning options for {file.name}:",
            ["Remove Duplicates", "Fill Missing Values", "Standardize Column Names", "Remove Columns"],
            key=f"cleaning_{file.name}"
        )

        # Apply cleaning options
        if "Remove Duplicates" in cleaning_options:
            df = df.drop_duplicates()
            st.success("✅ Duplicates removed!")
        if "Fill Missing Values" in cleaning_options:
            numeric_cols = df.select_dtypes(include=["number"]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            st.success("✅ Missing values filled!")
        if "Standardize Column Names" in cleaning_options:
            df.columns = df.columns.str.lower().str.replace(" ", "_")
            st.success("✅ Column names standardized!")
        if "Remove Columns" in cleaning_options:
            columns_to_remove = st.multiselect(
                f"Select columns to remove for {file.name}:",
                df.columns,
                key=f"remove_{file.name}"
            )
            df = df.drop(columns=columns_to_remove)
            st.success("✅ Columns removed!")

        # Save cleaned data to session state
        st.session_state.cleaned_data[file.name] = df

        # Select Columns to Keep
        st.subheader("🔍 Select Columns to Keep")
        columns_to_keep = st.multiselect(
            f"Choose columns to keep for {file.name}:",
            df.columns,
            default=df.columns,
            key=f"columns_{file.name}"
        )
        df = df[columns_to_keep]

        # Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show visualizations for {file.name}", key=f"viz_{file.name}"):
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                chart_type = st.selectbox(
                    f"Select chart type for {file.name}:",
                    ["Bar Chart", "Line Chart", "Histogram", "Scatter Plot", "Box Plot", "Correlation Matrix"],
                    key=f"chart_{file.name}"
                )
                if chart_type in ["Bar Chart", "Line Chart", "Histogram", "Scatter Plot", "Box Plot"]:
                    x_axis = st.selectbox("Select X-axis:", numeric_cols, key=f"x_{file.name}")
                    y_axis = st.selectbox("Select Y-axis:", numeric_cols, key=f"y_{file.name}")

                    if chart_type == "Bar Chart":
                        st.bar_chart(df[[x_axis, y_axis]])
                    elif chart_type == "Line Chart":
                        st.line_chart(df[[x_axis, y_axis]])
                    elif chart_type == "Histogram":
                        st.bar_chart(df[x_axis])
                    elif chart_type == "Scatter Plot":
                        fig, ax = plt.subplots()
                        sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax)
                        st.pyplot(fig)
                    elif chart_type == "Box Plot":
                        fig, ax = plt.subplots()
                        sns.boxplot(data=df, x=x_axis, y=y_axis, ax=ax)
                        st.pyplot(fig)
                elif chart_type == "Correlation Matrix":
                    corr = df.corr()
                    fig, ax = plt.subplots()
                    sns.heatmap(corr, annot=True, ax=ax)
                    st.pyplot(fig)
            else:
                st.warning("No numeric columns found for visualization.")

        # File Conversion
        st.subheader("🛠️ File Conversion")
        conversion_type = st.radio(
            f"Convert {file.name} to:",
            ["CSV", "Excel"],
            key=f"convert_{file.name}"
        )

        if st.button(f"Convert {file.name}", key=f"convert_btn_{file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            # Download Button
            st.download_button(
                label=f"📥 Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
                key=f"download_{file.name}"
            )
            st.success(f"🎉 {file.name} converted to {conversion_type}!")
            st.session_state.show_balloons = True  # Set balloons trigger to True

    # Show balloons only once after all files are processed
    if st.session_state.show_balloons:
        st.balloons()
        st.session_state.show_balloons = False  # Reset the trigger
else:
    st.info("👆 Upload your files to get started!")

# Footer
st.divider()
st.write("Made with ❤️ by [M Haris]")