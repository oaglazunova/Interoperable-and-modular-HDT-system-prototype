from functools import wraps
from flask import request, jsonify
import logging


def authenticate_and_authorize(external_parties, user_permissions, required_permission):
    """
    Decorator factory to authenticate and authorize based on required_permission.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Authentication
            api_key = request.headers.get("X-API-KEY")  # Use the updated header key
            if not api_key:
                logging.debug("API key is missing in the request.")
                return jsonify({"error": "API key is missing"}), 401

            # Verify API key
            client = next((c for c in external_parties if c["api_key"] == api_key), None)
            if not client:
                logging.debug("Invalid API key provided.")
                return jsonify({"error": "Invalid API key"}), 401

            # Determine accessible user IDs based on required_permission
            accessible_user_ids = []
            for user_id_str, perms in user_permissions.items():
                if client["client_id"] in perms.get("allowed_clients", {}):
                    if required_permission in perms["allowed_clients"][client["client_id"]]:
                        try:
                            user_id = int(user_id_str)
                            accessible_user_ids.append(user_id)
                        except ValueError:
                            logging.warning(f"Invalid user_id format: {user_id_str}")
                            continue

            if not accessible_user_ids:
                logging.debug("No permissions set for this user.")
                return jsonify({"error": "No permissions set for this user"}), 403

            # Attach client info and accessible_user_ids to request context
            request.client = client
            request.accessible_user_ids = accessible_user_ids

            logging.debug(f"Client '{client['client_id']}' has access to user IDs: {accessible_user_ids} for permission '{required_permission}'")

            return f(*args, **kwargs)
        return decorated_function
    return decorator
