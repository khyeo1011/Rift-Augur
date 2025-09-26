# Rift Augur: League of Legends Edition

Rift Augur is a backend platform tailored for League of Legends, providing intelligent matchmaking, player analytics, and real-time notifications. It is designed to enhance the player experience by leveraging advanced data analysis and scalable infrastructure, specifically for the League of Legends ecosystem.

## Features

- **RESTful API:** Clean, well-documented endpoints for League of Legends clients, bots, or companion apps.
- **Intelligent Matchmaking:** Goes beyond simple MMR, using League-specific stats (rank, role, champion pool, win-rate, etc.) to create balanced matches.
  - *Future Work:* Incorporate tilt detection, champion mastery, and toxicity scores.
- **Player Analytics:** Track Summoner performance, champion stats, and match history.
  - *Future Work:* Churn prediction, smurf detection, and role proficiency analysis.
- **Real-time Notifications:** Instantly notify users of match found, queue status, or performance milestones.
- **Scalable Architecture:** Built with DynamoDB and Redis for high throughput and low latency.
- **Containerized:** Dockerized for easy deployment and scaling.

## Architecture

- **Flask (Python):** Core REST API for League of Legends data and matchmaking.
- **DynamoDB:** Stores Summoner profiles, match history, and champion stats.
- **Redis:** 
  - **Matchmaking Queue:** Sorted set for players waiting for a match.
  - **Caching:** Frequently accessed Summoner and match data.
  - **Pub/Sub:** Real-time notifications (e.g., "Match Found").
- **Docker:** Orchestrated with docker-compose for local and cloud deployment.

## API Documentation

### Matchmaking

**POST** `/queue`

- Adds a Summoner to the matchmaking queue.
- **Body:**
  ```json
  { "summoner_name": "string", "summoner_id" : "string", "rank": "string", "role": "string", "champion_pool": ["Ahri", "Lee Sin"], "mmr": integer }
  ```
- **Response:**
  ```json
  { "status": "added to queue" }
  ```

### Player Stats

**GET** `/summoner/{summoner_name}/stats`

- Retrieves a Summoner's profile, champion stats, and match history.
- **Response:**
  ```json
  { "summoner_name": "string", "stats": { ... }, "champion_stats": { ... }, "recent_matches": [ ... ] }
  ```

### Match Results

**POST** `/matches/{match_id}/results`

- Reports the outcome of a League of Legends match.
- **Body:**
  ```json
  {
    "winning_team": ["summoner1", "summoner2", "summoner3", "summoner4", "summoner5"],
    "losing_team": ["summoner6", "summoner7", "summoner8", "summoner9", "summoner10"],
    "mvp": "summoner3"
  }
  ```
- **Response:**
  ```json
  { "status": "results recorded" }
  ```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

Clone the repository:

```sh
git clone https://github.com/khyeo1011/rift-augur.git
cd rift-augur
```

Build and run the services:

```sh
docker-compose up --build
```

The Flask app will be available at [http://localhost:5000](http://localhost:5000).

### Using the Frontend Dashboard

A simple frontend is provided in `index.html`.

After running `docker-compose up --build`, open the `index.html` file directly in your web browser.

Use the dashboard to:

- **Join the Queue:** Enter Summoner Name, Rank, Role, and Champion Pool to join matchmaking.
- **View Player Stats:** Enter a Summoner Name to view their League stats and match history.
- **See Real-time Notifications:** Watch for "Match Found" and other events.
- **Simulate Match Results:** After a match is found, simulate results and update Summoner stats.

## League of Legends-Specific Analytics

### Smarter Matchmaking

- **Goal:** Predict match quality using League-specific features.
- **Features:** Rank, role, champion mastery, recent win-rate, tilt detection, toxicity score.
- **Model:** To be determined (e.g., ensemble models, clustering).

### Player Churn Prediction

- **Goal:** Predict if a Summoner is likely to stop playing.
- **Features:** Match frequency, win/loss streaks, role changes, in-game reports.
- **Model:** To be determined (e.g., classification).

### Smurf Detection

- **Goal:** Identify new accounts with high skill.
- **Features:** KDA, CS per minute, champion pool diversity, early game performance.
- **Model:** To be determined (e.g., anomaly detection).

---

*Rift Augur is not affiliated with Riot Games or League of Legends. This project is for educational and demonstration purposes only.*