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



    # --- API Endpoints ---
    @app.route('/')
    def index():
        return jsonify({"message": "Rift Augur is running!"})



    @app.route('/players', methods=['GET', 'POST', 'PUT'])
    def handle_players():
        if request.method == 'POST':
            data = request.get_json()
            if not data or 'player_id' not in data or 'rank' not in data:
                return jsonify({"error": "player_id and rank are required"}), 400

            player_id = data['player_id']
            rank = data['rank']

            if not dynamodb:
                return jsonify({"error": "DynamoDB connection not available"}), 503

            table = dynamodb.Table('PlayerProfiles')
            try:
                table.put_item(
                    Item={
                        'player_id': player_id,
                        'rank': rank,
                        'wins': 0,
                        'losses': 0,
                        'character_preferences': ['DefaultChar']
                    },
                    ConditionExpression='attribute_not_exists(player_id)'
                )
                return jsonify({"status": f"player {player_id} added"}), 201
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    return jsonify({"error": f"Player {player_id} already exists"}), 409
                else:
                    app.logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
                    return jsonify({"error": "Could not add player"}), 500
        elif request.method == 'PUT':
            data = request.get_json()
            if not data or 'player_id' not in data or 'rank' not in data:
                return jsonify({"error": "player_id and rank are required"}), 400

            player_id = data['player_id']
            rank = data['rank']

            if not dynamodb:
                return jsonify({"error": "DynamoDB connection not available"}), 503

            table = dynamodb.Table('PlayerProfiles')
            try:
                table.update_item(
                    Key={'player_id': player_id},
                    UpdateExpression="SET #r = :rank",
                    ExpressionAttributeNames={'#r': 'rank'},
                    ExpressionAttributeValues={':rank': rank},
                    ConditionExpression='attribute_exists(player_id)'
                )
                return jsonify({"status": f"player {player_id} updated"}), 200
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    return jsonify({"error": f"Player {player_id} not found"}), 404
                else:
                    app.logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
                    return jsonify({"error": "Could not update player"}), 500
        else: # GET request
            prefix = request.args.get('prefix')
            if not dynamodb:
                return jsonify({"error": "DynamoDB connection not available"}), 503

            table = dynamodb.Table('PlayerProfiles')
            try:
                if prefix:
                    response = table.scan(
                        FilterExpression=boto3.dynamodb.conditions.Attr('player_id').begins_with(prefix)
                    )
                else:
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

        table = dynamodb.Table('PlayerProfiles')
        try:
            response = table.get_item(Key={'player_id': player_id})
            if 'Item' in response:
                return jsonify(response['Item']), 200
            else:
                return jsonify({"error": "Player not found"}), 404
        except ClientError as e:
            app.logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
            return jsonify({"error": "Could not retrieve player stats"}), 500







    @app.route('/predict', methods=['POST'])
    def predict_winner():
        """Predicts the winner of a match based on average team rank."""
        data = request.get_json()
        if not data or 'team_a' not in data or 'team_b' not in data:
            return jsonify({"error": "team_a and team_b must be provided"}), 400

        team_a = data['team_a']
        team_b = data['team_b']

        if not dynamodb:
            return jsonify({"error": "DynamoDB connection not available"}), 503

        table = dynamodb.Table('PlayerProfiles')

        rank_map = {
            "Iron": 0,
            "Bronze": 1,
            "Silver": 2,
            "Gold": 3,
            "Platinum": 4,
            "Diamond": 5,
            "Master": 6,
            "Grandmaster": 7,
            "Challenger": 8
        }

        division_map = {
            "I": 3,
            "II": 2,
            "III": 1,
            "IV": 0
        }

        def get_team_avg_rank(team):
            total_rank = 0
            for player_id in team:
                try:
                    response = table.get_item(Key={'player_id': player_id})
                    if 'Item' in response:
                        player_rank_str = response['Item'].get('rank', 'Bronze IV')
                        parts = player_rank_str.split()
                        rank = parts[0]
                        division = parts[1] if len(parts) > 1 else ''
                        rank_score = rank_map.get(rank, 1) * 4
                        division_score = division_map.get(division, 0)
                        total_rank += rank_score + division_score
                    else:
                        total_rank += 1 * 4 + 0 # Assume Bronze IV for players not in the database
                except ClientError as e:
                    app.logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
                    total_rank += 1 * 4 + 0 # Assume Bronze IV on error
            return total_rank / len(team) if team else 0

        avg_rank_a = get_team_avg_rank(team_a)
        avg_rank_b = get_team_avg_rank(team_b)

        # Calculate win probability using the logistic function
        k = 0.1 # Factor to control the steepness of the curve
        prob_a = 1 / (1 + 10**(-k * (avg_rank_a - avg_rank_b)))
        prob_b = 1 - prob_a

        return jsonify({"team_a_win_prob": prob_a, "team_b_win_prob": prob_b})



    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)