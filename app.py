import datetime
import pandas as pd
import streamlit as st

# ---------- Page config ----------
st.set_page_config(page_title="Cold Approach Tracker", page_icon="🎯", layout="wide")

# ---------- Constants ----------
RESULT_OPTIONS = ["", "Success", "Rejected", "Pending", "No Answer", "Voicemail", "Not Interested", "Callback Scheduled", "Other"]
METHOD_OPTIONS = ["", "In-Person", "Phone Call", "Email", "LinkedIn DM", "Instagram DM", "Twitter DM", "Text Message", "Other"]

# ---------- Session state (acts as our database) ----------
if "approach_log" not in st.session_state:
    st.session_state.approach_log = []

# ---------- Helper functions ----------
def to_dataframe():
    if not st.session_state.approach_log:
        return pd.DataFrame(columns=["Date", "Time", "Name", "Location", "Method", "Result", "Notes", "FollowUp"])
    return pd.DataFrame(st.session_state.approach_log)

def save_to_csv():
    df = to_dataframe()
    return df.to_csv(index=False).encode("utf-8")

def load_from_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    st.session_state.approach_log = df.to_dict("records")

# ---------- UI ----------
st.title("🎯 Cold Approach Tracker")
st.caption("Track every approach. Analyze what works. Close more deals.")

tab1, tab2, tab3, tab4 = st.tabs(["➕ Log New", "📋 View All", "📊 Stats", "💾 Save / Load"])

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
            st.success(f"✅ Logged! Total: {len(st.session_state.approach_log)}")
            st.rerun()

# ===== TAB 2: VIEW ALL =====
with tab2:
    df = to_dataframe()
    if df.empty:
        st.info("No approaches logged yet. Go to 'Log New' to add one.")
    else:
        st.dataframe(
            df.sort_values(by=["Date", "Time"], ascending=[False, False]),
            use_container_width=True,
            hide_index=True,
        )
        
        # Delete section
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
        
        st.subheader("📈 Results Breakdown")
        st.bar_chart(df["Result"].value_counts())
        
        if df["Method"].any():
            st.subheader("📞 Methods Used")
            st.bar_chart(df[df["Method"] != ""]["Method"].value_counts())
        
        if df["Location"].any():
            st.subheader("📍 Top Locations")
            st.bar_chart(df[df["Location"] != ""]["Location"].value_counts().head(10))
        
        # Upcoming follow-ups
        today = datetime.date.today().strftime("%Y-%m-%d")
        upcoming = df[(df["FollowUp"] != "") & (df["FollowUp"] >= today)]
        if not upcoming.empty:
            st.subheader(f"📅 Upcoming Follow-ups ({len(upcoming)})")
            st.dataframe(upcoming[["Date", "Name", "Location", "FollowUp", "Result"]], use_container_width=True, hide_index=True)

# ===== TAB 4: SAVE / LOAD =====
with tab4:
    st.info("💾 Your data is saved in your browser session. Download a CSV backup regularly!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download CSV",
            data=save_to_csv(),
            file_name="cold_approach_log.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        uploaded = st.file_uploader("📤 Load CSV backup", type=["csv"])
        if uploaded and st.button("Import", use_container_width=True):
            load_from_csv(uploaded)
            st.success(f"Imported {len(st.session_state.approach_log)} entries!")
            st.rerun()
    
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.approach_log = []
        st.rerun()
