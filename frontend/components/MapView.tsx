"use client";

import { useState, useMemo } from 'react';
import { Tile } from '@/lib/types';

interface MapViewProps {
  tiles: Tile[];
  currentPlayerId: number;
  onClaim: (x: number, y: number) => void;
  onAttack: (x: number, y: number) => void;
}

const MAP_SIZE = 50;

export default function MapView({ tiles, currentPlayerId, onClaim, onAttack }: MapViewProps) {
  const [selectedTile, setSelectedTile] = useState<Tile | null>(null);
  const [viewOffset, setViewOffset] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);

  // Create a lookup map for tiles
  const tileMap = useMemo(() => {
    const map = new Map<string, Tile>();
    tiles.forEach((tile) => {
      map.set(`${tile.x},${tile.y}`, tile);
    });
    return map;
  }, [tiles]);

  // Get player's tiles for adjacency check
  const playerTiles = useMemo(() => {
    return tiles.filter((t) => t.owner_id === currentPlayerId);
  }, [tiles, currentPlayerId]);

  // Check if a tile is adjacent to player's territory
  const isAdjacentToPlayer = (x: number, y: number) => {
    return playerTiles.some((tile) =>
      Math.abs(tile.x - x) <= 1 && Math.abs(tile.y - y) <= 1
    );
  };

  const getTileClass = (tile: Tile | undefined) => {
    if (!tile || !tile.owner_id) return 'bg-gray-400';
    if (tile.owner_id === currentPlayerId) return 'bg-blue-500';
    return 'bg-red-500';
  };

  const handleTileClick = (tile: Tile | undefined, x: number, y: number) => {
    if (!tile) {
      // Check if we can claim this spot
      if (playerTiles.length === 0 || isAdjacentToPlayer(x, y)) {
        onClaim(x, y);
      }
      return;
    }

    setSelectedTile(tile);

    if (tile.owner_id === currentPlayerId) {
      // Own tile - maybe show info
    } else if (tile.owner_id === null) {
      // Unclaimed - claim if adjacent
      if (isAdjacentToPlayer(x, y)) {
        onClaim(x, y);
      }
    } else {
      // Enemy tile - attack if adjacent
      if (isAdjacentToPlayer(x, y)) {
        onAttack(x, y);
      }
    }
  };

  // Calculate visible range based on zoom and offset
  const visibleSize = Math.floor(20 / zoom);
  const startX = Math.max(0, viewOffset.x);
  const startY = Math.max(0, viewOffset.y);
  const endX = Math.min(MAP_SIZE, startX + visibleSize);
  const endY = Math.min(MAP_SIZE, startY + visibleSize);

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Zoom:</span>
          <input
            type="range"
            min="0.5"
            max="2"
            step="0.25"
            value={zoom}
            onChange={(e) => setZoom(parseFloat(e.target.value))}
            className="w-32"
          />
          <span className="text-sm">{Math.round(zoom * 100)}%</span>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-blue-500 rounded"></div>
            <span>Your Tiles</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span>Enemy</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gray-400 rounded"></div>
            <span>Neutral</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-2">
        <button
          onClick={() => setViewOffset((prev) => ({ ...prev, y: Math.max(0, prev.y - 5) }))}
          className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >
          ↑
        </button>
        <button
          onClick={() => setViewOffset((prev) => ({ ...prev, y: Math.min(MAP_SIZE - visibleSize, prev.y + 5) }))}
          className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >
          ↓
        </button>
        <button
          onClick={() => setViewOffset((prev) => ({ ...prev, x: Math.max(0, prev.x - 5) }))}
          className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >
          ←
        </button>
        <button
          onClick={() => setViewOffset((prev) => ({ ...prev, x: Math.min(MAP_SIZE - visibleSize, prev.x + 5) }))}
          className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >
          →
        </button>
        <button
          onClick={() => setViewOffset({ x: 0, y: 0 })}
          className="px-3 py-1 bg-blue-100 rounded hover:bg-blue-200 text-blue-700"
        >
          Reset View
        </button>
      </div>

      {/* Map Grid */}
      <div
        className="border-2 border-gray-800 inline-block overflow-auto"
        style={{
          maxWidth: '100%',
          maxHeight: '600px',
        }}
      >
        <div
          className="grid gap-px bg-gray-800"
          style={{
            gridTemplateColumns: `repeat(${endX - startX}, minmax(0, 1fr))`,
          }}
        >
          {Array.from({ length: endY - startY }, (_, rowIdx) => {
            const y = startY + rowIdx;
            return Array.from({ length: endX - startX }, (_, colIdx) => {
              const x = startX + colIdx;
              const tile = tileMap.get(`${x},${y}`);
              const isPlayerTile = tile?.owner_id === currentPlayerId;
              const isEnemyTile = tile?.owner_id && tile?.owner_id !== currentPlayerId;
              const isUnclaimed = !tile?.owner_id;
              const isAdjacent = isAdjacentToPlayer(x, y);

              return (
                <button
                  key={`${x}-${y}`}
                  onClick={() => handleTileClick(tile, x, y)}
                  className={`
                    relative aspect-square min-w-[20px] min-h-[20px]
                    transition-all hover:brightness-110
                    ${getTileClass(tile)}
                    ${isUnclaimed && isAdjacent ? 'ring-1 ring-green-400 cursor-pointer' : ''}
                    ${isEnemyTile && isAdjacent ? 'ring-1 ring-yellow-400 cursor-crosshair' : ''}
                    ${isPlayerTile ? 'ring-1 ring-blue-300' : ''}
                  `}
                  title={`(${x}, ${y})${tile ? ` - Resource: ${tile.resource_value}` : ''}`}
                >
                  {tile && (
                    <span className="absolute bottom-0 right-0 text-[6px] text-white leading-none">
                      {tile.resource_value}
                    </span>
                  )}
                </button>
              );
            });
          })}
        </div>
      </div>

      {/* Instructions */}
      <div className="text-sm text-gray-600 bg-gray-50 p-4 rounded">
        <h3 className="font-bold mb-2">How to Play:</h3>
        <ul className="list-disc list-inside space-y-1">
          <li><span className="text-green-600 font-medium">Gray tiles with green border</span> - Click to claim adjacent territory</li>
          <li><span className="text-yellow-600 font-medium">Red tiles with yellow border</span> - Click to attack (you need more army than defender)</li>
          <li><span className="text-blue-600 font-medium">Blue tiles</span> - Your territory (generates gold every tick)</li>
          <li>Gold is generated every 10 seconds based on your tiles' resource values</li>
        </ul>
      </div>
    </div>
  );
}
