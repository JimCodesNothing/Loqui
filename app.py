import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

def play_sound(sound_type="success"):
    """Play a sound using Web Audio API (no files needed)."""
    if sound_type == "success":
        # Pleasant ascending chime (C5-E5-G5 major chord)
        js_code = """
        <script>
        (function() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const notes = [523.25, 659.25, 783.99];
                notes.forEach((freq, i) => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.frequency.value = freq;
                    osc.type = 'sine';
                    const startTime = ctx.currentTime + i * 0.08;
                    gain.gain.setValueAtTime(0.001, startTime);
                    gain.gain.exponentialRampToValueAtTime(0.3, startTime + 0.02);
                    gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.4);
                    osc.start(startTime);
                    osc.stop(startTime + 0.4);
                });
            } catch(e) { console.log('Audio error:', e); }
        })();
        </script>
        """
    elif sound_type == "achievement":
        # Triumphant fanfare (bigger chord)
        js_code = """
        <script>
        (function() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const notes = [392, 523.25, 659.25, 783.99, 1046.5];
                notes.forEach((freq, i) => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.frequency.value = freq;
                    osc.type = 'triangle';
                    const startTime = ctx.currentTime + i * 0.1;
                    gain.gain.setValueAtTime(0.001, startTime);
                    gain.gain.exponentialRampToValueAtTime(0.25, startTime + 0.03);
                    gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.6);
                    osc.start(startTime);
                    osc.stop(startTime + 0.6);
                });
            } catch(e) { console.log('Audio error:', e); }
        })();
        </script>
        """
    elif sound_type == "challenge":
        # Quick celebratory ding
        js_code = """
        <script>
        (function() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.frequency.value = 880;
                osc.type = 'sine';
                gain.gain.setValueAtTime(0.3, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
                osc.start();
                osc.stop(ctx.currentTime + 0.5);
            } catch(e) { console.log('Audio error:', e); }
        })();
        </script>
        """
    components.html(js_code, height=0)
