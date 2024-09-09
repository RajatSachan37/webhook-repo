from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import timezone
import datetime

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["webhook_db"]
collection = db["webhook_events"]


@app.route("/", methods=["GET"])
def test():
    return "Techstax Assignment"

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        data = request.json
        event_type = request.headers.get("X-GitHub-Event")

        if event_type == "push":
            # Parse push event
            event = {
                "type": "push",
                "author": data["pusher"]["name"],
                "to_branch": data["ref"].split("/")[-1],
                "timestamp": datetime.datetime.now(timezone.utc),
            }
    
        # Handle the 'pull_request' event
        elif event_type == "pull_request":
            # Check if the pull request has been merged
            if data["action"] == "closed" and data["pull_request"]["merged"]:
                # Handle merge event
                print("merged here 1st")
                event = {
                    "type": "merge",
                    "author": data["pull_request"]["user"]["login"],
                    "from_branch": data["pull_request"]["head"]["ref"],
                    "to_branch": data["pull_request"]["base"]["ref"],
                    "timestamp": datetime.datetime.now(timezone.utc),
                }
            else:
                # Handle pull request event
                event = {
                    "type": "pull_request",
                    "author": data["pull_request"]["user"]["login"],
                    "from_branch": data["pull_request"]["head"]["ref"],
                    "to_branch": data["pull_request"]["base"]["ref"],
                    "timestamp": datetime.datetime.now(timezone.utc),
                    # timezone.utc
                }

        else:
            return "Event type not supported", 400
        # Store event in MongoDB
        collection.insert_one(event)
        return jsonify({"message": "Event received!"}), 200


@app.route("/events")
def get_events():
    events = list(collection.find({},{'_id':0}).sort("timestamp", -1).limit(100))
    return jsonify({"events": events})


@app.route("/dashboard")
def index():
    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
