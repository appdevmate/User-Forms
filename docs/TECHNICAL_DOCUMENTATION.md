# Employee Training System - Technical Documentation
## Code Explanation for Beginners

This document explains the code line by line.

## Table of Contents
1. [Imports](#imports)
2. [Page Setup](#page-setup)  
3. [CSS Styling](#css-styling)
4. [Database Config](#database-config)
5. [Data Functions](#data-functions)
6. [Session State](#session-state)
7. [UI Components](#ui-components)
8. [Registration Flow](#registration-flow)

---

## Imports

### Line 1: psycopg2
```python
import psycopg2
```
**What it does**: Connects Python to PostgreSQL.
**Why**: To run database operations.

### Line 2: Streamlit
```python
import streamlit as st
```
**What it does**: Creates web interface.
**Why 'as st'**: Shorter to type `st.button()`.

### Line 3: RealDictCursor
```python
from psycopg2.extras import RealDictCursor
```
**What it does**: Returns data as dictionaries.
**Example**: `{'id': 1, 'name': 'John'}` instead of `(1, 'John')`

### Line 4: pandas
```python
import pandas as pd
```
**What it does**: Handles data tables.
**Use**: Converts data to DataFrames.

### Line 5: math  
```python
import math
```
**What it does**: Math operations.
**Use**: `math.ceil()` rounds up for pagination.

### Line 6: date
```python
from datetime import date
```
**What it does**: Handles dates.
**Use**: `date.today()` for training date input.

---

## Page Setup

```python
st.set_page_config(page_title="Employee Training Registration", layout="wide")
```

**What it does**: Sets up Streamlit page.

**Settings**:
- `page_title` - Browser tab title
- `layout="wide"` - Full width layout

**Important**: Must be first Streamlit command!

---

## CSS Styling

### Adding CSS

```python
st.markdown("""
<style>
...
</style>
""", unsafe_allow_html=True)
```

**What it does**: Adds custom styles.
**Why**: Customize colors, spacing, animations.

### Key Styles

**Remove padding**:
```css
.block-container {
    padding-top: 2rem !important;
}
```
Reduces empty space at top.

**Toast position**:
```css
.toast-container {
    position: fixed;
    top: 80px;
    right: 20px;
}
```
Puts notifications in top-right corner.

**Metric cards**:
```css
.metric-card {
    background: linear-gradient(...);
    border-radius: 16px;
}
```
Creates Apple-style cards.

---

## Database Config

### Connection Function

```python
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="training",
        user="postgres",
        password="123456",
        cursor_factory=RealDictCursor
    )
```

**What it does**: Creates connection to PostgreSQL.

**Settings explained**:
- `host="localhost"` - Database is on same computer
- `port="5432"` - PostgreSQL default port
- `database="training"` - Database name
- `user="postgres"` - Username
- `password="123456"` - Password (change this!)
- `cursor_factory=RealDictCursor` - Return data as dictionaries

**How to change**:
1. Update `host` if database is on different server
2. Change `database` to your database name
3. Update `user` and `password` with your credentials

**Security tip**: Don't hardcode passwords! Use environment variables.

---

## Data Functions

### Load Trained Users

```python
@st.cache_data(ttl=1)
def load_trained_users():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""...""")
            return cur.fetchall()
```

**What it does**: Gets all training records from database.

**Code explained**:
- `@st.cache_data(ttl=1)` - Cache results for 1 second
- `with get_db_connection()` - Open database connection
- `with conn.cursor()` - Create cursor to run queries
- `cur.execute("""...""")` - Run SQL query
- `return cur.fetchall()` - Return all results

**Why cache?** Avoids slow database queries on every page refresh.

**Returns**:
```python
[
    {'employee_id': 1, 'employee_name': 'John', 'system_name': 'SAP', 
     'training_date': date(2024, 1, 15), 'assigned_date': datetime(...)},
    ...
]
```

### Load Systems

```python
@st.cache_data(ttl=60)
def load_systems():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM systems ORDER BY name")
            return cur.fetchall()
```

**What it does**: Gets all available systems.

**Cached for 60 seconds** because systems rarely change.

**Returns**:
```python
[
    {'id': 1, 'name': 'Oracle ERP'},
    {'id': 2, 'name': 'SAP'},
    ...
]
```

### Load Untrained Employees

```python
@st.cache_data(ttl=1)
def load_untrained_for_system(system_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""...""", (system_id,))
            return cur.fetchall()
```

**What it does**: Gets employees NOT trained for a specific system.

**Parameter**: `system_id` - which system to check

**Returns**:
```python
[
    {'id': 3, 'name': 'Bob Johnson'},
    {'id': 4, 'name': 'Alice Williams'},
    ...
]
```

**Note**: `(system_id,)` is a tuple - prevents SQL injection.

---

## Session State

### What is Session State?

Streamlit reruns the script on every interaction. Session state saves data between reruns.

### Initialization

```python
if "systems" not in st.session_state:
    st.session_state.systems = load_systems()
```

**What it does**: Loads systems once and stores them.

**Flow**:
```
Run 1: Load from database → Store in state
Run 2: Use stored value → Skip database
```

### All Session Variables

```python
st.session_state.systems              # List of systems
st.session_state.trained_users        # Training records
st.session_state.show_confirm_dialog  # Show dialog? (True/False)
st.session_state.pending_registration # Registration data
st.session_state.show_toast           # Show toast? (True/False)
st.session_state.toast_message        # Toast message text
st.session_state.toast_type           # Type: success/warning/error
st.session_state.current_page         # Current page number
st.session_state.rows_per_page        # Rows per page (10/25/50/100)
```

---

## UI Components

### Toast Display

```python
if st.session_state.show_toast and st.session_state.toast_message:
    st.markdown(f"""
    <div class="toast-container">
        <div class="toast {st.session_state.toast_type}">
            {st.session_state.toast_message}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.show_toast = False
```

**What it does**: Shows notification in top-right.

**Logic**:
1. Check if toast should show
2. Display HTML with message
3. Reset flag to False

### Title

```python
st.title("🎓 Employee Training Registration System")
```

**What it does**: Shows main heading with emoji.

### Metric Cards

```python
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
```

**What it does**: Creates 3 metric cards in columns.

**Code explained**:
- `st.columns(3)` - Create 3 equal columns
- `with col1:` - Put content in first column
- `st.markdown(f"""...""")` - Insert HTML with values

### DataFrame with Pagination

```python
df = pd.DataFrame(st.session_state.trained_users)
df.columns = df.columns.str.replace('_', ' ').str.title()
```

**What it does**: Creates table and formats column names.

**Column transformation**:
```
employee_id → Employee Id
training_date → Training Date
```

### Pagination Calculation

```python
total_pages = math.ceil(total_rows / st.session_state.rows_per_page)
start_idx = (st.session_state.current_page - 1) * st.session_state.rows_per_page
end_idx = start_idx + st.session_state.rows_per_page
paginated_df = df.iloc[start_idx:end_idx]
```

**What it does**: Splits data into pages.

**Example**:
```
Total rows: 45, Rows per page: 10
Total pages: 5

Page 1: rows 0-9
Page 2: rows 10-19
Page 3: rows 20-29
...
```

### Pagination Buttons

```python
if st.button("«", disabled=(st.session_state.current_page == 1), key="first_page"):
    st.session_state.current_page = 1
    st.rerun()
```

**What it does**: Jump to first page button.

**Code explained**:
- `st.button("«")` - Button with double arrow
- `disabled=(...)` - Disable if on page 1
- `st.session_state.current_page = 1` - Set to page 1
- `st.rerun()` - Refresh page to show changes

---

## Registration Flow

### System Selection

```python
system_options = {s["name"]: s["id"] for s in systems}
selected_system_name = st.selectbox(
    "Select System",
    options=list(system_options.keys()),
    key="system_selector"
)
selected_system_id = system_options[selected_system_name]
```

**What it does**: Shows dropdown of systems.

**Code explained**:
- Dictionary maps names to IDs: `{'SAP': 1, 'Oracle': 2}`
- Dropdown shows names
- Get ID for selected name

### Training Date Input

```python
training_date = st.date_input(
    "Training Date",
    value=date.today(),
    help="Select the date when the training was completed"
)
```

**What it does**: Shows date picker.

**Settings**:
- `value=date.today()` - Defaults to today
- `help="..."` - Tooltip text

### Employee Multiselect

```python
selected_employees = st.multiselect(
    "Select Employees to Register",
    options=employee_options,
    key=f"employee_selector_{selected_system_id}"
)
```

**What it does**: Multi-selection dropdown.

**Dynamic key**: `f"employee_selector_{selected_system_id}"`
- Creates new widget per system
- Auto-clears when system changes

### Submit and Validation

```python
if st.button("📝 Register Users", ...):
    if not selected_employees:
        st.session_state.show_toast = True
        st.session_state.toast_message = "⚠️ Select at least one"
        st.rerun()
    else:
        st.session_state.pending_registration = {...}
        st.session_state.show_confirm_dialog = True
        st.rerun()
```

**What it does**: Validates and stores registration data.

**Flow**:
1. User clicks Register
2. Check if employees selected
3. If none: Show warning
4. If some: Store data and show dialog

### Confirmation Dialog

```python
if st.session_state.show_confirm_dialog:
    st.warning("⚠️ **Confirm Registration**")
    st.write(f"Register {len(pending['employees'])} for {pending['system_name']}?")
    st.write(f"**Training Date:** {pending['training_date']}")
```

**What it does**: Shows confirmation before saving.

### Database Insert

```python
for emp in pending['employees']:
    emp_id = int(emp.split(" - ")[0])
    cur.execute("""
        INSERT INTO user_systems (user_id, system_id, training_date)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING user_id
    """, (emp_id, pending['system_id'], pending['training_date']))
    if cur.fetchone():
        registered_count += 1
conn.commit()
```

**What it does**: Saves records to database.

**Code explained**:
- Loop through each employee
- Extract ID from "3 - Bob" → 3
- Insert into database
- Skip if duplicate exists
- Count successful inserts
- Commit all changes

### Success Handling

```python
load_trained_users.clear()
load_untrained_for_system.clear()
st.session_state.trained_users = load_trained_users()
st.session_state.show_toast = True
st.session_state.toast_message = "✅ Registered!"
st.rerun()
```

**What it does**: Updates UI after save.

**Steps**:
1. Clear caches
2. Reload fresh data
3. Show success toast
4. Refresh page

---

## Two Dates Explained

### Training Date (User Input)
```python
training_date = st.date_input("Training Date", value=date.today())
```
- When employee was actually trained
- User selects this
- Can be past, present, or future

### Assigned Date (Auto Timestamp)
- Set automatically by database
- Default value: `CURRENT_TIMESTAMP`
- When record was created

### Example
```
Employee trained: Jan 15, 2024
Record created: Jan 20, 2024

Database stores:
- training_date: 2024-01-15
- assigned_date: 2024-01-20 10:30:00
```

---

## Summary

This code creates a training registration system with:

**Core Features**:
- Database connection and queries
- Data caching for performance
- Session state management
- Paginated data tables
- Date input for training dates
- Multi-select for employees
- Confirmation dialogs
- Toast notifications

**Key Concepts**:
- `@st.cache_data` - Speed up queries
- `st.session_state` - Save data between reruns
- `with` statement - Auto-close connections
- f-strings - Insert variables in text
- Dictionary comprehension - Create mappings

Happy coding! 🚀
