import React, { useState } from 'react';
import Matchmaking from './components/Matchmaking';
import PlayerStats from './components/PlayerStats';
import MatchSimulator from './components/MatchSimulator';
import RecentMatches from './components/RecentMatches';
import Queue from './components/Queue';
import Notifications from './components/Notifications';
import { MatchNotification } from './types'; // Import the type

function App() {
  // State for the match that was just found and needs to be simulated
  const [currentMatch, setCurrentMatch] = useState<MatchNotification | null>(null);

  // A callback function to update recent matches after a result is posted
  const [refreshRecentMatches, setRefreshRecentMatches] = useState<boolean>(false);

  const handleMatchResultPosted = () => {
    setCurrentMatch(null); // Clear the simulator
    setRefreshRecentMatches(prev => !prev); // Trigger a refresh in RecentMatches
  };

  return (
    <div className="bg-primary min-h-screen text-text-primary p-4 sm:p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="text-center">
          <h1 className="text-3xl sm:text-4xl font-bold">Intelligent Gaming Matchmaking Dashboard 🎮</h1>
          <p className="text-text-secondary mt-2">Manage your game's matchmaking queue and player data.</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Matchmaking />
            <PlayerStats />
            <MatchSimulator 
              match={currentMatch} 
              onResultPosted={handleMatchResultPosted} 
            />
            <RecentMatches refreshTrigger={refreshRecentMatches} />
          </div>

          <div className="lg:col-span-1 space-y-8">
            {/* The Queue needs to know when a match is found to refresh itself */}
            <Queue matchFound={!!currentMatch} />
            {/* Pass the setCurrentMatch function to Notifications so it can update the state */}
            <Notifications onMatchFound={setCurrentMatch} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;