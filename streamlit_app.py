"""
AA Tracker - A Streamlit App
Meeting attendance and treasury tracking for AA groups
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from pathlib import Path
import sqlite3

# Configure page
st.set_page_config(
    page_title="AA Tracker",
    page_icon="🍀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Password protection
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

APP_PASSWORD = "nick123"

def check_password():
    """Show login screen if not authenticated"""
    if st.session_state.authenticated:
        return True
    
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background-color: #262730;
            border-radius: 10px;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🍀 AA Tracker")
    st.write("Please enter your password to access the app:")
    
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    
    st.markdown("---")
    st.caption("Contact Nick if you forgot your password")
    return False

if not check_password():
    st.stop()

# Custom dark theme CSS - Mobile responsive
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stSidebar {
        background-color: #262730;
    }
    .stTextInput, .stNumberInput, .stSelectbox, .stDateInput, .stTimeInput {
        background-color: #262730;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .income {
        color: #4ade80 !important;
    }
    .expense {
        color: #f87171 !important;
    }
    .stButton>button {
        background-color: #4ade80;
        color: #0e1117;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #22c55e;
    }
    .stButton>button[kind="secondary"] {
        background-color: #4a5568;
        color: #fafafa;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #2d3748;
    }
    .stButton>button[kind="danger"] {
        background-color: #f87171;
        color: #0e1117;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Mobile: Hide sidebar nav, show top nav instead */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .stRadio > div {
            flex-direction: row !important;
            flex-wrap: wrap !important;
            justify-content: center;
        }
        div[data-testid="stRadio"] > div > label {
            padding: 8px 12px !important;
            margin: 4px !important;
            font-size: 0.8rem !important;
        }
        div[data-testid="stMetric"] {
            padding: 0.5rem !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        .stForm > div[data-testid="stFormRow"] {
            flex-direction: column !important;
            gap: 0.75rem !important;
        }
        .stButton > button {
            min-height: 48px !important;
            font-size: 1rem !important;
            width: 100% !important;
            margin-top: 0.5rem !important;
        }
    }
    /* Quick Add section styling */
    .quick-add-header {
        font-size: 1.1rem;
        font-weight: 600;
    }
    /* Delete confirmation modal */
    .delete-confirm {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #f87171;
    }
</style>
""", unsafe_allow_html=True)

# Database setup
DB_PATH = Path(__file__).parent / "aa_tracker.db"

def get_db_connection():
    """Get database connection"""
    import sqlite3
    return sqlite3.connect(DB_PATH)

def clear_cache():
    """Clear all cached data after modifications"""
    get_meetings.clear()
    get_attendance.clear()
    get_categories.clear()
    get_transactions.clear()
    get_treasury_balance.clear()
    get_monthly_summary.clear()

