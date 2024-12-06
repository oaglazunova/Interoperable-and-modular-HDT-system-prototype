import os
import json
from dotenv import load_dotenv
import logging
from logging import FileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set global logging level to INFO
    format='%(asctime)s [%(levelname)s] [%(name)s]: %(message)s',  # Ensure root logger uses the same format
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        FileHandler('config/logging.log')  # Updated path for log file in the config folder
    ]
)

# Suppress debug logs from external libraries by setting their level to WARNING
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
# Add any other external loggers you wish to suppress

# Load environment variables from the .env file located in the config folder
load_dotenv(dotenv_path="config/.env")  # Explicitly specify the path to the .env file

def load_external_parties(filepath='config/external_parties.json'):
    """
    Load external parties from the specified JSON file, adding API keys from environment variables.
    """
    try:
        with open(filepath, 'r') as f:
            external_parties = json.load(f)['external_parties']
        
        for party in external_parties:
            client_id = party['client_id']
            api_key_env_var = f"{client_id.upper()}_API_KEY"
            api_key = os.getenv(api_key_env_var)
            if not api_key:
                logging.error(f"Environment variable {api_key_env_var} not set for client '{client_id}'. Skipping this client.")
                continue  # Optionally, skip clients without API keys
            party['api_key'] = api_key
            logging.debug(f"Loaded API key for {client_id}")  # This will not appear unless specific logger is set to DEBUG
        return external_parties
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return []
    except json.JSONDecodeError:
        logging.error(f"Failed to parse JSON file: {filepath}")
        return []

def load_user_permissions(filepath='config/user_permissions.json'):
    """
    Load user permissions from the specified JSON file.
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Failed to parse JSON file: {filepath}")
        return {}
