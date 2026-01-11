import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor
import pandas as pd
import math
from datetime import date

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Employee Training Registration", layout="wide")

# -----------------------------
# CSS Styles
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}
.toast-container {
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 999999;
}
.toast {
    min-width: 300px;
    max-width: 400px;
    color: #fff;
    border-radius: 8px;
    padding: 16px 20px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: slideIn 0.3s ease-out, slideOut 0.3s ease-in 2.7s forwards;
}
@keyframes slideIn {
    from { transform: translateX(400px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
@keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(400px); opacity: 0; }
}
.toast.success {
    background: linear-gradient(135deg, #4BB543 0%, #3a9635 100%);
    border-left: 4px solid #2d7528;
}
.toast.error {
    background: linear-gradient(135deg, #FF4136 0%, #cc342b 100%);
    border-left: 4px solid #991f1f;
}
.toast.warning {
    background: linear-gradient(135deg, #FF851B 0%, #cc6a16 100%);
    border-left: 4px solid #995011;
}
.metric-card {
    background: linear-gradient(145deg, #f5f5f7 0%, #e8e8ed 100%);
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 
        0 2px 8px rgba(0, 0, 0, 0.04),
        0 1px 3px rgba(0, 0, 0, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.6);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    gap: 16px;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 4px 16px rgba(0, 0, 0, 0.08),
        0 2px 6px rgba(0, 0, 0, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
}
.metric-icon {
    font-size: 28px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}
.metric-content {
    flex: 1;
}
.metric-value {
    font-size: 32px;
    font-weight: 600;
    color: #1d1d1f;
    line-height: 1;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    letter-spacing: -0.5px;
}
.metric-label {
    font-size: 13px;
    font-weight: 500;
    color: #6e6e73;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}
.pagination-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
    border-top: 1px solid #e0e0e0;
    margin-top: 10px;
}
.pagination-info {
    font-size: 14px;
    color: #666;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# DB connection
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="training",
        user="postgres",
        password="123456",
        cursor_factory=RealDictCursor
    )


# -----------------------------
# Load functions
# -----------------------------
@st.cache_data(ttl=1)
def load_trained_users():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT e.id   AS employee_id,
                               e.name AS employee_name,
                               s.name AS system_name,
                               us.training_date,
                               us.assigned_date
                        FROM user_systems us
                                 JOIN employees e ON e.id = us.user_id
                                 JOIN systems s ON s.id = us.system_id
                        ORDER BY us.assigned_date DESC, e.name, s.name
                        """)
            return cur.fetchall()

@st.cache_data(ttl=60)
def load_systems():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM systems ORDER BY name")
            return cur.fetchall()


@st.cache_data(ttl=1)
def load_untrained_for_system(system_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT id, name
                        FROM employees
                        WHERE id NOT IN (SELECT user_id FROM user_systems WHERE system_id = %s)
                        ORDER BY name
                        """, (system_id,))
            return cur.fetchall()


# -----------------------------
# Initialize session state
# -----------------------------
if "systems" not in st.session_state:
    st.session_state.systems = load_systems()
if "trained_users" not in st.session_state:
    st.session_state.trained_users = load_trained_users()
if "show_confirm_dialog" not in st.session_state:
    st.session_state.show_confirm_dialog = False
if "pending_registration" not in st.session_state:
    st.session_state.pending_registration = None
if "show_toast" not in st.session_state:
    st.session_state.show_toast = False
if "toast_message" not in st.session_state:
    st.session_state.toast_message = ""
if "toast_type" not in st.session_state:
    st.session_state.toast_type = "success"
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "rows_per_page" not in st.session_state:
    st.session_state.rows_per_page = 10

# -----------------------------
# Display toast
# -----------------------------
if st.session_state.show_toast and st.session_state.toast_message:
    st.markdown(f"""
    <div class="toast-container">
        <div class="toast {st.session_state.toast_type}">
            {st.session_state.toast_message}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.show_toast = False

# -----------------------------
# Title & Metrics
# -----------------------------
st.title("🎓 Employee Training Registration System")

trained_users_count = len({u["employee_id"] for u in st.session_state.trained_users})
systems_count = len(st.session_state.systems)
total_registrations = len(st.session_state.trained_users)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
            <div class="metric-value">{trained_users_count}</div>
            <div class="metric-label">Trained Users</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💻</div>
        <div class="metric-content">
            <div class="metric-value">{systems_count}</div>
            <div class="metric-label">Total Systems</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📋</div>
        <div class="metric-content">
            <div class="metric-value">{total_registrations}</div>
            <div class="metric-label">Total Registrations</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# Trained users table with pagination
# -----------------------------
st.subheader("📊 Trained Users")

if st.session_state.trained_users:
    df = pd.DataFrame(st.session_state.trained_users)

    # Rename columns to title case
    df.columns = df.columns.str.replace('_', ' ').str.title()

    total_rows = len(df)

    # Calculate pagination
    total_pages = math.ceil(total_rows / st.session_state.rows_per_page)

    # Ensure current page is within valid range
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages
    if st.session_state.current_page < 1:
        st.session_state.current_page = 1

    # Calculate start and end indices
    start_idx = (st.session_state.current_page - 1) * st.session_state.rows_per_page
    end_idx = start_idx + st.session_state.rows_per_page

    # Display paginated dataframe
    paginated_df = df.iloc[start_idx:end_idx]
    st.dataframe(paginated_df, use_container_width=True, hide_index=True)

    # Pagination controls at bottom
    st.markdown('<div class="pagination-container">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 3, 1])

    with col1:
        st.markdown(
            f'<p class="pagination-info">Showing {start_idx + 1}-{min(end_idx, total_rows)} of {total_rows} entries</p>',
            unsafe_allow_html=True)

    with col2:
        pcol1, pcol2, pcol3, pcol4, pcol5, pcol6 = st.columns([1, 1, 2, 1, 1, 1])

        with pcol1:
            if st.button("«", disabled=(st.session_state.current_page == 1), key="first_page"):
                st.session_state.current_page = 1
                st.rerun()

        with pcol2:
            if st.button("‹", disabled=(st.session_state.current_page == 1), key="prev_page"):
                st.session_state.current_page -= 1
                st.rerun()

        with pcol3:
            st.markdown(
                f"<p style='text-align: center; margin-top: 8px;'>Page {st.session_state.current_page} of {total_pages}</p>",
                unsafe_allow_html=True)

        with pcol4:
            if st.button("›", disabled=(st.session_state.current_page == total_pages), key="next_page"):
                st.session_state.current_page += 1
                st.rerun()

        with pcol5:
            if st.button("»", disabled=(st.session_state.current_page == total_pages), key="last_page"):
                st.session_state.current_page = total_pages
                st.rerun()

        with pcol6:
            pass  # Empty column for spacing

    with col3:
        new_rows_per_page = st.selectbox(
            "Show:",
            options=[10, 25, 50, 100],
            index=0,
            key="rows_per_page_selector",
            label_visibility="collapsed"
        )
        if new_rows_per_page != st.session_state.rows_per_page:
            st.session_state.rows_per_page = new_rows_per_page
            st.session_state.current_page = 1
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("No trained users yet.")

# -----------------------------
# Registration Form
# -----------------------------
st.markdown("---")
st.subheader("➕ Register Users for a System")

systems = st.session_state.systems
if not systems:
    st.warning("No systems available. Please add systems first.")
    st.stop()

# Confirmation Dialog
if st.session_state.show_confirm_dialog and st.session_state.pending_registration:
    pending = st.session_state.pending_registration

    st.markdown('<div class="confirm-dialog">', unsafe_allow_html=True)
    st.warning(f"⚠️ **Confirm Registration**")
    st.write(
        f"Are you sure you want to register **{len(pending['employees'])} employee(s)** for **{pending['system_name']}**?")
    st.write(f"**Training Date:** {pending['training_date']}")

    with st.expander("View Selected Employees"):
        for emp in pending['employees']:
            st.write(f"- {emp}")

    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("✅ Confirm", type="primary", use_container_width=True, key="confirm_btn"):
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        registered_count = 0
                        for emp in pending['employees']:
                            emp_id = int(emp.split(" - ")[0])
                            cur.execute("""
                                        INSERT INTO user_systems (user_id, system_id, training_date)
                                        VALUES (%s, %s, %s) ON CONFLICT (user_id, system_id) DO NOTHING
                                RETURNING user_id
                                        """, (emp_id, pending['system_id'], pending['training_date']))
                            if cur.fetchone():
                                registered_count += 1
                        conn.commit()

                load_trained_users.clear()
                load_untrained_for_system.clear()

                st.session_state.trained_users = load_trained_users()
                st.session_state.show_confirm_dialog = False
                st.session_state.pending_registration = None
                st.session_state.show_toast = True
                st.session_state.toast_message = f"✅ Successfully registered {registered_count} employee(s)!"
                st.session_state.toast_type = "success"
                st.rerun()
            except Exception as e:
                st.session_state.show_confirm_dialog = False
                st.session_state.pending_registration = None
                st.session_state.show_toast = True
                st.session_state.toast_message = f"❌ Error: {str(e)}"
                st.session_state.toast_type = "error"
                st.rerun()

    with col2:
        if st.button("❌ Cancel", use_container_width=True, key="cancel_btn"):
            st.session_state.show_confirm_dialog = False
            st.session_state.pending_registration = None
            st.session_state.show_toast = True
            st.session_state.toast_message = "ℹ️ Registration cancelled"
            st.session_state.toast_type = "warning"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# System selection
system_options = {s["name"]: s["id"] for s in systems}
selected_system_name = st.selectbox(
    "Select System",
    options=list(system_options.keys()),
    key="system_selector"
)

selected_system_id = system_options[selected_system_name]

# Training date input
training_date = st.date_input(
    "Training Date",
    value=date.today(),
    help="Select the date when the training was completed"
)

# Load employees for selected system
employees = load_untrained_for_system(selected_system_id)

if not employees:
    st.info(f"ℹ️ All employees are already trained for {selected_system_name}")
    employee_options = []
else:
    employee_options = [f"{e['id']} - {e['name']}" for e in employees]

# Employee selection
selected_employees = st.multiselect(
    "Select Employees to Register",
    options=employee_options,
    help="Select one or more employees to register for the selected system",
    key=f"employee_selector_{selected_system_id}"
)

# Submit button
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("📝 Register Users", type="primary", use_container_width=True, key="submit_btn"):
        if not selected_employees:
            st.session_state.show_toast = True
            st.session_state.toast_message = "⚠️ Please select at least one employee"
            st.session_state.toast_type = "warning"
            st.rerun()
        else:
            st.session_state.pending_registration = {
                'system_id': selected_system_id,
                'system_name': selected_system_name,
                'employees': selected_employees,
                'training_date': training_date
            }
            st.session_state.show_confirm_dialog = True
            st.rerun()