"use client";

import { LeaderboardEntry } from '@/lib/types';

interface LeaderboardProps {
  entries: LeaderboardEntry[];
  currentPlayerId: number;
}

export default function Leaderboard({ entries, currentPlayerId }: LeaderboardProps) {
  if (entries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">No players yet.</div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 text-left">Rank</th>
              <th className="px-4 py-2 text-left">Player</th>
              <th className="px-4 py-2 text-right">Gold</th>
              <th className="px-4 py-2 text-right">Army</th>
              <th className="px-4 py-2 text-right">Tiles</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr
                key={entry.player_id}
                className={`border-b hover:bg-gray-50 ${
                  entry.player_id === currentPlayerId ? 'bg-blue-50 font-medium' : ''
                }`}
              >
                <td className="px-4 py-3">
                  {entry.rank === 1 && '🥇'}
                  {entry.rank === 2 && '🥈'}
                  {entry.rank === 3 && '🥉'}
                  {entry.rank > 3 && entry.rank}
                </td>
                <td className="px-4 py-3">
                  {entry.username}
                  {entry.player_id === currentPlayerId && (
                    <span className="ml-2 text-xs text-blue-600">(You)</span>
                  )}
                </td>
                <td className="px-4 py-3 text-right font-bold text-yellow-600">
                  {entry.gold.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right">{entry.army_size}</td>
                <td className="px-4 py-3 text-right">{entry.tiles_owned}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
