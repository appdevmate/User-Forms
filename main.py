# import streamlit as st
# import psycopg2
# from psycopg2.extras import RealDictCursor
#
# st.set_page_config(page_title="Employee Training Registration", layout="wide")
# st.title("Employee Training Registration")
#
# # -----------------------------
# # PostgreSQL connection
# # -----------------------------
# def get_db_connection():
#     return psycopg2.connect(
#         host="localhost",
#         database="training",
#         user="postgres",
#         password="123456",
#         port=5432
#     )
#
# # -----------------------------
# # Load data functions
# # -----------------------------
# def load_trained_users():
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=RealDictCursor)
#     cur.execute("""
#         SELECT e.id AS employee_id,
#                e.name AS employee_name,
#                s.name AS system_name,
#                us.assigned_date
#         FROM user_systems us
#         JOIN employees e ON e.id = us.user_id
#         JOIN systems s ON s.id = us.system_id
#         ORDER BY e.name, s.name
#     """)
#     data = cur.fetchall()
#     cur.close()
#     conn.close()
#     return data
#
# def load_systems():
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=RealDictCursor)
#     cur.execute("SELECT id, name FROM systems ORDER BY name;")
#     systems = cur.fetchall()
#     cur.close()
#     conn.close()
#     return systems
#
# def load_untrained_for_system(system_id):
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=RealDictCursor)
#     cur.execute("""
#         SELECT id, name FROM employees
#         WHERE id NOT IN (
#             SELECT user_id FROM user_systems WHERE system_id = %s
#         )
#         ORDER BY name
#     """, (system_id,))
#     employees = cur.fetchall()
#     cur.close()
#     conn.close()
#     return employees
#
# # -----------------------------
# # Initialize session_state
# # -----------------------------
# if 'trained_users' not in st.session_state:
#     st.session_state.trained_users = load_trained_users()
# if 'systems' not in st.session_state:
#     st.session_state.systems = load_systems()
# if 'selected_system_id' not in st.session_state:
#     st.session_state.selected_system_id = None
# if 'employee_options' not in st.session_state:
#     st.session_state.employee_options = []
#
# # -----------------------------
# # Metallic Cards CSS
# # -----------------------------
# st.markdown("""
# <style>
# .metallic-card {
#     background: linear-gradient(145deg, #d4d4d4, #f0f0f0);
#     border-radius: 12px;
#     padding: 20px;
#     text-align: center;
#     color: #000;
#     box-shadow: 4px 4px 10px #aaa, -4px -4px 10px #fff;
#     margin-bottom: 10px;
# }
# .metallic-card h2 {
#     margin: 0;
#     font-size: 32px;
# }
# .metallic-card p {
#     margin: 0;
#     font-size: 16px;
#     font-weight: bold;
# }
# </style>
# """, unsafe_allow_html=True)
#
# # -----------------------------
# # Top Cards
# # -----------------------------
# trained_users_count = len({tu['employee_id'] for tu in st.session_state.trained_users})
# systems_count = len(st.session_state.systems)
#
# col1, col2 = st.columns(2)
# col1.markdown(
#     f"<div class='metallic-card'><h2>{trained_users_count}</h2><p>Total Trained Users</p></div>",
#     unsafe_allow_html=True
# )
# col2.markdown(
#     f"<div class='metallic-card'><h2>{systems_count}</h2><p>Total Systems</p></div>",
#     unsafe_allow_html=True
# )
#
# # -----------------------------
# # Table of Trained Users
# # -----------------------------
# st.subheader("Trained Users")
# if st.session_state.trained_users:
#     st.dataframe(st.session_state.trained_users)
# else:
#     st.info("No users have been trained yet.")
#
# # -----------------------------
# # Registration Form
# # -----------------------------
# st.markdown("---")
# st.subheader("Register Users for a System")
#
# with st.form("user_form"):
#
#     # Select system
#     selected_system_name = st.selectbox(
#         "Select System",
#         options=[s['name'] for s in st.session_state.systems],
#         key="system_select"
#     )
#
#     # Get system ID
#     system_id = next(s['id'] for s in st.session_state.systems if s['name'] == selected_system_name)
#     st.session_state.selected_system_id = system_id
#
#     # Load untrained employees for selected system dynamically
#     employee_list = load_untrained_for_system(system_id)
#     employee_options = [f"{e['id']} - {e['name']}" for e in employee_list]
#
#     selected_employees = st.multiselect(
#         "Select Employees",
#         options=employee_options,
#         help="Selected employees appear as removable chips"
#     )
#
#     submit = st.form_submit_button(
#         "Register Users",
#         disabled=(len(employee_options) == 0)
#     )
#
#     if len(employee_options) == 0:
#         st.warning("All employees have been trained for this system.")
#
# # -----------------------------
# # Insert into DB + Refresh
# # -----------------------------
# if submit and selected_employees:
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
#
#         inserted = 0
#         for emp in selected_employees:
#             emp_id = int(emp.split(" - ")[0])
#             cur.execute("""
#                 INSERT INTO user_systems (user_id, system_id)
#                 VALUES (%s, %s)
#                 ON CONFLICT (user_id, system_id) DO NOTHING;
#             """, (emp_id, system_id))
#             if cur.rowcount > 0:
#                 inserted += 1
#
#         conn.commit()
#         cur.close()
#         conn.close()
#
#         if inserted > 0:
#             st.toast(f"{inserted} user(s) successfully registered ✅")
#         else:
#             st.warning("Selected user(s) were already registered for this system.")
#
#         # Refresh table and autocomplete
#         st.session_state.trained_users = load_trained_users()
#
#     except Exception as e:
#         st.error(f"Database error: {e}")
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Employee Training Registration", layout="wide")
st.title("Employee Training Registration")

