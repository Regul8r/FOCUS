"""
FOCUS - Financial Data Publisher
Run this in Terminal 1: python3 publisher.py
"""

import json
import time
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from plaid_service import get_balances

load_dotenv()

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BROKER    = "broker.hivemq.com"
PORT      = 1883
TOPIC     = "focus/accounts"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "focus_data.json")

ACCESS_TOKEN = os.getenv('PLAID_ACCESS_TOKEN')

#  ─── ACCOUNT GOALS er defined) ────────────
GOALS = {
    "Plaid Checking":      {"goal": 500.00,   "type": "savings", "icon": "🏦", "category": "Everyday spending"},
    "Plaid Saving":        {"goal": 1000.00,  "type": "savings", "icon": "💰", "category": "Emergency fund"},
    "Plaid Credit Card":   {"goal": 500.00,   "type": "credit",  "icon": "💳", "category": "Monthly spending"},
    "Plaid Money Market":  {"goal": 10000.00, "type": "savings", "icon": "📈", "category": "Savings goal"},
}


def get_accounts():
    try:
        plaid_accounts = get_balances(ACCESS_TOKEN)
        accounts = []
        for i, acct in enumerate(plaid_accounts):
            name = acct['name']
            if name not in GOALS:
                continue
            meta = GOALS[name]
            accounts.append({
                "id": i + 1,
                "name": name,
                "icon": meta["icon"],
                "balance": acct['balance'] or 0,
                "goal": meta["goal"],
                "type": meta["type"],
                "category": meta["category"]
            })
        return accounts
    except Exception as e:
        print(f"Plaid error: {e}")
        return []

def get_health(account):
    balance = account["balance"]
    goal    = account["goal"]
    ratio   = balance / goal if goal > 0 else 1

    if account["type"] == "credit":
        if ratio <= 0.6:   return "green"
        elif ratio <= 0.9: return "yellow"
        else:              return "red"
    else:
        if ratio >= 1.0:   return "green"
        elif ratio >= 0.5: return "yellow"
        else:              return "red"


def build_payload():
    return [{**acct, "health": get_health(acct)} for acct in get_accounts()]


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    print(f"Connecting to MQTT broker at {BROKER}:{PORT}...")
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
        print("MQTT connected.\n")
    except Exception as e:
        print(f"MQTT connection failed: {e} — continuing with file only.\n")

    print(f"Writing data to: {DATA_FILE}")
    print(f"Publishing to MQTT topic: {TOPIC}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            payload = build_payload()
            message = json.dumps(payload)

            # Write to JSON file (Streamlit reads this)
            with open(DATA_FILE, "w") as f:
                json.dump(payload, f)

            # Also publish via MQTT
            try:
                client.publish(TOPIC, message, qos=1)
            except Exception:
                pass

            print(f"[{time.strftime('%H:%M:%S')}] Published {len(payload)} accounts")
            for acct in payload:
                icon = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[acct["health"]]
                print(f"  {icon} {acct['name']:12} ${acct['balance']:>8.2f}  (goal: ${acct['goal']:.2f})")
            print()

            time.sleep(10)

    except KeyboardInterrupt:
        print("\nPublisher stopped.")
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
