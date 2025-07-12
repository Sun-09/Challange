import streamlit as st
import json
import os
from datetime import datetime

# Constants
DATA_FILE = "challenge_data.json"
DING_FILE = "ding.mp3"
VICTORY_FILE = "victory.mp3"
BACKGROUND_MUSIC_FILE = "background.mp3"

# Data handling
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return None

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def reset_challenge():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

# Emoji messages
def get_emoji(percent):
    if percent < 25:
        return "🚶 Keep going!"
    elif percent < 50:
        return "🏃 You're halfway!"
    elif percent < 75:
        return "🔥 Crushing it!"
    elif percent < 100:
        return "💪 Almost there!"
    else:
        return "🎉 Done!"

# App UI
st.set_page_config(page_title="Challenge Tracker", layout="centered")
st.title("🏁 Daily Challenge Tracker")

# Animated CSS
st.markdown("""
    <style>
    .animated-bar {
        background: linear-gradient(to right, #00f260, #0575e6);
        height: 35px;
        border-radius: 10px;
        animation: growBar 2s ease-in-out infinite alternate;
    }
    @keyframes growBar {
        0% { opacity: 0.7; }
        100% { opacity: 1.0; }
    }
    .container {
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

data = load_data()

# Setup Challenge
if not data:
    st.subheader("🎯 Set Your Challenge")
    days = st.number_input("How many days is your challenge?", min_value=1, max_value=100, step=1)
    if st.button("🚀 Start Challenge"):
        save_data({
            "start_time": datetime.now().isoformat(),
            "challenge_days": days,
            "status": "running",
            "last_milestone": 0
        })
        st.success("Challenge Started!")
        st.rerun()

else:
    st.subheader("💥 Challenge in Progress")
    
    start_time = datetime.fromisoformat(data["start_time"])
    challenge_days = data["challenge_days"]
    total_secs = challenge_days * 24 * 60 * 60
    elapsed_secs = (datetime.now() - start_time).total_seconds()
    percent = min((elapsed_secs / total_secs) * 100, 100)
    milestone = int(percent // 5) * 5

    emoji_msg = get_emoji(percent)
    st.markdown(f"### {emoji_msg} ({percent:.2f}%)")

    # 🔊 Background music toggle
    st.markdown("---")
    music_enabled = st.toggle("🎵 Play Background Music", value=True)
    if music_enabled and os.path.exists(BACKGROUND_MUSIC_FILE):
        st.audio(BACKGROUND_MUSIC_FILE, format="audio/mp3", loop=True)

    # 🌈 Progress Bar
    bar_html = f"""
        <div class="container">
            <div style='width: {percent}%;' class='animated-bar'></div>
        </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)

    # 🔔 Motivational Ding at each 5%
    if milestone > data.get("last_milestone", 0) and milestone < 100:
        if os.path.exists(DING_FILE):
            st.audio(DING_FILE, format="audio/mp3", start_time=0)
        data["last_milestone"] = milestone
        save_data(data)

    # 🎉 Victory
    if percent >= 100:
        st.balloons()
        if os.path.exists(VICTORY_FILE):
            st.audio(VICTORY_FILE, format="audio/mp3", start_time=0)
        st.success("🎉 Congratulations! You completed your challenge!")
        if st.button("🔁 Start New Challenge"):
            reset_challenge()
            st.rerun()
    else:
        if st.button("❌ Stop Challenge"):
            reset_challenge()
            st.warning("Challenge stopped.")
            st.rerun()
