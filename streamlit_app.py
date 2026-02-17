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
            <div class="login-icon">🍀</div>
            <h2 style="border:none; margin-bottom:0.5rem;">AA TRACKER</h2>
            <p style="color:var(--text-muted); margin-bottom:2rem; text-transform:uppercase; font-size:0.8rem; letter-spacing:0.2em;">One day at a time</p>
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

# Custom CSS - Brutalist Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Archivo+Black&display=swap');
    
    :root {
        --bg-dark: #0a0a0a;
        --bg-card: #141414;
        --text: #f0f0f0;
        --text-muted: #666;
        --accent: #ff3e00;
        --accent-hover: #ff6b3d;
        --border: #333;
        --border-light: #444;
    }
    
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text);
        font-family: 'Space Mono', monospace;
        min-height: 100vh;
    }
    
    h1, h2, h3 {
        font-family: 'Archivo Black', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text);
    }
    
    h1 { 
        font-size: 3rem; 
        line-height: 1;
        border: 4px solid var(--text);
        padding: 1rem;
        margin-bottom: 2rem;
    }
    
    h2 { 
        font-size: 1.5rem; 
        border-left: 8px solid var(--accent);
        padding-left: 1rem;
        margin-bottom: 1.5rem;
    }
    
    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 2px solid var(--border);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: var(--accent);
    }
    
    div[data-testid="stMetricValue"] { 
        font-family: 'Archivo Black', sans-serif;
        font-size: 2.5rem; 
        text-transform: uppercase;
    }
    
    div[data-testid="stMetricLabel"] { 
        color: var(--accent);
        font-size: 0.75rem; 
        letter-spacing: 0.2em;
    }
    
    .stButton > button {
        background: var(--accent);
        color: #000;
        border: none;
        border-radius: 0;
        padding: 1rem 2rem;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        transition: all 0.1s;
    }
    
    .stButton > button:hover {
        background: var(--accent-hover);
        transform: translate(4px, 4px);
    }
    
    .stButton > button[kind="secondary"] {
        background: transparent;
        color: var(--text);
        border: 2px solid var(--border-light);
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--accent);
        color: var(--accent);
    }
    
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
        border: 4px solid var(--text);
        padding: 3rem;
        max-width: 400px;
        width: 90%;
    }
    
    .login-icon {
        font-size: 5rem;
        display: block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Supabase configuration
SUPABASE_URL = "https://qlkfubzlvgngbhnlecbk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsa2Z1YnpsdmduZ2JobmxlY2JrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzNjU1OTksImV4cCI6MjA4Njk0MTU5OX0.M_Yi7hCCKtRLAO-11qr60FbhXK6JkXMPzRyLw5_xKAY"

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
    try:
        supabase.table('attendance').insert({
            'meeting_id': meeting_id,
            'date': date_val.strftime('%Y-%m-%d') if hasattr(date_val, 'strftime') else str(date_val),
            'role': role,
            'notes': notes
        }).execute()
        clear_cache()
    except Exception as e:
        st.error(f"Failed to record attendance: {e}")

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

st.markdown('<h1>🍀 AA TRACKER</h1>', unsafe_allow_html=True)

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
