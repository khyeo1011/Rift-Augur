import React, { useState, useEffect } from 'react';
import { Player } from '../types'; // Import the Player interface

const API_BASE_URL = 'http://localhost:5000';

function Matchmaking() {
  const [playerId, setPlayerId] = useState<string>('');
  const [mmr, setMmr] = useState<string>('');
  const [existingPlayers, setExistingPlayers] = useState<Player[]>([]);

  useEffect(() => {
    const populateExistingPlayers = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/players`);
        const players: Player[] = await response.json();
        setExistingPlayers(players);
      } catch (error) {
        console.error('Error fetching existing players:', error);
      }
    };
    populateExistingPlayers();
  }, []);

  const handleJoinQueue = async () => {
    if (!playerId) {
      alert('Please enter a Player ID.');
      return;
    }

    try {
      await fetch(`${API_BASE_URL}/queue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_id: playerId,
          mmr: mmr ? parseInt(mmr, 10) : 1000
        }),
      });
      // Clear inputs after joining
      setPlayerId('');
      setMmr('');
      // You could add a success notification here
    } catch (error) {
      console.error('Error joining queue:', error);
      // You could add an error notification here
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Matchmaking</h2>
      <div className="space-y-4">
        {/* === MISSING UI ADDED HERE === */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="player-id" className="block text-sm font-medium text-highlight mb-1">Player ID</label>
            <input
              type="text"
              id="player-id"
              className="input"
              placeholder="e.g., player_123"
              value={playerId}
              onChange={(e) => setPlayerId(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="mmr" className="block text-sm font-medium text-highlight mb-1">MMR (defaults to 1000)</label>
            <input
              type="number"
              id="mmr"
              className="input"
              placeholder="e.g., 1500"
              value={mmr}
              onChange={(e) => setMmr(e.target.value)}
            />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={handleJoinQueue} className="btn">Join Queue</button>
          <div>
            <label htmlFor="existing-players" className="block text-sm font-medium text-highlight mb-1">Or select existing player</label>
            <select
              id="existing-players"
              className="input"
              value={playerId}
              onChange={(e) => setPlayerId(e.target.value)}
            >
              <option value="">-- Select Player --</option>
              {existingPlayers.map(player => (
                <option key={player.player_id} value={player.player_id}>
                  {player.player_id}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Matchmaking;