import React, { useState, useEffect } from 'react';

interface Player {
  player_id: string;
  wins: number;
  losses: number;
  rank: string;
  character_preferences: string[];
}

const API_BASE_URL = 'http://localhost:5000';

function PlayerStats() {
  const [searchPlayerId, setSearchPlayerId] = useState<string>('');
  const [playerStats, setPlayerStats] = useState<Player | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<Player[]>([]);

  useEffect(() => {
    if (searchPlayerId.length > 2) {
      const fetchSuggestions = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/players?prefix=${searchPlayerId}`);
          if (response.ok) {
            const data: Player[] = await response.json();
            setSuggestions(data);
          }
        } catch (err) {
          // Handle error silently
        }
      };
      fetchSuggestions();
    } else {
      setSuggestions([]);
    }
  }, [searchPlayerId]);

  const handleGetPlayerStats = async (playerId: string) => {
    setLoading(true);
    setError(null);
    setPlayerStats(null);
    setSuggestions([]);
    setSearchPlayerId(playerId);
    try {
      const response = await fetch(`${API_BASE_URL}/player/${playerId}/stats`);
      if (!response.ok) {
        throw new Error('Player not found or server error');
      }
      const data: Player = await response.json();
      setPlayerStats(data);
    } catch (err) {
      setError(`Could not fetch stats for ${playerId}.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Player Stats</h2>
      <div className="flex space-x-4 mb-4">
        <div className="relative w-full">
          <input
            type="text"
            className="input"
            placeholder="Enter Player ID to search"
            value={searchPlayerId}
            onChange={(e) => setSearchPlayerId(e.target.value)}
          />
          {suggestions.length > 0 && (
            <ul className="absolute z-10 w-full bg-secondary border border-primary rounded-md mt-1">
              {suggestions.map((player) => (
                <li
                  key={player.player_id}
                  className="p-2 hover:bg-primary cursor-pointer"
                  onClick={() => handleGetPlayerStats(player.player_id)}
                >
                  {player.player_id}
                </li>
              ))}
            </ul>
          )}
        </div>
        <button onClick={() => handleGetPlayerStats(searchPlayerId)} className="btn">Search</button>
      </div>
      <div className="p-4 bg-primary rounded-lg min-h-[100px]">
        {loading && <p className="text-highlight">Loading...</p>}
        {error && <p className="text-red-400">{error}</p>}
        {playerStats ? (
          <div>
            <h3 className="font-bold text-lg">{playerStats.player_id}</h3>
            <p><strong>Rank:</strong> {playerStats.rank}</p>
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