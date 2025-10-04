import React, { useState } from 'react';

const MatchPredictor: React.FC = () => {
  const [teamA, setTeamA] = useState('');
  const [teamB, setTeamB] = useState('');
  const [prediction, setPrediction] = useState<any>(null);

  const handlePredict = async () => {
    const teamAPlayers = teamA.split('\n').filter(p => p.trim() !== '');
    const teamBPlayers = teamB.split('\n').filter(p => p.trim() !== '');

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ team_a: teamAPlayers, team_b: teamBPlayers }),
      });
      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error('Error fetching prediction:', error);
    }
  };

  return (
    <div className="bg-secondary p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Match Predictor</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <h3 className="text-lg font-semibold mb-2">Team A</h3>
          <textarea
            className="w-full h-40 bg-primary text-text-primary p-2 rounded-md"
            value={teamA}
            onChange={(e) => setTeamA(e.target.value)}
            placeholder="Enter player IDs, one per line"
          />
        </div>
        <div>
          <h3 className="text-lg font-semibold mb-2">Team B</h3>
          <textarea
            className="w-full h-40 bg-primary text-text-primary p-2 rounded-md"
            value={teamB}
            onChange={(e) => setTeamB(e.target.value)}
            placeholder="Enter player IDs, one per line"
          />
        </div>
      </div>
      <button
        className="w-full bg-accent text-white font-bold py-2 px-4 rounded-md hover:bg-accent-dark transition duration-300"
        onClick={handlePredict}
      >
        Predict Winner
      </button>
      {prediction && (
        <div className="mt-4 p-4 bg-primary rounded-md">
          <h3 className="text-xl font-bold">Prediction Result</h3>
          <p><strong>Team A Win Probability:</strong> {(prediction.team_a_win_prob * 100).toFixed(2)}%</p>
          <p><strong>Team B Win Probability:</strong> {(prediction.team_b_win_prob * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
};

export default MatchPredictor;
