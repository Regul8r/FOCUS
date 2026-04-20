from plaid_service import get_balances
import os
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('PLAID_ACCESS_TOKEN')
accounts = get_balances(access_token)

for account in accounts:
    print(f"{account['name']} - ${account['balance']} ({account['type']})")