# Helper functions
@st.cache_data(ttl=60)
def get_meetings(active_only=True):
    """Get meetings from database"""
    conn = get_db_connection()
    if active_only:
        df = pd.read_sql("SELECT * FROM meeting WHERE is_active = 1 ORDER BY day_of_week, time", conn)
    else:
        df = pd.read_sql("SELECT * FROM meeting ORDER BY day_of_week, time", conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def get_attendance(limit=200):
    """Get attendance records"""
    conn = get_db_connection()
    df = pd.read_sql(f"""
        SELECT a.id, a.date, a.role, a.notes, a.meeting_id,
               m.name as meeting_name, m.day_of_week, m.time, m.location
        FROM attendance a
        JOIN meeting m ON a.meeting_id = m.id
        ORDER BY a.date DESC, m.time
        LIMIT {limit}
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def get_categories(category_type=None):
    """Get categories from database"""
    conn = get_db_connection()
    if category_type:
        df = pd.read_sql(f"SELECT * FROM category WHERE type = '{category_type}' AND is_active = 1", conn)
    else:
        df = pd.read_sql("SELECT * FROM category WHERE is_active = 1", conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def get_transactions(limit=100):
    """Get treasury transactions"""
    conn = get_db_connection()
    df = pd.read_sql(f"""
        SELECT t.id, t.date, t.amount, t.type, t.description, t.meeting_name, t.notes,
               c.name as category, c.type as cat_type
        FROM "transaction" t
        LEFT JOIN category c ON t.category_id = c.id
        ORDER BY t.date DESC, t.id DESC
        LIMIT {limit}
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def get_treasury_balance():
    """Calculate total treasury balance"""
    conn = get_db_connection()
    df = pd.read_sql("""
        SELECT 
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM "transaction"
    """, conn)
    conn.close()
    income = df['total_income'].iloc[0] or 0
    expense = df['total_expense'].iloc[0] or 0
    return income - expense

@st.cache_data(ttl=60)
def get_monthly_summary(year=None, month=None):
    """Get monthly income/expense summary"""
    conn = get_db_connection()
    if year and month:
        filter_str = f"WHERE strftime('%Y', date) = '{year}' AND strftime('%m', date) = '{month:02d}'"
    else:
        filter_str = ""
    
    df = pd.read_sql(f"""
        SELECT 
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM "transaction"
        {filter_str}
    """, conn)
    conn.close()
    return df

# Database operations
def add_meeting(name, day_of_week, time, location, format_type, is_treasurer_duty, notes):
    """Add a new meeting"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO meeting (name, day_of_week, time, location, format_type, is_treasurer_duty, notes, is_active) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
              (name, day_of_week, time, location, format_type, is_treasurer_duty, notes))
    conn.commit()
    conn.close()
    clear_cache()

def update_meeting(meeting_id, name, day_of_week, time, location, format_type, is_treasurer_duty, notes, is_active):
    """Update a meeting"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""UPDATE meeting SET name=?, day_of_week=?, time=?, location=?, format_type=?, 
                 is_treasurer_duty=?, notes=?, is_active=? WHERE id=?""",
              (name, day_of_week, time, location, format_type, is_treasurer_duty, notes, is_active, meeting_id))
    conn.commit()
    conn.close()
    clear_cache()

def delete_meeting(meeting_id):
    """Delete (deactivate) a meeting"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE meeting SET is_active = 0 WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()
    clear_cache()

def add_attendance(meeting_id, date_val, role, notes):
    """Record attendance"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO attendance (meeting_id, date, role, notes) 
                 VALUES (?, ?, ?, ?)""",
              (meeting_id, date_val, role, notes))
    conn.commit()
    conn.close()
    clear_cache()

def add_transaction(date_val, amount, category_id, tx_type, description, meeting_name, notes):
    """Add a treasury transaction"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO "transaction" (date, amount, category_id, type, description, meeting_name, notes) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (date_val, amount, category_id, tx_type, description, meeting_name, notes))
    conn.commit()
    conn.close()
    clear_cache()

def delete_transaction(tx_id):
    """Delete a transaction"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM "transaction" WHERE id = ?', (tx_id,))
    conn.commit()
    conn.close()
    clear_cache()

def add_category(name, cat_type, description):
    """Add a new category"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO category (name, type, description, is_active) 
                 VALUES (?, ?, ?, 1)""",
              (name, cat_type, description))
    conn.commit()
    conn.close()
    clear_cache()

# Navigation
pages = ["📊 Dashboard", "📅 Meetings", "✅ Check In", "📜 History", "💰 Treasury"]

st.title("🍀 AA Tracker")

# Create navigation
page = st.radio(
    "Navigate",
    pages + ["🔒 Logout"],
    horizontal=True,
    label_visibility="collapsed"
)

# Handle logout
if page == "🔒 Logout":
    st.session_state.authenticated = False
    st.rerun()

today = date.today()
current_year = today.year
current_month = today.month

DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Page: Dashboard
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # Get data
    meetings = get_meetings()
    attendance = get_attendance(100)
    balance = get_treasury_balance()
    
    # Attendance streak calculation
    streak = 0
    if not attendance.empty:
        # Get unique dates sorted
        unique_dates = sorted(attendance['date'].unique(), reverse=True)
        if unique_dates:
            # Check consecutive days
            check_date = today
            for d in unique_dates:
                d_date = date.fromisoformat(d) if isinstance(d, str) else d
                if d_date == check_date or d_date == check_date - timedelta(days=1):
                    streak += 1
                    check_date = d_date
                else:
                    break
    
    # Upcoming meetings this week
    this_week_meetings = []
    if not meetings.empty:
        current_day = today.weekday()  # 0=Monday
        for _, m in meetings.iterrows():
            if m['day_of_week'] >= current_day:
                this_week_meetings.append({
                    'name': m['name'],
                    'day': DAY_NAMES[m['day_of_week']],
                    'time': m['time'],
                    'location': m['location'],
                    'format': m['format_type']
                })
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Attendance Streak", f"{streak} days")
    with col2:
        st.metric("💰 Treasury Balance", f"${balance:,.2f}")
    with col3:
        st.metric("📅 Meetings This Week", len(this_week_meetings))
    with col4:
        st.metric("👥 Total Members", attendance['role'].count())
    
    # This week's meetings
    st.markdown("---")
    st.subheader("📅 Upcoming Meetings This Week")
    
    if this_week_meetings:
        for m in this_week_meetings:
            st.write(f"**{m['name']}** - {m['day']} at {m['time']} | 📍 {m['location']} | {m['format']}")
    else:
        st.info("No more meetings scheduled this week")
    
    # Recent activity
    st.markdown("---")
    st.subheader("📝 Recent Attendance")
    
    recent = attendance.head(10)
    if not recent.empty:
        for _, row in recent.iterrows():
            role_icon = {
                'attendee': '👤',
                'chaired': '🎤',
                'speaker': '📢',
                'treasurer': '💰'
            }.get(row['role'], '👤')
            st.write(f"{role_icon} {row['date']} - **{row['meeting_name']}** ({row['role']})")
    else:
        st.info("No attendance records yet")

# Page: Meetings
elif page == "📅 Meetings":
    st.title("📅 Meetings")
    
    # Add new meeting
    with st.expander("➕ Add New Meeting"):
        with st.form("add_meeting_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Meeting Name", placeholder="e.g., Stanhope Big Book")
                day_of_week = st.selectbox("Day of Week", list(range(7)), format_func=lambda x: DAY_NAMES[x])
                time_val = st.text_input("Time", value="7:00 PM", placeholder="7:00 PM")
            with col2:
                location = st.text_input("Location", placeholder="Big Stone Church")
                format_type = st.selectbox("Format", ["Big Book", "Open", "Closed", "Step", "Speaker", "Discussion"])
                is_treasurer_duty = st.checkbox("Treasurer Duty Required")
            
            notes = st.text_area("Notes (optional)")
            
            submitted = st.form_submit_button("Add Meeting", width='stretch')
            
            if submitted:
                if name and time_val and location:
                    add_meeting(name, day_of_week, time_val, location, format_type, is_treasurer_duty, notes)
                    st.success(f"Meeting '{name}' added!")
                    st.rerun()
                else:
                    st.error("Please fill in required fields")
    
    # Display meetings
    meetings = get_meetings(active_only=False)
    
    if not meetings.empty:
        st.subheader("All Meetings")
        
        for _, m in meetings.iterrows():
            status = "✅ Active" if m['is_active'] else "⏸️ Inactive"
            color = "green" if m['is_active'] else "gray"
            treasurer = " | 💰 Treasurer Duty" if m['is_treasurer_duty'] else ""
            
            with st.expander(f"{m['name']} - {DAY_NAMES[m['day_of_week']]} at {m['time']} ({status})"):
                # Edit form
                with st.form(f"edit_meeting_{m['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Name", value=m['name'], key=f"name_{m['id']}")
                        edit_day = st.selectbox("Day", list(range(7)), index=m['day_of_week'], format_func=lambda x: DAY_NAMES[x], key=f"day_{m['id']}")
                        edit_time = st.text_input("Time", value=m['time'], key=f"time_{m['id']}")
                        edit_location = st.text_input("Location", value=m['location'] or "", key=f"loc_{m['id']}")
                    with col2:
                        edit_format = st.selectbox("Format", ["Big Book", "Open", "Closed", "Step", "Speaker", "Discussion"], 
                                                  index=["Big Book", "Open", "Closed", "Step", "Speaker", "Discussion"].index(m['format_type']) if m['format_type'] in ["Big Book", "Open", "Closed", "Step", "Speaker", "Discussion"] else 0,
                                                  key=f"fmt_{m['id']}")
                        edit_treasurer = st.checkbox("Treasurer Duty", value=bool(m['is_treasurer_duty']), key=f"treas_{m['id']}")
                        edit_active = st.checkbox("Active", value=bool(m['is_active']), key=f"act_{m['id']}")
                    
                    edit_notes = st.text_area("Notes", value=m['notes'] or "", key=f"notes_{m['id']}")
                    
                    save_btn = st.form_submit_button("💾 Save Changes", width='stretch')
                    
                    if save_btn:
                        update_meeting(m['id'], edit_name, edit_day, edit_time, edit_location, edit_format, edit_treasurer, edit_notes, edit_active)
                        st.success("Meeting updated!")
                        st.rerun()
                
                # Delete button OUTSIDE the form
                if st.button("🗑️ Delete Meeting", key=f"del_meeting_{m['id']}"):
                    delete_meeting(m['id'])
                    st.success("Meeting deleted!")
                    st.rerun()
    else:
        st.info("No meetings yet. Add one above!")

