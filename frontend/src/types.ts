export interface Player {
  player_id: string;
  mmr: number;
  wins: number;
  losses: number;
  character_preferences: string[];
}

export interface MatchNotification {
  match_id: string;
  team_a: string[];
  team_b: string[];
}

export interface RecentMatch {
    match_id: string;
    winner_team: string[];
    loser_team: string[];
    timestamp: string;
}