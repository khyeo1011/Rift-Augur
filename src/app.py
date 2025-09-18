from flask import Flask, jsonify, request, Response
import redis
import boto3
import uuid
import json
import os

app = Flask(__name__)

# --- Configuration ---
# Use environment variables for configuration in a real application
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000")
AWS_REGION = "us-west-2" # Example region

# --- Service Connections ---
# In a production environment, you'd handle connections and sessions more robustly.
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=DYNAMODB_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id='fakeMyKeyId', # Dummy credentials for local DynamoDB
        aws_secret_access_key='fakeSecretAccessKey'
    )
    # Create DynamoDB table if it doesn't exist
    try:
        dynamodb.create_table(
            TableName='PlayerProfiles',
            KeySchema=[{'AttributeName': 'player_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'player_id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        app.logger.info("Created DynamoDB table 'PlayerProfiles'")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        app.logger.info("DynamoDB table 'PlayerProfiles' already exists.")

except Exception as e:
    app.logger.error(f"Could not connect to services: {e}")
    redis_client = None
    dynamodb = None


# --- Helper Functions ---
def find_match():
    """
    A simple matchmaking logic.
    In a real system, this would be a more complex, asynchronous process.
    """
    queue_name = 'matchmaking_queue'
    # For simplicity, we'll try to match 2 players.
    if redis_client and redis_client.zcard(queue_name) >= 2:
        # Get two players from the queue
        players_to_match = redis_client.zrange(queue_name, 0, 1)
        if players_to_match:
            match_id = str(uuid.uuid4())
            app.logger.info(f"Match found! ID: {match_id} with players: {players_to_match}")
            # Remove players from queue
            redis_client.zrem(queue_name, *players_to_match)
            # Publish a "match_found" event
            match_details = {"match_id": match_id, "players": players_to_match}
            redis_client.publish('match_notifications', json.dumps(match_details))
            return match_details
    return None

# --- API Endpoints ---
@app.route('/')
def index():
    return jsonify({"message": "Intelligent Gaming Matchmaking & Analytics Platform is running!"})

@app.route('/queue', methods=['POST'])
def join_queue():
    """Adds a player to the matchmaking queue."""
    data = request.get_json()
    player_id = data.get('player_id')
    mmr = data.get('mmr')

    if not player_id or not isinstance(mmr, int):
        return jsonify({"error": "player_id and a valid mmr are required"}), 400

    if not redis_client:
        return jsonify({"error": "Redis connection not available"}), 500

    try:
        # Add player to a sorted set with MMR as the score
        redis_client.zadd('matchmaking_queue', {player_id: mmr})
        app.logger.info(f"Player {player_id} added to queue with MMR {mmr}")

        # Attempt to find a match
        find_match()

        return jsonify({"status": f"player {player_id} added to queue"}), 200
    except Exception as e:
        app.logger.error(f"Error adding to queue: {e}")
        return jsonify({"error": "Could not add player to queue"}), 500


@app.route('/player/<string:player_id>/stats', methods=['GET'])
def get_player_stats(player_id):
    """Retrieves a player's profile and stats from DynamoDB."""
    if not dynamodb:
         return jsonify({"error": "DynamoDB connection not available"}), 500

    # First, try to get from Redis cache
    if redis_client:
        cached_stats = redis_client.get(f"player_cache:{player_id}")
        if cached_stats:
            app.logger.info(f"Cache hit for player {player_id}")
            return jsonify(json.loads(cached_stats)), 200

    app.logger.info(f"Cache miss for player {player_id}")
    table = dynamodb.Table('PlayerProfiles')
    try:
        response = table.get_item(Key={'player_id': player_id})
        if 'Item' in response:
            # Cache the result in Redis for 5 minutes
            if redis_client:
                redis_client.setex(f"player_cache:{player_id}", 300, json.dumps(response['Item']))
            return jsonify(response['Item']), 200
        else:
            # For this example, create a new player if not found
            new_player = {
                'player_id': player_id,
                'mmr': 1000,
                'wins': 0,
                'losses': 0,
                'character_preferences': ['DefaultChar']
            }
            table.put_item(Item=new_player)
            return jsonify(new_player), 201
    except Exception as e:
        app.logger.error(f"DynamoDB error: {e}")
        return jsonify({"error": "Could not retrieve player stats"}), 500

@app.route('/matches/<string:match_id>/results', methods=['POST'])
def post_match_results(match_id):
    """Updates player stats after a match."""
    data = request.get_json()
    winner_team = data.get('winner_team', [])
    loser_team = data.get('loser_team', [])

    if not winner_team or not loser_team:
        return jsonify({"error": "Winner and loser teams must be provided"}), 400

    if not dynamodb:
         return jsonify({"error": "DynamoDB connection not available"}), 500

    table = dynamodb.Table('PlayerProfiles')
    try:
        # Update winners
        for player_id in winner_team:
            table.update_item(
                Key={'player_id': player_id},
                UpdateExpression="SET wins = wins + :val, mmr = mmr + :mmr_change",
                ExpressionAttributeValues={':val': 1, ':mmr_change': 25} # Simple MMR change
            )
            if redis_client: redis_client.delete(f"player_cache:{player_id}")


        # Update losers
        for player_id in loser_team:
            table.update_item(
                Key={'player_id': player_id},
                UpdateExpression="SET losses = losses + :val, mmr = mmr - :mmr_change",
                ExpressionAttributeValues={':val': 1, ':mmr_change': 25}
            )
            if redis_client: redis_client.delete(f"player_cache:{player_id}")

        return jsonify({"status": f"Match {match_id} results recorded"}), 200
    except Exception as e:
        app.logger.error(f"Error updating match results: {e}")
        return jsonify({"error": "Could not update player stats"}), 500

# --- Server-Sent Events (SSE) Endpoint for real-time notifications ---
@app.route('/stream')
def stream():
    def event_stream():
        if not redis_client:
            app.logger.error("Redis not connected for SSE")
            return

        pubsub = redis_client.pubsub()
        pubsub.subscribe('match_notifications')
        app.logger.info("Client subscribed to SSE stream for 'match_notifications'")
        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = message['data']
                    app.logger.info(f"SSE sending message: {data}")
                    # SSE format is 'data: {json_string}\n\n'
                    yield f"data: {data}\n\n"
        except GeneratorExit:
            app.logger.info("Client disconnected from SSE stream.")
        finally:
            pubsub.close()

    return Response(event_stream(), mimetype='text/event-stream')


# --- Machine Learning Placeholder Endpoints ---

@app.route('/predict/churn/<string:player_id>', methods=['GET'])
def predict_churn(player_id):
    """
    Placeholder for player churn prediction.
    In a real application, this would query a deployed ML model.
    """
    # ML model logic would go here
    # For now, a dummy response
    is_likely_to_churn = (hash(player_id) % 10) < 2 # ~20% churn probability
    return jsonify({"player_id": player_id, "is_likely_to_churn": is_likely_to_churn})

@app.route('/detect/smurf', methods=['POST'])
def detect_smurf():
    """
    Placeholder for smurf detection.
    This would analyze player performance data.
    """
    player_data = request.get_json()
    # ML model logic here
    # Dummy response based on high actions per minute
    is_smurf = player_data.get('apm', 0) > 250 and player_data.get('matches_played', 100) < 20
    return jsonify({"player_id": player_data.get('player_id'), "is_smurf_candidate": is_smurf})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

