import React from 'react';
import PlayerStats from './components/PlayerStats';
import MatchPredictor from './components/MatchPredictor';
import AddPlayer from './components/AddPlayer';
import EditPlayer from './components/EditPlayer';

function App() {
  return (
    <div className="bg-primary min-h-screen text-text-primary p-4 sm:p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="text-center">
          <h1 className="text-3xl sm:text-4xl font-bold">Rift Augur</h1>
          <p className="text-text-secondary mt-2">Predict the outcome of your next match.</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <MatchPredictor />
            <PlayerStats />
          </div>

          <div className="lg:col-span-1 space-y-8">
            <AddPlayer />
            <EditPlayer />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
