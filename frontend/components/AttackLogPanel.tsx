"use client";

import { AttackLog } from '@/lib/types';

interface AttackLogPanelProps {
  logs: AttackLog[];
  currentPlayerId: number;
}

export default function AttackLogPanel({ logs, currentPlayerId }: AttackLogPanelProps) {
  if (logs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No attack logs yet. Go fight some battles!
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 text-left">Time</th>
              <th className="px-4 py-2 text-left">Attacker</th>
              <th className="px-4 py-2 text-left">Defender</th>
              <th className="px-4 py-2 text-left">Tile</th>
              <th className="px-4 py-2 text-left">Armies</th>
              <th className="px-4 py-2 text-left">Result</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => {
              const isAttacker = log.attacker_id === currentPlayerId;
              const isDefender = log.defender_id === currentPlayerId;
              const result = log.attacker_won
                ? (isAttacker ? 'Victory!' : 'Defeat')
                : (isAttacker ? 'Defeat' : 'Defense!');

              return (
                <tr
                  key={log.id}
                  className={`border-b hover:bg-gray-50 ${
                    isAttacker ? 'bg-blue-50' : isDefender ? 'bg-red-50' : ''
                  }`}
                >
                  <td className="px-4 py-3 text-sm">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <span className={isAttacker ? 'font-bold text-blue-600' : ''}>
                      {log.attacker_username}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={isDefender ? 'font-bold text-red-600' : ''}>
                      {log.defender_username}
                    </span>
                  </td>
                  <td className="px-4 py-3">({log.tile_x}, {log.tile_y})</td>
                  <td className="px-4 py-3 text-sm">
                    {log.attacker_army} vs {log.defender_army}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`font-bold ${
                        log.attacker_won === isAttacker
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {result}
                      {log.tile_captured && ' (Captured)'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
