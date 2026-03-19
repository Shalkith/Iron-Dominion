"""TypeScript types for the game."""

export interface Player {
  id: number;
  username: string;
  gold: number;
  army_size: number;
  created_at: string;
}

export interface Tile {
  id: number;
  x: number;
  y: number;
  owner_id: number | null;
  resource_value: number;
  owner?: Player;
}

export interface AttackLog {
  id: number;
  attacker_id: number;
  defender_id: number;
  attacker_username: string;
  defender_username: string;
  tile_x: number;
  tile_y: number;
  attacker_army: number;
  defender_army: number;
  attacker_won: boolean;
  tile_captured: boolean;
  created_at: string;
}

export interface Alliance {
  id: number;
  player1_id: number;
  player2_id: number;
  player1_username: string;
  player2_username: string;
  created_at: string;
}

export interface AllianceRequest {
  id: number;
  from_player_id: number;
  to_player_id: number;
  from_username: string;
  to_username: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
}

export interface AttackResult {
  success: boolean;
  attacker_won: boolean;
  message: string;
  tile_captured: boolean;
}

export interface LeaderboardEntry {
  rank: number;
  player_id: number;
  username: string;
  gold: number;
  army_size: number;
  tiles_owned: number;
}
