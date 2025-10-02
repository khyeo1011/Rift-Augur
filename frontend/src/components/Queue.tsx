import React, { useState, useEffect } from 'react';
import { Player } from '../types';

const API_BASE_URL = 'http://localhost:5000';

interface QueueProps {
  matchFound: boolean;
}

function Queue({ matchFound }: QueueProps) {
  const [players, setPlayers] = useState<Player[]>([]);

  const updateQueueDisplay = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/queue/players`);
      const queuePlayers: Player[] = await response.json();
      setPlayers(queuePlayers);
    } catch (error) {
      console.error('Error updating queue display:', error);
    }
  };

  useEffect(() => {
    updateQueueDisplay(); // Initial fetch
    const interval = setInterval(updateQueueDisplay, 5000); // Poll every 5 seconds
    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  // Also refresh when a match is found (passed via prop)
  useEffect(() => {
    if (matchFound) {
      setTimeout(updateQueueDisplay, 500); // Give the server a moment to update the queue
    }
  }, [matchFound]);


  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Current Queue</h2>
      <div className="space-y-2 h-48 overflow-y-auto pr-2">
        {players.length > 0 ? (
          players.map(p => (
            <div key={p.player_id} className="text-sm">
              <strong>{p.player_id}</strong> (MMR: {p.mmr})
            </div>
          ))
        ) : (
          <p className="text-highlight text-sm">No players in queue.</p>
        )}
      </div>
    </div>
  );
}

export default Queue;