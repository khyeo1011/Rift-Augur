import React, { useState, useEffect } from 'react';
import { MatchNotification } from '../types';

const API_BASE_URL = 'http://localhost:5000';

interface NotificationsProps {
  onMatchFound: (match: MatchNotification) => void;
}

function Notifications({ onMatchFound }: NotificationsProps) {
  const [logs, setLogs] = useState<string[]>(['Waiting for server events...']);

  useEffect(() => {
    const logNotification = (message: string) => {
      const time = new Date().toLocaleTimeString();
      setLogs(prevLogs => [`[${time}] ${message}`, ...prevLogs.filter(log => log !== 'Waiting for server events...')]);
    };

    const eventSource = new EventSource(`${API_BASE_URL}/stream`);

    eventSource.onopen = () => logNotification('Connected to server for real-time events.');

    eventSource.onmessage = (event) => {
      try {
        const data: MatchNotification = JSON.parse(event.data);
        if (data.match_id) {
          const message = `Match Found! ID: ${data.match_id}`;
          logNotification(message);
          onMatchFound(data); // Lift the state up to App.tsx
        }
      } catch (error) {
        console.error("Error parsing SSE message:", error);
      }
    };

    eventSource.onerror = () => {
      logNotification('Connection to server lost. Retrying...');
      eventSource.close();
    };

    return () => {
      eventSource.close(); // Clean up the connection when the component unmounts
    };
  }, [onMatchFound]);

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">Real-time Notifications</h2>
      <div className="space-y-3 h-96 overflow-y-auto pr-2">
        {logs.map((log, index) => (
          <div key={index} className="notification text-sm text-text-secondary">
            {log}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Notifications;