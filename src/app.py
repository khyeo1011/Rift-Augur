from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import redis
import boto3
from botocore.exceptions import ClientError
import uuid
import json
import os
from datetime import datetime

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # --- Configuration ---
    app.config.from_mapping(
        REDIS_HOST=os.environ.get("REDIS_HOST", "localhost"),
        REDIS_PORT=int(os.environ.get("REDIS_PORT", 6379)),
        DYNAMODB_ENDPOINT=os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000"),
        AWS_REGION="us-west-2",
        MATCH_SIZE=10  # Number of players required for a match
    )

    # --- Service Connections ---
    try:
        redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=0,
            decode_responses=True
        )
        redis_client.ping()  # Check the connection
        app.logger.info("Successfully connected to Redis.")
    except redis.exceptions.ConnectionError as e:
        app.logger.error(f"Could not connect to Redis: {e}")
        redis_client = None

    try:
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=app.config['DYNAMODB_ENDPOINT'],
            region_name=app.config['AWS_REGION'],
            aws_access_key_id='fakeMyKeyId',
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
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                app.logger.info("DynamoDB table 'PlayerProfiles' already exists.")
            else:
                raise
    except Exception as e:
        app.logger.error(f"Could not connect to DynamoDB: {e}")
        dynamodb = None

    # --- Helper Functions ---
    def find_match():
        """
        More robust matchmaking logic for 10 players.
        """
        queue_name = 'matchmaking_queue'
        if not redis_client:
            return None

        if redis_client.zcard(queue_name) >= app.config['MATCH_SIZE']:
            players_to_match = redis_client.zrange(queue_name, 0, app.config['MATCH_SIZE'] - 1)
            if players_to_match:
                match_id = str(uuid.uuid4())
                team_a = players_to_match[:5]
                team_b = players_to_match[5:]
                app.logger.info(f"Match found! ID: {match_id} with Team A: {team_a} and Team B: {team_b}")
                redis_client.zrem(queue_name, *players_to_match)
                match_details = {"match_id": match_id, "team_a": team_a, "team_b": team_b}
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
        if not data or 'player_id' not in data:
            return jsonify({"error": "player_id is required"}), 400

        player_id = data['player_id']
        mmr = data.get('mmr', 1000)

        if not isinstance(mmr, int):
            return jsonify({"error": "mmr must be an integer"}), 400
        if not redis_client or not dynamodb:
            return jsonify({"error": "A database connection is not available"}), 503

        try:
            table = dynamodb.Table('PlayerProfiles')
            # Create a new player profile if it doesn't exist.
            try:
                table.put_item(
                    Item={
                        'player_id': player_id,
                        'mmr': mmr,
                        'wins': 0,
                        'losses': 0,
                        'character_preferences': ['DefaultChar']
                    },
                    ConditionExpression='attribute_not_exists(player_id)'
                )
                app.logger.info(f"Created new player profile for {player_id}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    # Player already exists, update their MMR for matchmaking.
                    table.update_item(Key={'player_id': player_id}, UpdateExpression="SET mmr = :m", ExpressionAttributeValues={':m': mmr})
                    app.logger.info(f"Updated MMR for existing player {player_id}")
                else:
                    raise

            # Add player to the Redis queue
            redis_client.zadd('matchmaking_queue', {player_id: mmr})
            app.logger.info(f"Player {player_id} added to queue with MMR {mmr}")
            find_match()
            return jsonify({"status": f"player {player_id} added to queue"}), 200
        except Exception as e:
            app.logger.error(f"Error adding to queue: {e}")
            return jsonify({"error": "Could not add player to queue"}), 500

    @app.route('/queue/players', methods=['GET'])
    def get_queue_players():
        """Gets all players currently in the matchmaking queue."""
        if not redis_client:
            return jsonify({"error": "Redis connection not available"}), 503

        try:
            players = redis_client.zrange('matchmaking_queue', 0, -1, withscores=True)
            return jsonify([{"player_id": p[0], "mmr": int(p[1])} for p in players])
        except Exception as e:
            app.logger.error(f"Error getting queue players: {e}")
            return jsonify({"error": "Could not retrieve queue players"}), 500

    @app.route('/players', methods=['GET'])
    def get_all_players():
        """Gets all players from the database."""
        if not dynamodb:
            return jsonify({"error": "DynamoDB connection not available"}), 503

        table = dynamodb.Table('PlayerProfiles')
        try:
            response = table.scan()
            return jsonify(response.get('Items', []))
        except ClientError as e:
            app.logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
            return jsonify({"error": "Could not retrieve players"}), 500

    @app.route('/player/<string:player_id>/stats', methods=['GET'])
    def get_player_stats(player_id):
        """Retrieves a player's profile and stats from DynamoDB."""
        if not dynamodb:
            return jsonify({"error": "DynamoDB connection not available"}), 503

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
                if redis_client:
                    redis_client.setex(f"player_cache:{player_id}", 300, json.dumps(response['Item']))
                return jsonify(response['Item']), 200
            else:
                new_player = {
                    'player_id': player_id,
                    'mmr': 1000,
                    'wins': 0,
                    'losses': 0,
                    'character_preferences': ['DefaultChar']
                }
                table.put_item(Item=new_player)
                return jsonify(new_player), 201
        except ClientError as e:
            app.logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
            return jsonify({"error": "Could not retrieve player stats"}), 500

    @app.route('/matches/recent', methods=['GET'])
    def get_recent_matches():
        """Gets the last 10 matches from Redis."""
        if not redis_client:
            return jsonify({"error": "Redis connection not available"}), 503
        try:
            matches_json = redis_client.lrange('recent_matches', 0, 9)
            matches = [json.loads(m) for m in matches_json]
            return jsonify(matches)
        except Exception as e:
            app.logger.error(f"Error getting recent matches: {e}")
            return jsonify({"error": "Could not retrieve recent matches"}), 500

    @app.route('/matches/<string:match_id>/results', methods=['POST'])
    def post_match_results(match_id):
        """Updates player stats after a match."""
        data = request.get_json()
        if not data or 'winner_team' not in data or 'loser_team' not in data:
            return jsonify({"error": "winner_team and loser_team must be provided"}), 400

        winner_team = data['winner_team']
        loser_team = data['loser_team']

        if not dynamodb:
            return jsonify({"error": "DynamoDB connection not available"}), 503

        table = dynamodb.Table('PlayerProfiles')
        try:
            # Update winners and losers
            for player_id in winner_team:
                table.update_item(Key={'player_id': player_id}, UpdateExpression="SET wins = wins + :v, mmr = mmr + :c", ExpressionAttributeValues={':v': 1, ':c': 25})
                if redis_client: redis_client.delete(f"player_cache:{player_id}")
            for player_id in loser_team:
                table.update_item(Key={'player_id': player_id}, UpdateExpression="SET losses = losses + :v, mmr = mmr - :c", ExpressionAttributeValues={':v': 1, ':c': 25})
                if redis_client: redis_client.delete(f"player_cache:{player_id}")
            
            # Store match result in Redis for recent matches list
            if redis_client:
                match_result = {
                    "match_id": match_id,
                    "winner_team": winner_team,
                    "loser_team": loser_team,
                    "timestamp": datetime.utcnow().isoformat()
                }
                redis_client.lpush('recent_matches', json.dumps(match_result))
                redis_client.ltrim('recent_matches', 0, 9) # Keep only the last 10 matches

            return jsonify({"status": f"Match {match_id} results recorded"}), 200
        except ClientError as e:
            app.logger.error(f"Error updating match results: {e.response['Error']['Message']}")
            return jsonify({"error": "Could not update player stats"}), 500

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
                        yield f"data: {data}\n\n"
            except GeneratorExit:
                app.logger.info("Client disconnected from SSE stream.")
            finally:
                pubsub.close()

        return Response(event_stream(), mimetype='text/event-stream')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)