# Page: Check In
elif page == "✅ Check In":
    st.title("✅ Check In")
    
    meetings = get_meetings()
    
    if not meetings.empty:
        with st.form("check_in_form"):
            col1, col2 = st.columns(2)
            with col1:
                meeting_id = st.selectbox("Select Meeting", meetings['id'], 
                                          format_func=lambda x: f"{meetings[meetings['id']==x]['name'].values[0]} - {DAY_NAMES[meetings[meetings['id']==x]['day_of_week'].values[0]]} {meetings[meetings['id']==x]['time'].values[0]}")
                date_val = st.date_input("Date", today)
            with col2:
                role = st.selectbox("Role", ["attendee", "chaired", "speaker", "treasurer"],
                                    format_func=lambda x: {"attendee": "👤 Attendee", "chaired": "🎤 Chaired", "speaker": "📢 Speaker", "treasurer": "💰 Treasurer"}[x])
            
            notes = st.text_area("Notes (optional)")
            
            submitted = st.form_submit_button("✅ Check In", width='stretch')
            
            if submitted:
                add_attendance(meeting_id, date_val, role, notes)
                st.success(f"Checked in to {meetings[meetings['id']==meeting_id]['name'].values[0]}!")
                st.rerun()
    else:
        st.info("No active meetings. Add one in the Meetings tab first!")

# Page: History
elif page == "📜 History":
    st.title("📜 Attendance History")
    
    attendance = get_attendance(500)
    
    if not attendance.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            meeting_filter = st.selectbox("Filter by meeting", ["all"] + list(attendance['meeting_name'].unique()))
        with col2:
            month_filter = st.selectbox("Filter by month", ["all"] + [d.strftime('%Y-%m') for d in pd.date_range(end=today, periods=12, freq='MS')[::-1]])
        
        if meeting_filter != "all":
            attendance = attendance[attendance['meeting_name'] == meeting_filter]
        
        if month_filter != "all":
            attendance = attendance[attendance['date'].str.startswith(month_filter)]
        
        # Stats
        total_records = len(attendance)
        unique_meetings = attendance['meeting_name'].nunique()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Records", total_records)
        with col2:
            st.metric("Unique Meetings", unique_meetings)
        
        st.markdown("---")
        
        # Display
        for _, row in attendance.iterrows():
            role_icon = {
                'attendee': '👤',
                'chaired': '🎤',
                'speaker': '📢',
                'treasurer': '💰'
            }.get(row['role'], '👤')
            
            with st.expander(f"{role_icon} {row['date']} - **{row['meeting_name']}** ({row['role']})"):
                st.write(f"**Meeting:** {row['meeting_name']}")
                st.write(f"**Date:** {row['date']}")
                st.write(f"**Role:** {row['role']}")
                st.write(f"**Location:** {row['location']}")
                if row['notes']:
                    st.write(f"**Notes:** {row['notes']}")
    else:
        st.info("No attendance records yet. Check in to get started!")

