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

APP_PASSWORD = st.secrets.get("APP_PASSWORD", "nick123")

def check_password():
    """Show login screen if not authenticated"""
    if st.session_state.authenticated:
        return True
    
    st.markdown("""
    <style>
        .login-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
        }
        .login-card {
            background: var(--bg-card);
            border: 4px solid var(--text);
            padding: 3rem;
            text-align: center;
            max-width: 380px;
            width: 90%;
        }
        .login-icon {
            font-size: 5rem;
            display: block;
            margin-bottom: 1rem;
        }
    </style>
    <div class="login-wrapper">
        <div class="login-card">
            <div class="login-icon">▣</div>
            <h2 style="border:none; margin-bottom:0.5rem; font-family: 'JetBrains Mono', monospace;">> AA_TRACKER</h2>
            <p style="color:var(--text-muted); margin-bottom:2rem; text-transform:uppercase; font-size:0.7rem; letter-spacing:0.25em;">// one day at a time</p>
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

# Custom CSS - Industrial / Terminal Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    :root {
        --bg-dark: #0d0d0d;
        --bg-card: #161616;
        --bg-input: #1a1a1a;
        --text: #e8e8e8;
        --text-dim: #888888;
        --text-muted: #555555;
        --accent: #00ff88;
        --accent-dim: #00cc6a;
        --accent-glow: rgba(0, 255, 136, 0.15);
        --border: #2a2a2a;
        --border-light: #3a3a3a;
        --terminal-amber: #ffb000;
        --terminal-red: #ff3333;
    }
    
    /* Scanline effect overlay */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 0, 0, 0.03) 2px,
            rgba(0, 0, 0, 0.03) 4px
        );
        pointer-events: none;
        z-index: 9999;
    }
    
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text);
        font-family: 'IBM Plex Mono', monospace;
        min-height: 100vh;
    }
    
    /* Text selection */
    ::selection {
        background: var(--accent);
        color: var(--bg-dark);
    }
    
    h1, h2, h3, h4 {
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: var(--text);
        font-weight: 700;
    }
    
    h1 { 
        font-size: 2.5rem; 
        line-height: 1.2;
        border: 3px solid var(--text);
        padding: 1.25rem 1.5rem;
        margin-bottom: 2rem;
        position: relative;
        background: var(--bg-card);
    }
    
    h1::before {
        content: "> ";
        color: var(--accent);
    }
    
    h1::after {
        content: "_";
        animation: blink 1s step-end infinite;
    }
    
    @keyframes blink {
        50% { opacity: 0; }
    }
    
    h2 { 
        font-size: 1.25rem; 
        border-left: 4px solid var(--accent);
        padding-left: 1rem;
        margin-bottom: 1.5rem;
        background: var(--bg-card);
        padding: 0.75rem 1rem;
    }
    
    h3 {
        font-size: 1rem;
        border-bottom: 1px solid var(--border-light);
        padding-bottom: 0.5rem;
    }
    
    /* Metrics - terminal style */
    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        padding: 1.25rem;
        margin-bottom: 1rem;
        position: relative;
    }
    
    div[data-testid="stMetric"]::before {
        content: "[";
        position: absolute;
        top: 0.5rem;
        left: 0.5rem;
        color: var(--border-light);
        font-family: 'JetBrains Mono', monospace;
    }
    
    div[data-testid="stMetric"]::after {
        content: "]";
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        color: var(--border-light);
        font-family: 'JetBrains Mono', monospace;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: var(--accent);
        box-shadow: 0 0 20px var(--accent-glow);
    }
    
    div[data-testid="stMetricValue"] { 
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem; 
        font-weight: 700;
        color: var(--accent);
        text-shadow: 0 0 10px var(--accent-glow);
    }
    
    div[data-testid="stMetricLabel"] { 
        color: var(--text-dim);
        font-size: 0.7rem; 
        letter-spacing: 0.25em;
        text-transform: uppercase;
    }
    
    /* Buttons - terminal style */
    .stButton > button {
        background: transparent;
        color: var(--accent);
        border: 2px solid var(--accent);
        border-radius: 0;
        padding: 0.75rem 1.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        transition: all 0.15s ease;
        position: relative;
    }
    
    .stButton > button:hover {
        background: var(--accent);
        color: var(--bg-dark);
        box-shadow: 0 0 20px var(--accent-glow);
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    .stButton > button[kind="secondary"] {
        background: transparent;
        color: var(--text-dim);
        border: 1px solid var(--border-light);
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--text);
        color: var(--text);
    }
    
    /* Input fields */
    .stTextInput > div > div, .stNumberInput > div > div, 
    .stSelectbox > div > div, .stDateInput > div > div {
        background: var(--bg-card);
        border: 2px solid var(--border);
        border-radius: 0;
        color: var(--text);
    }
    
    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within {
        border-color: var(--accent);
    }
    
    .stRadio > div > label {
        background: var(--bg-card);
        border: 2px solid var(--border);
        border-radius: 0;
        padding: 0.75rem 1.25rem;
        color: var(--text-muted);
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.1em;
    }
    
    .stRadio > div > label:hover {
        border-color: var(--border-light);
        color: var(--text);
    }
    
    .stRadio > div > label:has(input:checked) {
        background: var(--accent);
        color: #000;
        border-color: var(--accent);
        font-weight: 700;
    }
    
    .streamlit-expanderHeader {
        background: var(--bg-card);
        border: 2px solid var(--border);
        border-radius: 0;
        color: var(--text);
        font-family: 'Space Mono', monospace;
        text-transform: uppercase;
    }
    
    .stDataFrame {
        background: var(--bg-card);
        border: 2px solid var(--border);
        border-radius: 0;
    }
    
    hr { 
        border: none; 
        height: 4px; 
        background: var(--accent); 
        margin: 2rem 0; 
    }
    
    .stSuccess, .stError {
        border-radius: 0;
        border: 2px solid;
    }
    
    .stSuccess { 
        background: transparent; 
        border-color: var(--accent);
        color: var(--accent);
    }
    
    .stError { 
        background: transparent; 
        border-color: #ff0000;
        color: #ff0000;
    }
    
    @media (max-width: 768px) {
        h1 { font-size: 1.75rem; padding: 0.5rem; }
        h2 { font-size: 1.25rem; }
        div[data-testid="stMetricValue"] { font-size: 1.5rem; }
        .stRadio > div { flex-direction: column !important; }
    }
    
    /* Login page */
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
    }
    
    .login-card {
        background: var(--bg-card);
        border: 3px solid var(--accent);
        padding: 3rem;
        max-width: 400px;
        width: 90%;
        position: relative;
    }
    
    .login-card::before {
        content: "/// AUTHENTICATE";
        position: absolute;
        top: -12px;
        left: 1rem;
        background: var(--bg-dark);
        color: var(--accent);
        padding: 0 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.2em;
    }
    
    .login-icon {
        font-size: 4rem;
        display: block;
        margin-bottom: 1rem;
        filter: grayscale(100%) brightness(1.5);
    }
    
    /* Tables / DataFrames */
    .stDataFrame {
        background: var(--bg-card);
        border: 1px solid var(--border);
    }
    
    .stDataFrame thead th {
        background: var(--bg-input) !important;
        color: var(--accent) !important;
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.15em;
        border-bottom: 2px solid var(--accent) !important;
    }
    
    .stDataFrame tbody td {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background: var(--accent-glow) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: var(--bg-card);
        border-right: 1px solid var(--border);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-bottom: none;
        color: var(--text-dim);
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.15em;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent) !important;
        color: var(--bg-dark) !important;
        border-color: var(--accent) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-light);
        border: 1px solid var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-dim);
    }
    
    /* Cursor blink animation for headings */
    @keyframes cursor-blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

# Supabase configuration
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def get_supabase_client():
    """Create Supabase client"""
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

def clear_cache():
    """Clear all cached data after modifications"""
    get_meetings.clear()
    get_attendance.clear()
    get_categories.clear()
    get_transactions.clear()
    get_treasury_balance.clear()
    get_monthly_summary.clear()

# Helper functions using Supabase
@st.cache_data(ttl=60)
def get_meetings(active_only=True):
    """Get meetings from Supabase"""
    try:
        query = supabase.table('meeting').select('*')
        if active_only:
            query = query.eq('is_active', True)
        result = query.order('day_of_week').order('time').execute()
        return pd.DataFrame(result.data) if result.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load meetings: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_attendance(limit=200):
    """Get attendance records from Supabase"""
    try:
        result = supabase.table('attendance').select('id, date, role, notes, meeting_id').order('date', desc=True).limit(limit).execute()
        df = pd.DataFrame(result.data) if result.data else pd.DataFrame()
        if not df.empty:
            # Get meeting info
            meetings = get_meetings(active_only=False)
            df = df.merge(meetings[['id', 'name', 'day_of_week', 'time', 'location']], left_on='meeting_id', right_on='id', how='left', suffixes=('', '_m'))
            df = df.rename(columns={'name': 'meeting_name'})
        return df
    except Exception as e:
        st.error(f"Failed to load attendance: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_categories(category_type=None):
    """Get categories from Supabase"""
    try:
        query = supabase.table('category').select('*')
        if category_type:
            query = query.eq('type', category_type)
        result = query.eq('is_active', True).execute()
        return pd.DataFrame(result.data) if result.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load categories: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_transactions(limit=100):
    """Get treasury transactions from Supabase"""
    try:
        result = supabase.table('transaction').select('*').order('date', desc=True).order('id', desc=True).limit(limit).execute()
        df = pd.DataFrame(result.data) if result.data else pd.DataFrame()
        if not df.empty:
            # Get category info
            cats = get_categories()
            df = df.merge(cats[['id', 'name', 'type']], left_on='category_id', right_on='id', how='left', suffixes=('', '_cat'))
            df = df.rename(columns={'name': 'category_name', 'type_cat': 'cat_type'})
        return df
    except Exception as e:
        st.error(f"Failed to load transactions: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_treasury_balance():
    """Calculate total treasury balance from Supabase"""
    try:
        result = supabase.table('transaction').select('type, amount').execute()
        df = pd.DataFrame(result.data) if result.data else pd.DataFrame()
        if df.empty:
            return 0
        income = df[df['type'] == 'income']['amount'].sum() or 0
        expense = df[df['type'] == 'expense']['amount'].sum() or 0
        return income - expense
    except Exception as e:
        st.error(f"Failed to load balance: {e}")
        return 0

@st.cache_data(ttl=60)
def get_monthly_summary(year=None, month=None):
    """Get monthly income/expense summary from Supabase"""
    try:
        query = supabase.table('transaction').select('type, amount, date')
        if year and month:
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year+1}-01-01"
            else:
                end_date = f"{year}-{month+1:02d}-01"
            query = query.gte('date', start_date).lt('date', end_date)
        result = query.execute()
        df = pd.DataFrame(result.data) if result.data else pd.DataFrame()
        if df.empty:
            return pd.DataFrame([{'total_income': 0, 'total_expense': 0}])
        income = df[df['type'] == 'income']['amount'].sum() or 0
        expense = df[df['type'] == 'expense']['amount'].sum() or 0
        return pd.DataFrame([{'total_income': income, 'total_expense': expense}])
    except Exception as e:
        st.error(f"Failed to load summary: {e}")
        return pd.DataFrame([{'total_income': 0, 'total_expense': 0}])

# Database operations
def add_meeting(name, day_of_week, time, location, format_type, is_treasurer_duty, notes):
    """Add a new meeting to Supabase"""
    try:
        supabase.table('meeting').insert({
            'name': name,
            'day_of_week': day_of_week,
            'time': time,
            'location': location,
            'format_type': format_type,
            'is_treasurer_duty': is_treasurer_duty,
            'notes': notes
        }).execute()
        clear_cache()
    except Exception as e:
        st.error(f"Failed to add meeting: {e}")

def update_meeting(meeting_id, name, day_of_week, time, location, format_type, is_treasurer_duty, notes, is_active):
    """Update a meeting in Supabase"""
    try:
        supabase.table('meeting').update({
            'name': name,
            'day_of_week': day_of_week,
            'time': time,
            'location': location,
            'format_type': format_type,
            'is_treasurer_duty': is_treasurer_duty,
            'notes': notes,
            'is_active': is_active
        }).eq('id', meeting_id).execute()
        clear_cache()
    except Exception as e:
        st.error(f"Failed to update meeting: {e}")

def delete_meeting(meeting_id):
    """Delete (deactivate) a meeting"""
    try:
        supabase.table('meeting').update({'is_active': False}).eq('id', meeting_id).execute()
        clear_cache()
    except Exception as e:
        st.error(f"Failed to delete meeting: {e}")

def add_attendance(meeting_id, date_val, role, notes):
    """Record attendance in Supabase"""
    from datetime import date as date_type
    
    # Validate date is not in the future
    check_date = date_val if isinstance(date_val, date_type) else date_type.fromisoformat(str(date_val))
    if check_date > today:
        st.error("Cannot check in for future dates")
        return False
    
    # Check for duplicate
    date_str = check_date.strftime('%Y-%m-%d') if hasattr(check_date, 'strftime') else str(check_date)
    existing = supabase.table('attendance').select('id').eq('meeting_id', meeting_id).eq('date', date_str).execute()
    if existing.data:
        st.error("Already checked in for this meeting on this date!")
        return False
    
    try:
        supabase.table('attendance').insert({
            'meeting_id': meeting_id,
            'date': date_str,
            'role': role,
            'notes': notes
        }).execute()
        clear_cache()
        return True
    except Exception as e:
        st.error(f"Failed to record attendance: {e}")
        return False

def add_transaction(date_val, amount, category_id, tx_type, description, meeting_name, notes):
    """Add treasury transaction to Supabase"""
    try:
        supabase.table('transaction').insert({
            'date': date_val.strftime('%Y-%m-%d') if hasattr(date_val, 'strftime') else str(date_val),
            'amount': amount,
            'category_id': category_id,
            'type': tx_type,
            'description': description,
            'meeting_name': meeting_name,
            'notes': notes
        }).execute()
        clear_cache()
    except Exception as e:
        st.error(f"Failed to add transaction: {e}")

def delete_transaction(tx_id):
    """Delete a transaction"""
    try:
        supabase.table('transaction').delete().eq('id', tx_id).execute()
        clear_cache()
    except Exception as e:
        st.error(f"Failed to delete transaction: {e}")

def add_category(name, cat_type, description):
    """Add a new category"""
    try:
        supabase.table('category').insert({
            'name': name,
            'type': cat_type,
            'description': description
        }).execute()
        clear_cache()
    except Exception as e:
        st.error(f"Failed to add category: {e}")

# Navigation
pages = ["📊 Dashboard", "📅 Meetings", "✅ Check In", "📜 History", "💰 Treasury"]

st.markdown('<h1>AA_TRACKER_v2.0</h1>', unsafe_allow_html=True)

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
    
    # Meetings attended this week
    week_start = today - timedelta(days=today.weekday())
    this_week_attendance = attendance[pd.to_datetime(attendance['date']).dt.date >= week_start]
    meetings_this_week = len(this_week_attendance)
    
    # Total check-ins (all time)
    total_checkins = len(attendance)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Attendance Streak", f"{streak} days")
    with col2:
        st.metric("💰 Treasury Balance", f"${balance:,.2f}")
    with col3:
        st.metric("📅 Attended This Week", meetings_this_week)
    
    # Secondary metrics
    st.metric("✓ Total Check-ins", total_checkins)
    
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
                if add_attendance(meeting_id, date_val, role, notes):
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
