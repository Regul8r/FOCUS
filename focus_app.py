"""
FOCUS - Financial Ambient Awareness Dashboard
Run this in Terminal 2: streamlit run focus_app.py
"""

import json
import os
import time
import streamlit as st
import anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "focus_data.json")

st.set_page_config(page_title="FOCUS", page_icon="🟦", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
    .stApp { background-color: #0a0a0a; color: #f0f0f0; }
    .stButton button { border: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; max-width: 100% !important; padding-left: 1rem !important; padding-right: 1rem !important; }
@media (max-width: 768px) {
    .focus-title { font-size: 1.8rem !important; }
    .summary-bar { flex-wrap: wrap; gap: 8px; }
    .summary-pill { font-size: 0.7rem !important; }
}
    .face-card {
        border-radius: 14px;
        padding: 22px 18px 16px;
        text-align: center;
        border: 1px solid transparent;
        margin-bottom: 6px;
        position: relative;
        overflow: hidden;
    }
    .face-green { background: linear-gradient(160deg, #0a2e18, #0f3d22); border-color: #2ecc71; box-shadow: 0 0 24px rgba(46,204,113,0.2); }
    .face-yellow { background: linear-gradient(160deg, #2e2000, #3d2c00); border-color: #f1c40f; box-shadow: 0 0 24px rgba(241,196,15,0.2); }
    .face-red { background: linear-gradient(160deg, #2e0000, #3d0a0a); border-color: #e74c3c; box-shadow: 0 0 24px rgba(231,76,60,0.25); animation: redpulse 2.5s ease-in-out infinite; }
    .face-dismissed { background: #111; border-color: #222; opacity: 0.35; }
    @keyframes redpulse { 0%, 100% { box-shadow: 0 0 24px rgba(231,76,60,0.25); } 50% { box-shadow: 0 0 40px rgba(231,76,60,0.5); } }
    .face-icon { font-size: 1.8rem; margin-bottom: 4px; }
    .face-name { font-size: 1rem; font-weight: 700; letter-spacing: 0.04em; margin-bottom: 2px; }
    .face-balance { font-size: 1.7rem; font-weight: 800; margin: 6px 0 2px; }
    .face-goal { font-size: 0.7rem; opacity: 0.5; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px; }
    .prog-track { width: 100%; height: 5px; background: rgba(255,255,255,0.08); border-radius: 99px; margin: 10px 0 14px; overflow: hidden; }
    .prog-fill-green { height: 5px; border-radius: 99px; background: #2ecc71; }
    .prog-fill-yellow { height: 5px; border-radius: 99px; background: #f1c40f; }
    .prog-fill-red { height: 5px; border-radius: 99px; background: #e74c3c; }
    .nudge-box { background: rgba(255,255,255,0.04); border-left: 3px solid #f1c40f; padding: 10px 14px; border-radius: 0 8px 8px 0; font-size: 0.88rem; line-height: 1.55; margin-top: 8px; text-align: left; color: #e0e0e0; }
    .summary-bar { display: flex; gap: 12px; background: #111; border: 1px solid #1e1e1e; border-radius: 10px; padding: 14px 20px; margin-bottom: 24px; align-items: center; }
    .summary-pill { border-radius: 6px; padding: 5px 14px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.06em; }
    .pill-green { background: rgba(46,204,113,0.12); color: #2ecc71; border: 1px solid rgba(46,204,113,0.25); }
    .pill-yellow { background: rgba(241,196,15,0.12); color: #f1c40f; border: 1px solid rgba(241,196,15,0.25); }
    .pill-red { background: rgba(231,76,60,0.12); color: #e74c3c; border: 1px solid rgba(231,76,60,0.25); }
    .pill-dim { background: rgba(255,255,255,0.04); color: #555; border: 1px solid #222; }
    .summary-label { font-size: 0.72rem; color: #444; letter-spacing: 0.1em; text-transform: uppercase; margin-left: auto; }
    .live-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #2ecc71; margin-right: 6px; animation: blink 1.5s infinite; }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
    .focus-header { text-align: center; padding: 10px 0 22px; }
    .focus-title { font-size: 2.6rem; font-weight: 900; letter-spacing: 0.35em; color: #fff; font-family: 'Space Mono', monospace; }
    .focus-sub { font-size: 0.75rem; letter-spacing: 0.18em; color: #444; text-transform: uppercase; margin-top: 4px; }
    .legend { display: flex; gap: 24px; justify-content: center; margin-top: 20px; }
    .legend-item { font-size: 0.78rem; color: #555; letter-spacing: 0.05em; }
    .settings-box { background: #111; border: 1px solid #1e1e1e; border-radius: 10px; padding: 20px; margin-bottom: 24px; }
    .settings-title { font-size: 0.75rem; letter-spacing: 0.15em; color: #444; text-transform: uppercase; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "dismissed"    not in st.session_state: st.session_state.dismissed    = set()
if "nudges"       not in st.session_state: st.session_state.nudges       = {}
if "lamp_color"   not in st.session_state: st.session_state.lamp_color   = "#00ff88"
if "speak_hour"   not in st.session_state: st.session_state.speak_hour   = 9

# ─── LOAD DATA ─────────────────────────────────────────────────────────────────
def load_accounts():
    try:
        if os.path.exists(DATA_FILE):
            age = time.time() - os.path.getmtime(DATA_FILE)
            with open(DATA_FILE) as f:
                return json.load(f), age
    except Exception as e:
        st.error(f"Error: {e}")
    return [], None

# ─── CLAUDE NUDGE ──────────────────────────────────────────────────────────────
def get_nudge(account):
    ai = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    health_context = {"green": "healthy", "yellow": "needs attention", "red": "danger zone"}.get(account["health"], "")
    msg = ai.messages.create(
        model="claude-sonnet-4-6", max_tokens=100,
        messages=[{"role": "user", "content":
            f"You are FOCUS, a financial awareness assistant. "
            f"Account: {account['name']}, Status: {health_context}. "
            f"Give one calm, plain-language nudge in 2 sentences max. No numbers. Sound like a financially savvy friend."
        }]
    )
    return msg.content[0].text.strip()

# ─── PROGRESS BAR ──────────────────────────────────────────────────────────────
def progress_bar(account):
    balance = account["balance"]
    goal    = account["goal"]
    health  = account["health"]
    if account["type"] == "credit":
        pct = max(0, min(100, (1 - balance / goal) * 100)) if goal > 0 else 0
    else:
        pct = max(0, min(100, (balance / goal) * 100)) if goal > 0 else 0
    return (
        f'<div class="prog-track">'
        f'<div class="prog-fill-{health}" style="width:{pct:.0f}%"></div>'
        f'</div>'
        f'<div class="face-goal">Goal: ${goal:,.0f} &nbsp;&middot;&nbsp; {pct:.0f}% there</div>'
    )

# ─── RENDER FACE ───────────────────────────────────────────────────────────────
def render_face(account, col):
    aid       = account["id"]
    dismissed = aid in st.session_state.dismissed
    health    = account["health"]

    with col:
        if dismissed:
            st.markdown(f"""
            <div class="face-card face-dismissed">
                <div class="face-icon">{account['icon']}</div>
                <div class="face-name">{account['name']}</div>
                <div style="font-size:0.7rem;color:#333;margin-top:6px">HANDLED ✓</div>
            </div>""", unsafe_allow_html=True)
            if st.button("↩ Restore", key=f"r{aid}", use_container_width=True):
                st.session_state.dismissed.discard(aid)
                st.rerun()
            return

        st.markdown(f"""
        <div class="face-card face-{health}">
            <div class="face-icon">{account['icon']}</div>
            <div class="face-name">{account['name']}</div>
            <div class="face-balance">${account['balance']:,.2f}</div>
            {progress_bar(account)}
        </div>""", unsafe_allow_html=True)

        if st.button("Get Insight ✦", key=f"n{aid}", use_container_width=True, type="primary"):
            with st.spinner("Claude is analyzing..."):
                try:
                    st.session_state.nudges[aid] = get_nudge(account)
                except Exception as e:
                    st.session_state.nudges[aid] = f"Error: {e}"
            st.rerun()

        if aid in st.session_state.nudges:
            st.markdown(f'<div class="nudge-box">✦ {st.session_state.nudges[aid]}</div>', unsafe_allow_html=True)

        if health == "green":
            if st.button("Dismiss ✓", key=f"d{aid}", use_container_width=True):
                st.session_state.dismissed.add(aid)
                st.rerun()

# ─── MAIN ──────────────────────────────────────────────────────────────────────
accounts, age = load_accounts()

st.markdown("""
<div class="focus-header">
    <div class="focus-title">FOCUS</div>
    <div class="focus-sub">ambient financial awareness · one face at a time</div>
</div>""", unsafe_allow_html=True)

# ─── SETTINGS ROW ──────────────────────────────────────────────────────────────
with st.expander("⚙ Lamp Settings", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        lamp_color = st.color_picker("Pick your ambient color", value=st.session_state.lamp_color, label_visibility="collapsed")
        st.session_state.lamp_color = lamp_color
        st.markdown(f'<div style="width:100%;height:40px;border-radius:8px;background:{lamp_color};margin-top:8px"></div>', unsafe_allow_html=True)
        user_name = st.text_input("Your name", value=st.session_state.get('user_name', ''), placeholder="Enter your name")
        st.session_state.user_name = user_name
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "focus_config.json"), "w") as f:
            json.dump({"lamp_color": lamp_color, "speak_hour": st.session_state.speak_hour, "user_name": user_name}, f)
    with col_b:
        st.markdown('<div class="settings-title">Daily summary time</div>', unsafe_allow_html=True)
        speak_hour = st.slider("What time should FOCUS speak?", 0, 23, st.session_state.speak_hour, label_visibility="collapsed")
        st.session_state.speak_hour = speak_hour
        hour_display = f"{speak_hour % 12 or 12}:00 {'AM' if speak_hour < 12 else 'PM'}"
        st.markdown(f'<div style="font-size:1.4rem;font-weight:700;color:#fff;margin-top:8px">{hour_display}</div>', unsafe_allow_html=True)

if accounts:
    counts = {"green": 0, "yellow": 0, "red": 0}
    for a in accounts:
        if a["id"] not in st.session_state.dismissed:
            counts[a["health"]] = counts.get(a["health"], 0) + 1

    dismissed_count = len(st.session_state.dismissed)
    freshness = f"Updated {int(age)}s ago" if age and age < 30 else "Reconnecting..."

    st.markdown(f"""
    <div class="summary-bar">
        <span class="live-dot"></span>
        <span class="summary-pill pill-green">🟢 {counts['green']} On Track</span>
        <span class="summary-pill pill-yellow">🟡 {counts['yellow']} Watch</span>
        <span class="summary-pill pill-red">🔴 {counts['red']} Hold</span>
        <span class="summary-pill pill-dim">✓ {dismissed_count} Dismissed</span>
        <span class="summary-label">{freshness}</span>
    </div>""", unsafe_allow_html=True)

    cols1 = st.columns(3, gap="medium")
    for i in range(min(3, len(accounts))):
        render_face(accounts[i], cols1[i])

    if len(accounts) > 3:
        cols2 = st.columns(3, gap="medium")
        for i in range(3, min(6, len(accounts))):
            render_face(accounts[i], cols2[i - 3])

    st.markdown("""
    <div class="legend">
        <span class="legend-item">🟢 Green — On track. Dismiss when ready.</span>
        <span class="legend-item">🟡 Yellow — Needs attention.</span>
        <span class="legend-item">🔴 Red — Hold. Take action now.</span>
    </div>""", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;color:#333">
        <div style="font-size:2rem;margin-bottom:12px">⏳</div>
        <div style="font-size:0.9rem;letter-spacing:0.1em;text-transform:uppercase">
            Waiting for publisher — run python3 publisher.py in Tab 1
        </div>
    </div>""", unsafe_allow_html=True)

time.sleep(5)
st.rerun()