# -----------------------------
# PostgreSQL connection
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="training",
        user="postgres",
        password="123456",
        port=5432
    )

# -----------------------------
# Load data functions
# -----------------------------
def load_trained_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT e.id AS employee_id,
               e.name AS employee_name,
               s.name AS system_name,
               us.assigned_date
        FROM user_systems us
        JOIN employees e ON e.id = us.user_id
        JOIN systems s ON s.id = us.system_id
        ORDER BY e.name, s.name
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def load_systems():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM systems ORDER BY name;")
    systems = cur.fetchall()
    cur.close()
    conn.close()
    return systems

def load_untrained_for_system(system_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id, name FROM employees
        WHERE id NOT IN (
            SELECT user_id FROM user_systems WHERE system_id = %s
        )
        ORDER BY name
    """, (system_id,))
    employees = cur.fetchall()
    cur.close()
    conn.close()
    return employees

# -----------------------------
# Initialize session_state
# -----------------------------
if 'trained_users' not in st.session_state:
    st.session_state.trained_users = load_trained_users()
if 'systems' not in st.session_state:
    st.session_state.systems = load_systems()

# -----------------------------
# Metallic Cards CSS
# -----------------------------
st.markdown("""
<style>
.metallic-card {
    background: linear-gradient(145deg, #d4d4d4, #f0f0f0);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: #000;
    box-shadow: 4px 4px 10px #aaa, -4px -4px 10px #fff;
    margin-bottom: 10px;
}
.metallic-card h2 {
    margin: 0;
    font-size: 32px;
}
.metallic-card p {
    margin: 0;
    font-size: 16px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Top Cards
# -----------------------------
trained_users_count = len({tu['employee_id'] for tu in st.session_state.trained_users})
systems_count = len(st.session_state.systems)

col1, col2 = st.columns(2)
col1.markdown(
    f"<div class='metallic-card'><h2>{trained_users_count}</h2><p>Total Trained Users</p></div>",
    unsafe_allow_html=True
)
col2.markdown(
    f"<div class='metallic-card'><h2>{systems_count}</h2><p>Total Systems</p></div>",
    unsafe_allow_html=True
)

# -----------------------------
# Table of Trained Users
# -----------------------------
st.subheader("Trained Users")
if st.session_state.trained_users:
    st.dataframe(st.session_state.trained_users)
else:
    st.info("No users have been trained yet.")

# -----------------------------
# Registration Form
# -----------------------------
st.markdown("---")
st.subheader("Register Users for a System")

# Select system OUTSIDE the form
selected_system_name = st.selectbox(
    "Select System",
    options=[s['name'] for s in st.session_state.systems],
    key="system_select"
)

# Get system ID
system_id = next(s['id'] for s in st.session_state.systems if s['name'] == selected_system_name)

# Load untrained employees for selected system dynamically
employee_list = load_untrained_for_system(system_id)
employee_options = [f"{e['id']} - {e['name']}" for e in employee_list]

# Now use the form only for the multiselect and submit button
with st.form("user_form"):
    selected_employees = st.multiselect(
        "Select Employees",
        options=employee_options,
        help="Selected employees appear as removable chips"
    )

    submit = st.form_submit_button(
        "Register Users",
        disabled=(len(employee_options) == 0)
    )

if len(employee_options) == 0:
    st.warning("All employees have been trained for this system.")

# -----------------------------
# Insert into DB + Refresh
# -----------------------------
if submit and selected_employees:
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        inserted = 0
        for emp in selected_employees:
            emp_id = int(emp.split(" - ")[0])
            cur.execute("""
                INSERT INTO user_systems (user_id, system_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, system_id) DO NOTHING;
            """, (emp_id, system_id))
            if cur.rowcount > 0:
                inserted += 1

        conn.commit()
        cur.close()
        conn.close()

        if inserted > 0:
            st.success(f"✅ {inserted} user(s) successfully registered!")
        else:
            st.warning("Selected user(s) were already registered for this system.")

        # Refresh table
        st.session_state.trained_users = load_trained_users()
        st.rerun()  # Force refresh to update the UI

    except Exception as e:
        st.error(f"Database error: {e}")