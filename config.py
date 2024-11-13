import os

config = {
    'client_id': os.getenv('CLIENT_ID'),
    'client_secret': os.getenv('CLIENT_SECRET'),
    'tenant_id': os.getenv('TENANT_ID'),
    'authority': os.getenv('AUTHORITY'),
    'scope': ['https://graph.microsoft.com/.default']
}