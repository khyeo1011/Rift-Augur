import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5000';

interface Player {
  player_id: string;
  wins: number;
  losses: number;
  rank: string;
  character_preferences: string[];
}

const EditPlayer: React.FC = () => {
  const [playerId, setPlayerId] = useState('');
  const [rank, setRank] = useState('Bronze');
  const [division, setDivision] = useState('I');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<Player[]>([]);

  useEffect(() => {
    if (playerId.length > 2) {
      const fetchSuggestions = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/players?prefix=${playerId}`);
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
  }, [playerId]);

  const handleEditPlayer = async () => {
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_BASE_URL}/players`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_id: playerId, rank: `${rank} ${division}` }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to edit player');
      }

      setSuccess(`Player ${playerId} updated successfully.`);
      setPlayerId('');
      setRank('Bronze');
      setDivision('I');
      setSuggestions([]);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="bg-secondary p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Edit Player</h2>
      <div className="flex flex-col space-y-4">
        <div className="relative w-full">
          <input
            type="text"
            className="input"
            placeholder="Enter Player ID"
            value={playerId}
            onChange={(e) => setPlayerId(e.target.value)}
          />
          {suggestions.length > 0 && (
            <ul className="absolute z-10 w-full bg-primary border border-secondary rounded-md mt-1">
              {suggestions.map((player) => (
                <li
                  key={player.player_id}
                  className="p-2 hover:bg-secondary cursor-pointer"
                  onClick={() => {
                    setPlayerId(player.player_id);
                    setSuggestions([]);
                  }}
                >
                  {player.player_id}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="flex space-x-4">
          <select
            className="input w-1/2"
            value={rank}
            onChange={(e) => setRank(e.target.value)}
          >
            <option value="Iron">Iron</option>
            <option value="Bronze">Bronze</option>
            <option value="Silver">Silver</option>
            <option value="Gold">Gold</option>
            <option value="Platinum">Platinum</option>
            <option value="Diamond">Diamond</option>
            <option value="Master">Master</option>
            <option value="Grandmaster">Grandmaster</option>
            <option value="Challenger">Challenger</option>
          </select>
          <select
            className="input w-1/2"
            value={division}
            onChange={(e) => setDivision(e.target.value)}
          >
            <option value="I">I</option>
            <option value="II">II</option>
            <option value="III">III</option>
            <option value="IV">IV</option>
          </select>
        </div>
        <button onClick={handleEditPlayer} className="btn">Edit Player</button>
        {error && <p className="text-red-400">{error}</p>}
        {success && <p className="text-green-400">{success}</p>}
      </div>
    </div>
  );
};

export default EditPlayer;