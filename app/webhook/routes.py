from flask import Blueprint, send_from_directory, jsonify, request
from ..extensions import mongo

# Blueprint configuration for webhook
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


# Route to handle GitHub webhooks sent to /webhook/receiver (POST method)
@webhook.route('/receiver', methods=["POST"], endpoint='receiver_post')
def github_webhook():
    # Check if the content type of the request is JSON
    if request.headers['Content-Type'] == 'application/json':
        payload = request.json  # Parse the JSON payload
        action = payload.get('action')  # Get the 'action' field from the payload
        ref = payload.get('ref')  # Get the 'ref' field from the payload (if available)

        # Prepare a dictionary to store the parsed event data
        log_data = {
            "request_id": "",
            "author": "",
            "action": "",
            "from_branch": "",
            "to_branch": "",
            "timestamp": ""
        }

        # Check if the payload is a 'push' event
        if action is None and 'commits' in payload:
            author = payload['pusher']['name']  # Extract the author name from payload
            branch = ref.split('/')[-1]  # Extract the branch name from the 'ref'
            timestamp = payload['head_commit']['timestamp']  # Extract the commit timestamp
            commit_hash = payload['head_commit']['id']  # Extract the commit hash
            # Populate log data for a 'push' event
            log_data["request_id"] = commit_hash
            log_data["author"] = author
            log_data["action"] = "PUSH"
            log_data["from_branch"] = branch
            log_data["to_branch"] = branch
            log_data["timestamp"] = timestamp
            print(f'"{author}" pushed to "{branch}" on {timestamp}')

        # Check if the payload is a 'pull request opened' event
        elif action == 'opened':
            author = payload['pull_request']['user']['login']  # Extract the author's username
            source_branch = payload['pull_request']['head']['ref']  # Extract the source branch
            target_branch = payload['pull_request']['base']['ref']  # Extract the target branch
            timestamp = payload['pull_request']['created_at']  # Extract the creation timestamp
            pr_id = str(payload['pull_request']['id'])  # Extract the pull request ID
            # Populate log data for a 'pull request opened' event
            log_data["request_id"] = pr_id
            log_data["author"] = author
            log_data["action"] = "PULL_REQUEST"
            log_data["from_branch"] = source_branch
            log_data["to_branch"] = target_branch
            log_data["timestamp"] = timestamp
            print(f'"{author}" submitted a pull request from "{source_branch}" to "{target_branch}" on {timestamp}')

        # Check if the payload is a 'pull request merged' event
        elif action == 'closed' and payload['pull_request']['merged']:
            author = payload['pull_request']['user']['login']  # Extract the author's username
            source_branch = payload['pull_request']['head']['ref']  # Extract the source branch
            target_branch = payload['pull_request']['base']['ref']  # Extract the target branch
            timestamp = payload['pull_request']['merged_at']  # Extract the merge timestamp
            pr_id = str(payload['pull_request']['id'])  # Extract the pull request ID
            # Populate log data for a 'pull request merged' event
            log_data["request_id"] = pr_id
            log_data["author"] = author
            log_data["action"] = "MERGE"
            log_data["from_branch"] = source_branch
            log_data["to_branch"] = target_branch
            log_data["timestamp"] = timestamp
            print(f'"{author}" merged branch "{source_branch}" to "{target_branch}" on {timestamp}')

        else:
            # If the action is unknown, print an error message and return a 400 response
            print(f"Unknown action: {action}")
            return jsonify({"error": "Unknown action"}), 400

        # Store the formatted log data in MongoDB
        try:
            mongo.db.webhook_logs.insert_one(log_data)  # Insert the log data into the 'webhook_logs' collection
            print("Event log successfully inserted into MongoDB.")
            return jsonify({"message": "GitHub event data processed and stored"}), 200
        except Exception as e:
            print(f"Error storing GitHub event data in MongoDB: {e}")
            return jsonify({"error": str(e)}), 500

    # If the request is not JSON, return a 400 response
    return jsonify({"error": "Invalid content type"}), 400


# Route to retrieve data from MongoDB and return it as JSON
@webhook.route('/data', methods=["GET"])
def get_data():
    try:
        # Retrieve data from MongoDB
        logs = mongo.db.webhook_logs.find()
        # Convert MongoDB cursor to a list of dictionaries
        logs_list = list(logs)
        # Convert MongoDB ObjectId to string
        for log in logs_list:
            log['_id'] = str(log['_id'])
        return jsonify(logs_list), 200
    except Exception as e:
        print(f"Error retrieving data from MongoDB: {e}")
        return jsonify({"error": str(e)}), 500