# Page: Treasury
elif page == "💰 Treasury":
    st.title("💰 Treasury")
    
    # Quick Add transaction
    with st.expander("⚡ Quick Add Transaction", expanded=True):
        with st.form("quick_treasury_form"):
            col1, col2, col3 = st.columns([2, 2, 1], gap="small")
            
            with col1:
                tx_type = st.selectbox("Type", ["income", "expense"], 
                                        format_func=lambda x: "💵 Income" if x == "income" else "💸 Expense")
                categories = get_categories(tx_type)
                category = st.selectbox("Category", categories['id'], 
                                       format_func=lambda x: categories[categories['id']==x]['name'].values[0])
            with col2:
                amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
                date_val = st.date_input("Date", today)
            with col3:
                description = st.text_input("Description", placeholder="What for?")
                meeting_name = st.text_input("Meeting Name (optional)")
            
            notes = st.text_area("Notes (optional)", key="treasury_notes")
            
            submit_btn = st.form_submit_button("➕ Add Transaction", width='stretch')
            
            if submit_btn:
                if amount > 0:
                    add_transaction(date_val, amount, category, tx_type, description, meeting_name, notes)
                    st.success(f"Added: {tx_type} - ${amount:,.2f}")
                    st.rerun()
                else:
                    st.error("Please enter an amount")
    
    # Balance summary
    balance = get_treasury_balance()
    summary = get_monthly_summary(current_year, current_month)
    income = summary['total_income'].iloc[0] or 0
    expense = summary['total_expense'].iloc[0] or 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💵 Monthly Income", f"${income:,.2f}")
    with col2:
        st.metric("💸 Monthly Expenses", f"${expense:,.2f}")
    with col3:
        st.metric("💰 Total Balance", f"${balance:,.2f}", delta=balance)
    
    # Transactions list
    st.markdown("---")
    st.subheader("📋 Recent Transactions")
    
    transactions = get_transactions(50)
    
    if not transactions.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            type_filter = st.selectbox("Filter by type", ["all", "income", "expense"])
        with col2:
            month_filter = st.selectbox("Filter by month", ["all"] + [d.strftime('%Y-%m') for d in pd.date_range(end=today, periods=12, freq='MS')[::-1]])
        
        if type_filter != "all":
            transactions = transactions[transactions['type'] == type_filter]
        
        if month_filter != "all":
            transactions = transactions[transactions['date'].str.startswith(month_filter)]
        
        for _, row in transactions.iterrows():
            icon = "💵" if row['type'] == 'income' else "💸"
            color = "#4ade80" if row['type'] == 'income' else "#f87171"
            
            with st.expander(f"{icon} {row['date']} - ${row['amount']:,.2f} ({row['type']})"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Amount:** ${row['amount']:,.2f}")
                    st.write(f"**Type:** {row['type']}")
                    if row['category']:
                        st.write(f"**Category:** {row['category']}")
                    if row['description']:
                        st.write(f"**Description:** {row['description']}")
                    if row['meeting_name']:
                        st.write(f"**Meeting:** {row['meeting_name']}")
                    if row['notes']:
                        st.write(f"**Notes:** {row['notes']}")
                with col2:
                    # Delete confirmation
                    confirm_key = f"confirm_tx_{row['id']}"
                    if confirm_key not in st.session_state:
                        st.session_state[confirm_key] = False
                    
                    if not st.session_state[confirm_key]:
                        if st.button("🗑️ Delete", key=f"del_tx_{row['id']}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        st.warning("Confirm?")
                        col_confirm1, col_confirm2 = st.columns(2)
                        with col_confirm1:
                            if st.button("✅ Yes", key=f"yes_tx_{row['id']}"):
                                delete_transaction(row['id'])
                                st.session_state[confirm_key] = False
                                st.rerun()
                        with col_confirm2:
                            if st.button("❌ No", key=f"no_tx_{row['id']}"):
                                st.session_state[confirm_key] = False
                                st.rerun()
    else:
        st.info("No transactions yet. Add one above!")
    
    # Add category
    st.markdown("---")
    with st.expander("➕ Add Category"):
        with st.form("add_category_form"):
            col1, col2 = st.columns(2)
            with col1:
                cat_name = st.text_input("Category Name", placeholder="e.g., 7th Tradition")
                cat_type = st.selectbox("Type", ["income", "expense"])
            with col2:
                cat_desc = st.text_input("Description", placeholder="What is this for?")
            
            if st.form_submit_button("Add Category"):
                if cat_name:
                    add_category(cat_name, cat_type, cat_desc)
                    st.success(f"Category '{cat_name}' added!")
                    st.rerun()
                else:
                    st.error("Please enter a category name")

# Footer
st.markdown("---")
st.markdown(f"🍀 AA Tracker | 📅 {today.strftime('%B %d, %Y')}")
