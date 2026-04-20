import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
import os
from dotenv import load_dotenv

load_dotenv()

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Create sandbox public token
request = SandboxPublicTokenCreateRequest(
    institution_id='ins_109508',
    initial_products=[Products('transactions')]
)
response = client.sandbox_public_token_create(request)
public_token = response['public_token']
print(f"Public token: {public_token}")

# Exchange for access token
exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
exchange_response = client.item_public_token_exchange(exchange_request)
access_token = exchange_response['access_token']
print(f"Access token: {access_token}")
