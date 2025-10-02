import React, { useState } from 'react';
import { Player } from '../types'; // Import the Player interface

const API_BASE_URL = 'http://localhost:5000';

function PlayerStats() {
  const [searchPlayerId, setSearchPlayerId] = useState<string>('');
  const [playerStats, setPlayerStats] = useState<Player | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGetPlayerStats = async () => {
    if (!searchPlayerId) {
      alert('Please enter a Player ID to search.');
      return;
    }
    setLoading(true);
    setError(null);
    setPlayerStats(null);
    try {
      const response = await fetch(`${API_BASE_URL}/player/${searchPlayerId}/stats`);
      if (!response.ok) {
        throw new Error('Player not found or server error');
      }
      const data: Player = await response.json();
      setPlayerStats(data);
    } catch (err) {
      setError(`Could not fetch stats for ${searchPlayerId}.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Player Stats</h2>
      {/* === MISSING UI ADDED HERE === */}
      <div className="flex space-x-4 mb-4">
        <input
          type="text"
          className="input"
          placeholder="Enter Player ID to search"
          value={searchPlayerId}
          onChange={(e) => setSearchPlayerId(e.target.value)}
          onKeyUp={(e) => e.key === 'Enter' && handleGetPlayerStats()}
        />
        <button onClick={handleGetPlayerStats} className="btn">Search</button>
      </div>
      <div className="p-4 bg-primary rounded-lg min-h-[100px]">
        {loading && <p className="text-highlight">Loading...</p>}
        {error && <p className="text-red-400">{error}</p>}
        {playerStats ? (
          <div>
            <h3 className="font-bold text-lg">{playerStats.player_id}</h3>
            <p><strong>MMR:</strong> {playerStats.mmr}</p>
            <p><strong>Wins:</strong> {playerStats.wins}</p>
            <p><strong>Losses:</strong> {playerStats.losses}</p>
            <p><strong>Preferred Characters:</strong> {playerStats.character_preferences.join(', ')}</p>
          </div>
        ) : (
          !loading && !error && <p className="text-highlight">Search for a player to see their stats.</p>
        )}
      </div>
    </div>
  );
}

export default PlayerStats;