"use client";

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, gameApi, allianceApi } from '@/lib/api';
import { Player, Tile, Alliance, AllianceRequest, AttackLog, LeaderboardEntry } from '@/lib/types';
import MapView from '@/components/MapView';
import PlayerStats from '@/components/PlayerStats';
import AlliancePanel from '@/components/AlliancePanel';
import AttackLogPanel from '@/components/AttackLogPanel';
import Leaderboard from '@/components/Leaderboard';

export default function DashboardPage() {
  const router = useRouter();
  const [player, setPlayer] = useState<Player | null>(null);
  const [tiles, setTiles] = useState<Tile[]>([]);
  const [myTiles, setMyTiles] = useState<Tile[]>([]);
  const [alliances, setAlliances] = useState<Alliance[]>([]);
  const [pendingRequests, setPendingRequests] = useState<{ incoming: AllianceRequest[]; outgoing: AllianceRequest[] }>({ incoming: [], outgoing: [] });
  const [attackLogs, setAttackLogs] = useState<AttackLog[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState<'map' | 'alliances' | 'logs' | 'leaderboard'>('map');

  const fetchData = useCallback(async () => {
    try {
      const [playerData, tilesData, myTilesData, alliancesData, requestsData, logsData, leaderboardData] = await Promise.all([
        authApi.me(),
        gameApi.getMapWithOwners(),
        gameApi.getMyTiles(),
        allianceApi.getMyAlliances(),
        allianceApi.getPendingRequests(),
        gameApi.getAttackLogs(),
        gameApi.getLeaderboard(),
      ]);

      setPlayer(playerData);
      setTiles(tilesData);
      setMyTiles(myTilesData);
      setAlliances(alliancesData);
      setPendingRequests(requestsData);
      setAttackLogs(logsData.logs || []);
      setLeaderboard(leaderboardData.leaderboard || []);
    } catch (err: any) {
      if (err.message?.includes('Not authenticated') || err.message?.includes('401')) {
        router.push('/');
      } else {
        setError(err.message || 'Failed to load data');
      }
    }
  }, [router]);

  useEffect(() => {
    fetchData();
    setLoading(false);

    // Poll for updates every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleLogout = async () => {
    try {
      await authApi.logout();
      router.push('/');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  const handleClaim = async (x: number, y: number) => {
    try {
      const result = await gameApi.claimTile(x, y);
      setMessage(result.message);
      fetchData();
      setTimeout(() => setMessage(''), 3000);
    } catch (err: any) {
      setError(err.message);
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleAttack = async (x: number, y: number) => {
    try {
      const result = await gameApi.attackTile(x, y);
      setMessage(result.message);
      fetchData();
      setTimeout(() => setMessage(''), 3000);
    } catch (err: any) {
      setError(err.message);
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleSpawn = async () => {
    try {
      const result = await gameApi.spawn();
      setMessage(result.message);
      fetchData();
    } catch (err: any) {
      setError(err.message);
      setTimeout(() => setError(''), 3000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!player) {
    return null;
  }

  const hasSpawned = myTiles.length > 0;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">War Game</h1>
            <p className="text-sm text-gray-600">Welcome, {player.username}!</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm text-gray-600">Gold: <span className="font-bold text-yellow-600">{player.gold}</span></div>
              <div className="text-sm text-gray-600">Army: <span className="font-bold text-blue-600">{player.army_size}</span></div>
              <div className="text-sm text-gray-600">Tiles: <span className="font-bold text-green-600">{myTiles.length}</span></div>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Notifications */}
      {(message || error) && (
        <div className="max-w-7xl mx-auto px-4 py-2">
          {message && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {message}
            </div>
          )}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
        </div>
      )}

      {/* Spawn Screen */}
      {!hasSpawned && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold mb-4">Welcome to War Game!</h2>
            <p className="text-gray-600 mb-6">
              You need to spawn on the map to start playing. Click the button below to claim your first tile.
            </p>
            <button
              onClick={handleSpawn}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-700"
            >
              Spawn on Map
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      {hasSpawned && (
        <div className="max-w-7xl mx-auto px-4 py-6">
          {/* Tabs */}
          <div className="flex gap-2 mb-6 bg-white p-2 rounded-lg shadow-sm">
            {(['map', 'alliances', 'logs', 'leaderboard'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-md font-medium capitalize ${
                  activeTab === tab
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {tab === 'logs' ? 'Attack Logs' : tab}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="bg-white rounded-lg shadow-md p-6">
            {activeTab === 'map' && (
              <MapView
                tiles={tiles}
                currentPlayerId={player.id}
                onClaim={handleClaim}
                onAttack={handleAttack}
              />
            )}

            {activeTab === 'alliances' && (
              <AlliancePanel
                alliances={alliances}
                pendingRequests={pendingRequests}
                currentPlayerId={player.id}
                onUpdate={fetchData}
              />
            )}

            {activeTab === 'logs' && (
              <AttackLogPanel logs={attackLogs} currentPlayerId={player.id} />
            )}

            {activeTab === 'leaderboard' && (
              <Leaderboard entries={leaderboard} currentPlayerId={player.id} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
