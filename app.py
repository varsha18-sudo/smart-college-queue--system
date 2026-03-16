"""
QuickQ College Queue Token Management System
Single file Streamlit application - Fixed 80 student limit
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
import time

# ------------------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="QuickQ · College Token System",
    page_icon="🎟️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------------------------
# Initialize session state
# ------------------------------------------------------------------------------
def initialize_session_state():
    """Initialize all session state variables"""
    
    # Departments - Added Submission
    if 'departments' not in st.session_state:
        st.session_state.departments = ['Student Section', 'Accounts Section', 'Bus Line', 'Canteen', 'Submission']
    
    # Subjects for Submission department
    if 'submission_subjects' not in st.session_state:
        st.session_state.submission_subjects = ['DBMS', 'OS', 'CT', 'IOT', 'DT', 'OE']
    
    # Queue state for each department - Start with 0 issued tokens
    if 'queue_state' not in st.session_state:
        st.session_state.queue_state = {}
        for dept in st.session_state.departments:
            st.session_state.queue_state[dept] = {
                'current': 1,        # start serving from token 1
                'last': 0,            # start with 0 issued tokens
                'paused': False,
                'avg_wait_min': 2,
                'total_issued': 0      # track total tokens issued
            }
    
    # Time slots
    if 'time_slots' not in st.session_state:
        st.session_state.time_slots = {
            'Slot 1': '8:30 AM - 10:30 AM',
            'Slot 2': '11:00 AM - 1:00 PM',
            'Slot 3': '2:00 PM - 4:30 PM'
        }
    
    # Student data
    if 'students' not in st.session_state:
        st.session_state.students = {}
    
    # Add some sample students
    st.session_state.students['S001'] = {'name': 'Alex Johnson', 'password': 'pass123', 'dept': None, 'token': None, 'slot': None, 'subject': None, 'history': []}
    st.session_state.students['S002'] = {'name': 'Maria Garcia', 'password': 'pass123', 'dept': None, 'token': None, 'slot': None, 'subject': None, 'history': []}
    st.session_state.students['S003'] = {'name': 'Kim Lee', 'password': 'pass123', 'dept': None, 'token': None, 'slot': None, 'subject': None, 'history': []}
    
    # Token history
    if 'token_history' not in st.session_state:
        st.session_state.token_history = []
    
    # Admin credentials
    if 'admins' not in st.session_state:
        st.session_state.admins = {}
    
    # Navigation state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'selected_dept' not in st.session_state:
        st.session_state.selected_dept = None
    if 'selected_subject' not in st.session_state:
        st.session_state.selected_subject = None

# Call initialization
initialize_session_state()

# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------
def get_next_token(dept):
    """Generate next token for department - Limited to 80 students"""
    state = st.session_state.queue_state[dept]
    
    # Check if maximum capacity reached (80 students)
    if state['total_issued'] >= 80:
        st.error("⚠️ Maximum capacity of 80 students reached! No more tokens can be issued.")
        return None
    
    # Increment last token number and total issued
    state['last'] += 1
    state['total_issued'] += 1
    new_token = state['last']
    
    # Record in history
    history_entry = {
        'token': new_token,
        'department': dept,
        'issued_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'issued'
    }
    st.session_state.token_history.append(history_entry)
    
    return new_token

def people_ahead(dept, token):
    """Calculate number of people ahead"""
    state = st.session_state.queue_state.get(dept)
    if not state or token is None:
        return 0
    if token <= state['current']:
        return 0
    return token - state['current'] - 1

def waiting_time(dept, token):
    """Estimate waiting time"""
    ahead = people_ahead(dept, token)
    avg = st.session_state.queue_state.get(dept, {}).get('avg_wait_min', 2)
    return ahead * avg

def logout():
    """Handle logout"""
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.user_id = None
    st.session_state.page = 'home'
    st.rerun()

# ------------------------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(145deg, #f0f5fe 0%, #e9f0fa 100%);
    }
    
    h1, h2, h3 {
        color: #0a1e3c !important;
        font-weight: 700 !important;
    }
    
    .custom-card {
        background: white;
        border-radius: 2.5rem;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 12px 30px -8px rgba(25, 60, 120, 0.15);
        margin: 1rem 0;
    }
    
    .portal-icon {
        background: #dbeafe;
        width: 80px;
        height: 80px;
        border-radius: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2.2rem;
        color: #2563eb;
    }
    
    .token-badge {
        background: #2563eb;
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        padding: 0.5rem 2rem;
        border-radius: 4rem;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .token-badge-small {
        background: #1e293b;
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        padding: 0.3rem 1.5rem;
        border-radius: 3rem;
        display: inline-block;
    }
    
    .stat-item {
        background: #f8fafc;
        border-radius: 1.5rem;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid #2563eb;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        color: #475569;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    /* Admin bar with better visibility */
    .admin-bar {
        background: #1e293b;
        border-radius: 2rem;
        padding: 1.5rem 2rem;
        display: flex;
        justify-content: space-between;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border: 2px solid #2563eb;
    }
    
    .admin-bar .stat-label {
        color: #93c5fd;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .admin-bar .big-number {
        font-size: 2.8rem;
        font-weight: 800;
        color: white;
        line-height: 1.2;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Admin status card */
    .admin-status-card {
        background: white;
        padding: 2rem;
        border-radius: 2rem;
        margin-top: 1.5rem;
        border: 2px solid #2563eb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .admin-status-card p {
        font-size: 1.2rem;
        margin: 0.8rem 0;
        color: #0a1e3c;
        font-weight: 500;
    }
    
    .admin-status-card strong {
        color: #2563eb;
        font-weight: 700;
        font-size: 1.3rem;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 2rem;
        font-weight: 700;
        font-size: 1.2rem;
        margin-left: 1rem;
    }
    
    .status-running {
        background: #10b981;
        color: white;
    }
    
    .status-paused {
        background: #f59e0b;
        color: white;
    }
    
    /* Token History Section - White background, RED text */
    .token-history-container {
        background: linear-gradient(145deg, #fff5f5, #fee2e2);
        border: 3px solid #dc2626;
        border-radius: 2rem;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 10px 25px -5px rgba(220, 38, 38, 0.3);
    }
    
    .token-history-header {
        background: #dc2626;
        color: white;
        padding: 1rem 2rem;
        border-radius: 3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.5rem;
        font-weight: 700;
        font-size: 1.5rem;
        border: 2px solid #991b1b;
    }
    
    .token-history-item {
        background: white;
        border-left: 6px solid #dc2626;
        border-radius: 1rem;
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.2);
    }
    
    .token-history-item strong {
        color: #dc2626;
        font-size: 1.2rem;
        background: #fee2e2;
        padding: 0.2rem 1rem;
        border-radius: 2rem;
        margin-right: 1rem;
    }
    
    .token-history-stats {
        background: #991b1b;
        color: white;
        padding: 1.2rem;
        border-radius: 1.5rem;
        margin: 1.5rem 0;
        display: flex;
        justify-content: space-around;
    }
    
    .token-history-stats .number {
        font-size: 2rem;
        font-weight: 800;
        display: block;
    }
    
    .token-history-stats .label {
        color: #fecaca;
        font-size: 0.9rem;
        text-transform: uppercase;
    }
    
    /* Token History Expander - White background, RED text */
    div[data-testid="stExpander"] {
        border: 2px solid #e5e7eb !important;
        border-radius: 1rem !important;
        background: #ffffff !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    div[data-testid="stExpander"] > details > summary {
        background: #ffffff !important;
        color: #dc2626 !important;
        font-weight: 800 !important;
        font-size: 1.5rem !important;
        border-radius: 1rem 1rem 0 0 !important;
        padding: 1rem !important;
        border-bottom: 2px solid #f3f4f6 !important;
    }
    
    div[data-testid="stExpander"] > details > summary:hover {
        background: #f9fafb !important;
    }
    
    div[data-testid="stExpander"] > details > summary span {
        color: #dc2626 !important;
        font-weight: 800 !important;
    }
    
    div[data-testid="stExpander"] > details > div {
        background: #ffffff !important;
        padding: 1.5rem !important;
    }
    
    .slot-card {
        background: #1e293b;
        border: 2px solid #2563eb;
        border-radius: 1.5rem;
        padding: 1rem;
        text-align: center;
        font-weight: 700;
        color: white;
        margin: 0.5rem 0;
    }
    
    .slot-time {
        color: #93c5fd;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.3rem;
    }
    
    .capacity-full {
        background: #fee2e2;
        border: 2px solid #ef4444;
        color: #b91c1c;
        padding: 2rem;
        border-radius: 2rem;
        text-align: center;
        font-weight: 700;
        font-size: 1.5rem;
        margin: 2rem 0;
    }
    
    .token-counter {
        background: #0a1e3c;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        display: inline-block;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .red-badge {
        background: #dc2626;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 2rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Header
# ------------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("🏠 Home", use_container_width=True):
        if st.session_state.logged_in:
            logout()
        else:
            st.session_state.page = 'home'
            st.rerun()
with col2:
    st.markdown("<h2 style='text-align: center;'>🎟️ QuickQ · College</h2>", unsafe_allow_html=True)
with col3:
    if st.session_state.logged_in:
        st.markdown(f"<p style='text-align: right;'>👤 {st.session_state.user_id}</p>", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------------------------------------------
# Page routing
# ------------------------------------------------------------------------------
if not st.session_state.logged_in:
    # HOME PAGE
    if st.session_state.page == 'home':
        st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Welcome to QuickQ</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='custom-card'>
                <div class='portal-icon'>👨‍🎓</div>
                <h3>Student Portal</h3>
                <p>Get token, track queue</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Student Portal", key="student_home", use_container_width=True):
                st.session_state.page = 'student_login'
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class='custom-card'>
                <div class='portal-icon'>👩‍🏫</div>
                <h3>Admin Portal</h3>
                <p>Manage queues</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Admin Portal", key="admin_home", use_container_width=True):
                st.session_state.page = 'admin_login'
                st.rerun()
    
    # STUDENT LOGIN PAGE
    elif st.session_state.page == 'student_login':
        st.markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>🔐 Student Login</h1>", unsafe_allow_html=True)
        
        with st.form("student_login_form"):
            student_id = st.text_input("Student ID", placeholder="Enter ID (e.g., S001)")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            department = st.selectbox("Department", st.session_state.departments)
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted and student_id and password:
                st.session_state.logged_in = True
                st.session_state.user_type = 'student'
                st.session_state.user_id = student_id
                
                if student_id not in st.session_state.students:
                    st.session_state.students[student_id] = {
                        'name': f'Student {student_id}',
                        'password': password,
                        'dept': None,
                        'token': None,
                        'slot': None,
                        'subject': None,
                        'history': []
                    }
                
                st.session_state.selected_dept = department
                st.session_state.students[student_id]['dept'] = department
                st.session_state.students[student_id]['token'] = None
                st.session_state.students[student_id]['slot'] = None
                st.session_state.students[student_id]['subject'] = None
                st.session_state.page = 'student_dashboard'
                st.rerun()
            elif submitted:
                st.error("Please enter both ID and password")
        
        if st.button("← Back to Home"):
            st.session_state.page = 'home'
            st.rerun()
    
    # ADMIN LOGIN PAGE
    elif st.session_state.page == 'admin_login':
        st.markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>👩‍🏫 Faculty Admin Login</h1>", unsafe_allow_html=True)
        
        with st.form("admin_login_form"):
            admin_id = st.text_input("Faculty ID", placeholder="Enter your faculty ID")
            admin_password = st.text_input("Password", type="password", placeholder="Enter password")
            department = st.selectbox("Department", st.session_state.departments)
            
            submitted = st.form_submit_button("Access Dashboard", use_container_width=True)
            
            if submitted:
                if admin_id and admin_password.lower() == "faculty":
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'admin'
                    st.session_state.user_id = admin_id
                    st.session_state.selected_dept = department
                    
                    st.session_state.admins[admin_id] = {
                        'password': admin_password,
                        'dept': department
                    }
                    
                    st.session_state.page = 'admin_dashboard'
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        if st.button("← Back to Home"):
            st.session_state.page = 'home'
            st.rerun()

else:
    # STUDENT DASHBOARD
    if st.session_state.user_type == 'student':
        student_id = st.session_state.user_id
        student = st.session_state.students.get(student_id, {'name': f'Student {student_id}', 'history': []})
        dept = st.session_state.selected_dept
        q = st.session_state.queue_state[dept]
        my_token = student.get('token')
        my_slot = student.get('slot')
        my_subject = student.get('subject')
        ahead = people_ahead(dept, my_token) if my_token else 0
        wait = waiting_time(dept, my_token) if my_token else 0
        
        st.markdown(f"<h1>👋 Welcome, {student['name']}</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                logout()
        
        st.markdown(f"<h2>{dept}</h2>", unsafe_allow_html=True)
        
        # Show token counter
        tokens_left = 80 - q['total_issued']
        st.markdown(f"""
        <div class='token-counter'>
            🎟️ Tokens Available: {tokens_left}/80
        </div>
        """, unsafe_allow_html=True)
        
        # Current serving
        st.markdown("<p class='stat-label'>Current serving</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='token-badge'>{q['current']}</div>", unsafe_allow_html=True)
        
        # Check if maximum capacity reached
        if q['total_issued'] >= 80 and not my_token:
            st.markdown("""
            <div class='capacity-full'>
                🚫 SORRY!<br>
                Maximum capacity of 80 students reached.<br>
                No more tokens can be issued.
            </div>
            """, unsafe_allow_html=True)
        
        elif not my_token:
            # If Submission department, show subject selection first
            if dept == 'Submission' and not my_subject:
                st.markdown("<h3>Select Subject for Submission</h3>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                subjects = st.session_state.submission_subjects
                
                for i, subject in enumerate(subjects):
                    if i % 3 == 0:
                        with col1:
                            if st.button(f"📚 {subject}", key=f"subj_{subject}", use_container_width=True):
                                st.session_state.selected_subject = subject
                                st.session_state.students[student_id]['subject'] = subject
                                st.rerun()
                    elif i % 3 == 1:
                        with col2:
                            if st.button(f"📚 {subject}", key=f"subj_{subject}", use_container_width=True):
                                st.session_state.selected_subject = subject
                                st.session_state.students[student_id]['subject'] = subject
                                st.rerun()
                    else:
                        with col3:
                            if st.button(f"📚 {subject}", key=f"subj_{subject}", use_container_width=True):
                                st.session_state.selected_subject = subject
                                st.session_state.students[student_id]['subject'] = subject
                                st.rerun()
            
            # After subject is selected (or if not Submission), show time slots
            elif dept != 'Submission' or my_subject:
                if dept == 'Submission' and my_subject:
                    st.markdown(f"""
                    <div style='background: #0a1e3c; color: white; padding: 0.8rem; border-radius: 2rem; text-align: center; margin-bottom: 1rem;'>
                        📚 Selected Subject: <strong>{my_subject}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<h3>Select Time Slot</h3>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                selected_slot = None
                
                with col1:
                    st.markdown(f"""
                    <div class='slot-card'>
                        🕐 Slot 1
                        <div class='slot-time'>{st.session_state.time_slots['Slot 1']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Select Slot 1", key="slot1", use_container_width=True):
                        selected_slot = 'Slot 1'
                
                with col2:
                    st.markdown(f"""
                    <div class='slot-card'>
                        🕑 Slot 2
                        <div class='slot-time'>{st.session_state.time_slots['Slot 2']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Select Slot 2", key="slot2", use_container_width=True):
                        selected_slot = 'Slot 2'
                
                with col3:
                    st.markdown(f"""
                    <div class='slot-card'>
                        🕒 Slot 3
                        <div class='slot-time'>{st.session_state.time_slots['Slot 3']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Select Slot 3", key="slot3", use_container_width=True):
                        selected_slot = 'Slot 3'
                
                if selected_slot:
                    new_token = get_next_token(dept)
                    if new_token:
                        st.session_state.students[student_id]['token'] = new_token
                        st.session_state.students[student_id]['slot'] = selected_slot
                        
                        history_entry = {
                            'token': new_token,
                            'department': dept,
                            'slot': selected_slot,
                            'subject': my_subject if dept == 'Submission' else None,
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        if 'history' not in st.session_state.students[student_id]:
                            st.session_state.students[student_id]['history'] = []
                        st.session_state.students[student_id]['history'].append(history_entry)
                        
                        st.rerun()
        
        else:
            # Show token confirmation
            st.markdown(f"""
            <div style='text-align: center; margin: 1.5rem 0;'>
                <div style='background:#10b981; color:white; padding:1rem 2rem; border-radius:3rem; display:inline-block; font-weight:700; font-size:1.5rem;'>
                    ✅ YOUR TOKEN: #{my_token}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if dept == 'Submission' and my_subject:
                st.markdown(f"""
                <div style='background:#0a1e3c; color:white; padding:0.8rem; border-radius:2rem; text-align:center; margin-bottom:1rem;'>
                    📚 Subject: {my_subject}
                </div>
                """, unsafe_allow_html=True)
            
            if my_slot:
                st.markdown(f"""
                <div class='slot-card' style='margin-bottom:1rem;'>
                    📅 {st.session_state.time_slots[my_slot]}
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='stat-item'><div class='stat-label'>People ahead</div><div class='stat-value'>{ahead}</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='stat-item'><div class='stat-label'>Est. waiting</div><div class='stat-value'>{wait} min</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='stat-item'><div class='stat-label'>Total waiting</div><div class='stat-value'>{q['last'] - q['current']}</div></div>", unsafe_allow_html=True)
    
    # ADMIN DASHBOARD
    elif st.session_state.user_type == 'admin':
        dept = st.session_state.selected_dept
        q = st.session_state.queue_state[dept]
        waiting_count = q['last'] - q['current']
        tokens_issued = q['total_issued']
        
        st.markdown(f"<h1 style='color: #0a1e3c; font-size: 2.5rem;'>⚙️ {dept} Admin Panel</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                logout()
        
        # Admin control bar
        st.markdown(f"""
        <div class='admin-bar'>
            <div>
                <div class='stat-label'>CURRENT SERVING</div>
                <div class='big-number'>{q['current']}</div>
            </div>
            <div>
                <div class='stat-label'>LAST TOKEN</div>
                <div class='big-number'>{q['last']}</div>
            </div>
            <div>
                <div class='stat-label'>ISSUED</div>
                <div class='big-number'>{tokens_issued}/80</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Control buttons
        st.markdown("<h3 style='color: #0a1e3c; margin-top: 1rem;'>Queue Controls</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➡️ NEXT TOKEN", use_container_width=True):
                if not q['paused'] and q['current'] < q['last']:
                    st.session_state.queue_state[dept]['current'] += 1
                    st.rerun()
                elif q['paused']:
                    st.warning("⏸️ Queue is paused")
                else:
                    st.warning("No more tokens waiting")
        
        with col2:
            if not q['paused']:
                if st.button("⏸️ PAUSE QUEUE", use_container_width=True):
                    st.session_state.queue_state[dept]['paused'] = True
                    st.rerun()
            else:
                if st.button("▶️ RESUME QUEUE", use_container_width=True):
                    st.session_state.queue_state[dept]['paused'] = False
                    st.rerun()
        
        with col3:
            st.button("🔄 REFRESH", use_container_width=True, on_click=lambda: st.rerun())
        
        # Status card
        status_text = "RUNNING" if not q['paused'] else "PAUSED"
        status_class = "status-running" if not q['paused'] else "status-paused"
        next_token = q['current'] + 1 if q['current'] < q['last'] else "No tokens"
        tokens_left = 80 - tokens_issued
        
        st.markdown(f"""
        <div class='admin-status-card'>
            <p><strong>Queue Status:</strong> 
                <span class='status-badge {status_class}'>{status_text}</span>
            </p>
            <p><strong>Next Token to Call:</strong> <span style='font-size: 2rem; color: #2563eb;'>{next_token}</span></p>
            <p><strong>Tokens Issued:</strong> {tokens_issued} out of 80 <span class='red-badge'>{tokens_left} left</span></p>
            <p><strong>People Waiting:</strong> {waiting_count}</p>
            <p><strong>Department:</strong> {dept}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Token History Section - White background, RED text
        with st.expander("🔴 TOKEN HISTORY", expanded=False):
            dept_history = [h for h in st.session_state.token_history if h['department'] == dept]
            
            if dept_history:
                # Stats at the top
                total_issued = len(dept_history)
                served_tokens = q['current'] - 1
                
                st.markdown(f"""
                <div class='token-history-stats'>
                    <div>
                        <span class='number'>{total_issued}</span>
                        <span class='label'>Total Issued</span>
                    </div>
                    <div>
                        <span class='number'>{served_tokens}</span>
                        <span class='label'>Served</span>
                    </div>
                    <div>
                        <span class='number'>{waiting_count}</span>
                        <span class='label'>Waiting</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<h3 style='color: #dc2626; margin: 1rem 0;'>📋 Recent Tokens</h3>", unsafe_allow_html=True)
                
                # Show last 15 tokens
                for entry in reversed(dept_history[-15:]):
                    if entry['token'] < q['current']:
                        status_text = "✅ SERVED"
                        status_color = "#10b981"
                    else:
                        status_text = "⏳ WAITING"
                        status_color = "#f59e0b"
                    
                    st.markdown(f"""
                    <div class='token-history-item'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <strong>#{entry['token']}</strong>
                                <span style='margin-left: 1rem;'>{entry['issued_time'][:10]} at {entry['issued_time'][11:16]}</span>
                            </div>
                            <div>
                                <span style='background: {status_color}; color: white; padding: 0.2rem 1rem; border-radius: 2rem;'>{status_text}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No tokens issued yet for this department")

# ------------------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------------------
st.markdown("""
<div style='text-align: center; margin-top: 3rem; padding: 1rem; color: #475569;'>
    <hr>
    🎟️ QuickQ · Total Capacity: 80 Students
</div>
""", unsafe_allow_html=True)
