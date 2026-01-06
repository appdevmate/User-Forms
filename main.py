import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # Load .env for local development

# Update env only if secrets exist (avoids FileNotFoundError)
if hasattr(st, "secrets") and st.secrets is not None:
    try:
        os.environ.update(st.secrets)
    except FileNotFoundError:
        pass  # ignore if secrets.toml is missing locally


# -----------------------------
# Streamlit config
# -----------------------------
st.set_page_config(page_title="Employee Training Registration", layout="wide")
st.title("Employee Training Registration")

# -----------------------------
# PostgreSQL connection
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        cursor_factory=RealDictCursor
    )

# -----------------------------
# Load data functions
# -----------------------------
def load_trained_users():
    conn = get_db_connection()
    cur = conn.cursor()
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
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM systems ORDER BY name;")
    systems = cur.fetchall()
    cur.close()
    conn.close()
    return systems

def load_untrained_for_system(system_id):
    conn = get_db_connection()
    cur = conn.cursor()
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
# Initialize session state
# -----------------------------
if "trained_users" not in st.session_state:
    st.session_state.trained_users = load_trained_users()

if "systems" not in st.session_state:
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
trained_users_count = len({u["employee_id"] for u in st.session_state.trained_users})
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

selected_system_name = st.selectbox(
    "Select System",
    options=[s["name"] for s in st.session_state.systems]
)

system_id = next(
    s["id"] for s in st.session_state.systems if s["name"] == selected_system_name
)

employee_list = load_untrained_for_system(system_id)
employee_options = [f"{e['id']} - {e['name']}" for e in employee_list]

with st.form("user_form"):
    selected_employees = st.multiselect(
        "Select Employees",
        options=employee_options
    )

    submit = st.form_submit_button(
        "Register Users",
        disabled=(len(employee_options) == 0)
    )

if len(employee_options) == 0:
    st.warning("All employees have been trained for this system.")

# -----------------------------
# Insert + Refresh
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
                ON CONFLICT (user_id, system_id) DO NOTHING
            """, (emp_id, system_id))

            if cur.rowcount > 0:
                inserted += 1

        conn.commit()
        cur.close()
        conn.close()

        if inserted > 0:
            st.success(f"{inserted} user(s) successfully registered.")
        else:
            st.warning("Selected users were already registered.")

        st.session_state.trained_users = load_trained_users()
        st.rerun()

    except Exception as e:
        st.error(f"Database error: {e}")
