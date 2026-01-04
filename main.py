import streamlit as st

st.title("Employee Training Registration Form")

# -----------------------------
# Dummy data
# -----------------------------
dropdown_names = [
    "Workforce Management System",
    "Warehouse Management System",
    "Quality Control System",
    "Document Management System",
    "FABS",
]

employee_list = [
    "Sami Toufic Taha",
    "Yousef El Kaakour",
    "Samir Kassab",
    "Baha Marie",
    "Ahmad Udwan",
    "Solomon Ladaga",
    "Wafa Hadidi",
]

# -----------------------------
# Form
# -----------------------------
with st.form("user_form"):

    selected_name = st.selectbox(
        label="Select System Name",
        options=dropdown_names
    )

    selected_date = st.date_input(
        label="Select Training Date"
    )

    selected_employees = st.multiselect(
        label="Select Employees",
        options=employee_list,
        help="Selected employees appear as removable chips"
    )

    submit = st.form_submit_button("Submit")

# -----------------------------
# Output + Toast
# -----------------------------
if submit:
    st.toast("Training registration saved successfully", icon="✅")

    # st.subheader("Submitted Data")
    # st.write("**System Name:**", selected_name)
    # st.write("**Training Date:**", selected_date)
    # st.write("**Selected Employees:**", selected_employees)
