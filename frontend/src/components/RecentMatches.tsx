import React, { useState, useEffect } from 'react';
import { RecentMatch } from '../types';

const API_BASE_URL = 'http://localhost:5000';

interface RecentMatchesProps {
  refreshTrigger: boolean;
}

function RecentMatches({ refreshTrigger }: RecentMatchesProps) {
  const [matches, setMatches] = useState<RecentMatch[]>([]);

  useEffect(() => {
    const fetchRecentMatches = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/matches/recent`);
        const recentMatches: RecentMatch[] = await response.json();
        setMatches(recentMatches);
      } catch (error) {
        console.error('Error fetching recent matches:', error);
      }
    };

    fetchRecentMatches();
  }, [refreshTrigger]); // Refreshes when the trigger changes

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Recent Matches</h2>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {matches.length > 0 ? (
          matches.map(match => (
            <div key={match.match_id} className="p-2 bg-primary rounded">
              <p className="text-sm font-bold text-green-400">WINNERS: {match.winner_team.join(', ')}</p>
              <p className="text-sm text-red-400">LOSERS: {match.loser_team.join(', ')}</p>
            </div>
          ))
        ) : (
          <p className="text-highlight">No recent matches to display.</p>
        )}
      </div>
    </div>
  );
}

export default RecentMatches;