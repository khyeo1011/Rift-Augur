import React from 'react';
import { MatchNotification } from '../types';

const API_BASE_URL = 'http://localhost:5000';

interface MatchSimulatorProps {
  match: MatchNotification | null;
  onResultPosted: () => void;
}

function MatchSimulator({ match, onResultPosted }: MatchSimulatorProps) {
  
  const reportMatchResult = async (winnerTeam: string[], loserTeam: string[]) => {
    if (!match) return;

    try {
      await fetch(`${API_BASE_URL}/matches/${match.match_id}/results`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ winner_team: winnerTeam, loser_team: loserTeam }),
      });
      onResultPosted(); // Notify parent that the result was posted
    } catch (error) {
      console.error('Error reporting match result:', error);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Match Simulator</h2>
      <p className="text-highlight mb-4">Simulate a match result. Use player IDs from a 'Match Found' notification.</p>
      <div className="space-y-4">
        {!match ? (
          <p className="text-highlight">Waiting for a match to be found...</p>
        ) : (
          <div>
            <div>
              <h4 className="font-bold">Team A</h4>
              <p>{match.team_a.join(', ')}</p>
            </div>
            <div className="mt-2">
              <h4 className="font-bold">Team B</h4>
              <p>{match.team_b.join(', ')}</p>
            </div>
            <div className="flex flex-wrap gap-4 mt-4">
              <button className="btn btn-sm" onClick={() => reportMatchResult(match.team_a, match.team_b)}>Team A Wins</button>
              <button className="btn btn-sm" onClick={() => reportMatchResult(match.team_b, match.team_a)}>Team B Wins</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MatchSimulator;