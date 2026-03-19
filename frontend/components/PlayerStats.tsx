"use client";

import { Player, Tile } from '@/lib/types';

interface PlayerStatsProps {
  player: Player;
  myTiles: Tile[];
}

export default function PlayerStats({ player, myTiles }: PlayerStatsProps) {
  const totalResourceValue = myTiles.reduce((sum, tile) => sum + tile.resource_value, 0);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
          <div className="text-2xl font-bold text-yellow-700">{player.gold}</div>
          <div className="text-sm text-yellow-600">Gold</div>
        </div>

        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-700">{player.army_size}</div>
          <div className="text-sm text-blue-600">Army Size</div>
        </div>

        <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-700">{myTiles.length}</div>
          <div className="text-sm text-green-600">Tiles Owned</div>
        </div>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-bold mb-4">Resource Generation</h3>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Gold per tick:</span>
            <span className="font-bold">{totalResourceValue}</span>
          </div>
          <div className="flex justify-between">
            <span>Gold per minute:</span>
            <span className="font-bold">{totalResourceValue * 6}</span>
          </div>
        </div>
      </div>

      {myTiles.length > 0 && (
        <div>
          <h3 className="font-bold mb-4">Your Tiles</h3>
          <div className="max-h-96 overflow-y-auto border rounded">
            <table className="w-full">
              <thead className="bg-gray-100 sticky top-0">
                <tr>
                  <th className="px-4 py-2 text-left">Position</th>
                  <th className="px-4 py-2 text-left">Resource</th>
                </tr>
              </thead>
              <tbody>
                {myTiles.map((tile) => (
                  <tr key={tile.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">({tile.x}, {tile.y})</td>
                    <td className="px-4 py-2">{tile.resource_value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
