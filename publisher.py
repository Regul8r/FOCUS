"""
FOCUS - Financial Data Publisher
Run this in Terminal 1: python3 publisher.py

Publishes account data via MQTT AND writes to a local JSON file.
Streamlit reads the JSON file — reliable, no threading issues.
"""

import json
import time
import os
import paho.mqtt.client as mqtt

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BROKER    = "broker.hivemq.com"
PORT      = 1883
TOPIC     = "focus/accounts"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "focus_data.json")

# ─── ACCOUNT DATA ─────────────────────────────────────────────────────────────
ACCOUNTS = [
    {"id": 1, "name": "Checking",    "icon": "🏦", "balance": 847.50,  "goal": 500.00,  "type": "savings", "category": "Everyday spending"},
    {"id": 2, "name": "Savings",     "icon": "💰", "balance": 2340.00, "goal": 1000.00, "type": "savings", "category": "Emergency fund"},
    {"id": 3, "name": "Credit Card", "icon": "💳", "balance": 680.00,  "goal": 500.00,  "type": "credit",  "category": "Monthly spending"},
    {"id": 4, "name": "Rent Fund",   "icon": "🏠", "balance": 1200.00, "goal": 1200.00, "type": "savings", "category": "Fixed expense"},
    {"id": 5, "name": "Vacation Money", "icon": "🚢", "balance": 45.00,   "goal": 90.00,  "type": "savings", "category": "Vacation Fund"},
    {"id": 6, "name": "Car Maintenance", "icon": "🚘", "balance": 85.00, "goal": 200.00, "type": "savings", "category": "Car fund"},
]


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
    return [{**acct, "health": get_health(acct)} for acct in ACCOUNTS]


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