# ---------- Page config ----------
st.set_page_config(page_title="Cold Approach Tracker", page_icon="🎯", layout="wide")
# Add this right after st.set_page_config()
if st.sidebar.button("🔄 Reset Session (Debug)"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
# ---------- Constants ----------
RESULT_OPTIONS = ["", "Success", "Rejected", "Pending", "No Answer", "Voicemail", "Not Interested", "Callback Scheduled", "Other"]
METHOD_OPTIONS = ["", "In-Person", "Phone Call", "Email", "LinkedIn DM", "Instagram DM", "Twitter DM", "Text Message", "Other"]

# ---------- Achievement definitions ----------
ACHIEVEMENTS = [
    {"id": "first_log",       "name": "First Step",          "icon": "👣", "desc": "Log your first approach",                    "check": lambda df: len(df) >= 1},
    {"id": "ten_logs",        "name": "Getting Started",     "icon": "🔟", "desc": "Log 10 approaches",                          "check": lambda df: len(df) >= 10},
    {"id": "fifty_logs",      "name": "Half Century",        "icon": "💯", "desc": "Log 50 approaches",                          "check": lambda df: len(df) >= 50},
    {"id": "hundred_logs",    "name": "Centurion",           "icon": "🏛️", "desc": "Log 100 approaches",                         "check": lambda df: len(df) >= 100},
    {"id": "first_success",   "name": "First Win",           "icon": "🎉", "desc": "Get your first success",                     "check": lambda df: (df["Result"] == "Success").any()},
    {"id": "ten_successes",   "name": "Closer",              "icon": "🤝", "desc": "Get 10 successes",                           "check": lambda df: (df["Result"] == "Success").sum() >= 10},
    {"id": "fifty_successes", "name": "Sales Machine",       "icon": "🏆", "desc": "Get 50 successes",                           "check": lambda df: (df["Result"] == "Success").sum() >= 50},
    {"id": "streak_7",        "name": "Week Warrior",        "icon": "🔥", "desc": "Maintain a 7-day streak",                    "check": lambda df: calc_best_streak(df) >= 7},
    {"id": "streak_30",       "name": "Monthly Master",      "icon": "⚡", "desc": "Maintain a 30-day streak",                   "check": lambda df: calc_best_streak(df) >= 30},
    {"id": "multi_method",    "name": "Multi-Channel",       "icon": "📡", "desc": "Use 3+ different methods",                   "check": lambda df: (df["Method"] != "").nunique() >= 3},
    {"id": "multi_location",  "name": "Well-Traveled",       "icon": "🗺️", "desc": "Approach in 5+ different locations",         "check": lambda df: (df["Location"] != "").nunique() >= 5},
    {"id": "early_bird",      "name": "Early Bird",          "icon": "🌅", "desc": "Log an approach before 9 AM",                "check": lambda df: _is_before(df, 9)},
    {"id": "night_owl",       "name": "Night Owl",           "icon": "🦉", "desc": "Log an approach after 9 PM",                 "check": lambda df: _is_after(df, 21)},
]

def _is_before(df, hour):
    try:
        return df["Time"].apply(lambda t: int(str(t).split(":")[0]) < hour).any()
    except Exception:
        return False

def _is_after(df, hour):
    try:
        return df["Time"].apply(lambda t: int(str(t).split(":")[0]) >= hour).any()
    except Exception:
        return False

# ---------- Streak calculation ----------
def calc_streaks(df):
    """Returns (current_streak, best_streak)."""
    if df.empty or "Date" not in df.columns:
        return 0, 0
    try:
        dates = sorted(set(pd.to_datetime(df["Date"]).dt.date))
    except Exception:
        return 0, 0
    if not dates:
        return 0, 0

    # Best streak
    best = 1
    current_run = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_run += 1
            best = max(best, current_run)
        else:
            current_run = 1

    # Current streak (must include today or yesterday)
    today = datetime.date.today()
    if dates[-1] == today:
        end = today
    elif dates[-1] == today - datetime.timedelta(days=1):
        end = today - datetime.timedelta(days=1)
    else:
        return 0, best

    streak = 1
    for i in range(len(dates) - 1, 0, -1):
        if (dates[i] - dates[i-1]).days == 1:
            streak += 1
        else:
            break
    return streak, best

def calc_best_streak(df):
    _, best = calc_streaks(df)
    return best
# ---------- Session state ----------
if "approach_log" not in st.session_state:
    st.session_state.approach_log = []
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "show_login" not in st.session_state:
    st.session_state.show_login = True

# ---------- Login Screen ----------
if st.session_state.show_login and not st.session_state.current_user:
    st.title("🎯 Cold Approach Tracker")
    st.markdown("### Login or Create Account")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Login**")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if login_user and login_pass:
                st.session_state.current_user = login_user
                st.session_state.show_login = False
                load_data()
                st.rerun()
    
    with col2:
        st.markdown("**Create Account**")
        new_user = st.text_input("Username", key="new_user")
        new_pass = st.text_input("Password", type="password", key="new_pass")
        if st.button("Create Account", use_container_width=True):
            if new_user and new_pass:
                st.session_state.current_user = new_user
                st.session_state.show_login = False
                st.rerun()
    
    st.stop()

# ---------- Helpers ----------
def to_dataframe():
    if not st.session_state.approach_log:
        return pd.DataFrame(columns=["Date", "Time", "Name", "Location", "Method", "Result", "Notes", "FollowUp"])
    return pd.DataFrame(st.session_state.approach_log)

def save_to_csv():
    return to_dataframe().to_csv(index=False).encode("utf-8")

def load_from_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    st.session_state.approach_log = df.to_dict("records")

# ---------- UI ----------
# Debug: Reset session
if st.sidebar.button("🔄 Reset Session (Debug)", key="reset_session_btn"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
st.title("🎯 Cold Approach Tracker")
st.caption("Track every approach. Analyze what works. Close more deals.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Log New", "📋 View All", "📊 Stats", "🏆 Gamification", "💾 Save / Load"])

# ===== TAB 1: LOG NEW =====
with tab1:
    now = datetime.datetime.now()
    col1, col2 = st.columns(2)
    with col1:
        date_val = st.date_input("📅 Date", value=now.date())
        time_val = st.text_input("🕐 Time", value=now.strftime("%H:%M:%S"))
        name_val = st.text_input("👤 Name", placeholder="John Doe")
        location_val = st.text_input("📍 Location", placeholder="City, venue, or address")
    with col2:
        method_val = st.selectbox("📞 Method", options=METHOD_OPTIONS)
        result_val = st.selectbox("🎯 Result", options=RESULT_OPTIONS)
        followup_val = st.date_input("📅 Follow-up Date", value=None)
    notes_val = st.text_area("📝 Notes", placeholder="Context, conversation details, next steps...", height=100)

    if st.button("✅ Log Approach", type="primary", use_container_width=True):
        if not result_val:
            st.warning("⚠️ Please select a result before logging.")
        else:
            entry = {
                "Date": date_val.strftime("%Y-%m-%d"),
                "Time": time_val.strip() or now.strftime("%H:%M:%S"),
                "Name": name_val.strip(),
                "Location": location_val.strip(),
                "Method": method_val,
                "Result": result_val,
                "Notes": notes_val.strip(),
                "FollowUp": followup_val.strftime("%Y-%m-%d") if followup_val else "",
            }
            st.session_state.approach_log.append(entry)
            save_data()
            play_sound("success")
            st.success(f"✅ Logged! Total: {len(st.session_state.approach_log)}")
            st.rerun()

# ===== TAB 2: VIEW ALL =====
with tab2:
    df = to_dataframe()
    if df.empty:
        st.info("No approaches logged yet. Go to 'Log New' to add one.")
    else:
        st.dataframe(df.sort_values(by=["Date", "Time"], ascending=[False, False]),
                     use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("🗑️ Delete an entry")
        options = [f"{i+1}. {r['Date']} | {r.get('Name', '')} @ {r.get('Location', '')} | {r['Result']}"
                   for i, r in enumerate(st.session_state.approach_log)]
        to_delete = st.selectbox("Select to delete", options=["(none)"] + options)
        if st.button("🗑️ Delete Selected", type="secondary") and to_delete != "(none)":
            idx = options.index(to_delete)
            removed = st.session_state.approach_log.pop(idx)
            st.success(f"Deleted: {removed.get('Name', 'Unknown')}")
            st.rerun()

# ===== TAB 3: STATS =====
with tab3:
    df = to_dataframe()
    if df.empty:
        st.info("No data yet.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(df))
        c1.metric("Successes", len(df[df["Result"] == "Success"]))
        success_rate = len(df[df["Result"] == "Success"]) / len(df) * 100 if len(df) else 0
        c2.metric("Success Rate", f"{success_rate:.1f}%")
        c3.metric("Locations", (df["Location"] != "").sum())
        c4.metric("Methods Used", (df["Method"] != "").nunique())
        
        st.subheader("📈 Results Breakdown")
        st.bar_chart(df["Result"].value_counts())
        if df["Method"].any():
            st.subheader("📞 Methods Used")
            st.bar_chart(df[df["Method"] != ""]["Method"].value_counts())
        if df["Location"].any():
            st.subheader("📍 Top Locations")
            st.bar_chart(df[df["Location"] != ""]["Location"].value_counts().head(10))
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        upcoming = df[(df["FollowUp"] != "") & (df["FollowUp"] >= today)]
        if not upcoming.empty:
            st.subheader(f"📅 Upcoming Follow-ups ({len(upcoming)})")
            st.dataframe(upcoming[["Date", "Name", "Location", "FollowUp", "Result"]],
                         use_container_width=True, hide_index=True)

# ===== TAB 4: GAMIFICATION (NEW!) =====
with tab4:
    df = to_dataframe()
    current_streak, best_streak = calc_streaks(df)
    today = datetime.date.today()
    month_start = today.replace(day=1)
    month_df = df[pd.to_datetime(df["Date"]).dt.date >= month_start] if not df.empty else df
    month_total = len(month_df)
    month_successes = len(month_df[month_df["Result"] == "Success"]) if not month_df.empty else 0
    
    # --- Streaks section ---
    st.subheader("🔥 Streaks")
    c1, c2 = st.columns(2)
    c1.metric("Current Streak", f"{current_streak} day{'s' if current_streak != 1 else ''}",
              delta="Keep it going!" if current_streak > 0 else "Log today to start!")
    c2.metric("Best Streak", f"{best_streak} day{'s' if best_streak != 1 else ''}")
    
    if current_streak > 0:
        st.progress(min(current_streak / 30, 1.0), text=f"Next milestone: 30-day streak ({current_streak}/30)")
    st.divider()
    
    # --- Achievements section ---
    st.subheader("🏅 Achievements")
    unlocked = [a for a in ACHIEVEMENTS if a["check"](df)]
    locked = [a for a in ACHIEVEMENTS if a not in unlocked]
    
    st.success(f"You've unlocked **{len(unlocked)} / {len(ACHIEVEMENTS)}** achievements!")
    
   if unlocked:
    # Check for newly unlocked achievements
    if "last_achievement_count" not in st.session_state:
        st.session_state.last_achievement_count = 0
    if len(unlocked) > st.session_state.last_achievement_count:
        play_sound("achievement")  # 🎵 Play fanfare for new achievement!
        st.session_state.last_achievement_count = len(unlocked)
    
    st.markdown("**✅ Unlocked:**")
    cols = st.columns(3)
    for i, a in enumerate(unlocked):
        with cols[i % 3]:
            st.markdown(f"### {a['icon']} {a['name']}\n*{a['desc']}*")
    
    if locked:
        st.markdown("**🔒 Locked:**")
        cols = st.columns(3)
        for i, a in enumerate(locked):
            with cols[i % 3]:
                st.markdown(f"### 🔒 {a['name']}\n*{a['desc']}*")
    st.divider()
    
    # --- Monthly challenges section ---
    st.subheader(f"🎯 Monthly Challenges — {today.strftime('%B %Y')}")
    
    # Initialize challenge goals in session state
    if "challenge_logs" not in st.session_state:
        st.session_state.challenge_logs = 20
    if "challenge_successes" not in st.session_state:
        st.session_state.challenge_successes = 5
    if "challenge_streak" not in st.session_state:
        st.session_state.challenge_streak = 7
    
    with st.expander("⚙️ Set your goals"):
        st.session_state.challenge_logs = st.number_input(
            "Monthly approaches goal", min_value=1, value=st.session_state.challenge_logs, step=5)
        st.session_state.challenge_successes = st.number_input(
            "Monthly successes goal", min_value=1, value=st.session_state.challenge_successes, step=1)
        st.session_state.challenge_streak = st.number_input(
            "Streak goal (days)", min_value=1, value=st.session_state.challenge_streak, step=1)
    
    # Challenge 1: Monthly logs
    goal1 = st.session_state.challenge_logs
    prog1 = min(month_total / goal1, 1.0)
    st.markdown(f"**📋 Log {goal1} approaches this month**")
    st.progress(prog1, text=f"{month_total} / {goal1}")
    if prog1 >= 1.0:
    play_sound("challenge")  # 🎵 Play celebration ding
    st.balloons()
    st.success("🏆 Challenge complete!")
    # Challenge 2: Monthly successes
    goal2 = st.session_state.challenge_successes
    prog2 = min(month_successes / goal2, 1.0)
    st.markdown(f"**🎯 Get {goal2} successes this month**")
    st.progress(prog2, text=f"{month_successes} / {goal2}")
   if prog2 >= 1.0:
    play_sound("challenge")  # 🎵 Play celebration ding
    st.balloons()
    st.success("🏆 Challenge complete!")
    
    # Challenge 3: Streak
    goal3 = st.session_state.challenge_streak
    prog3 = min(current_streak / goal3, 1.0)
    st.markdown(f"**🔥 Maintain a {goal3}-day streak**")
    st.progress(prog3, text=f"{current_streak} / {goal3}")
    if prog3 >= 1.0:
    play_sound("challenge")  # 🎵 Play celebration ding
    st.balloons()
    st.success("🏆 Challenge complete!")

# ===== TAB 5: SAVE / LOAD =====
with tab5:
    st.info("💾 Your data is saved in your browser session. Download a CSV backup regularly!")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download CSV", data=save_to_csv(),
                           file_name="cold_approach_log.csv", mime="text/csv",
                           use_container_width=True)
    with col2:
        uploaded = st.file_uploader("📤 Load CSV backup", type=["csv"])
        if uploaded and st.button("Import", use_container_width=True):
            load_from_csv(uploaded)
            st.success(f"Imported {len(st.session_state.approach_log)} entries!")
            st.rerun()
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.approach_log = []
        st.rerun()
