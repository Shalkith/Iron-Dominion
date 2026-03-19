"use client";

import { useState } from 'react';
import { Alliance, AllianceRequest } from '@/lib/types';
import { allianceApi } from '@/lib/api';

interface AlliancePanelProps {
  alliances: Alliance[];
  pendingRequests: { incoming: AllianceRequest[]; outgoing: AllianceRequest[] };
  currentPlayerId: number;
  onUpdate: () => void;
}

export default function AlliancePanel({ alliances, pendingRequests, currentPlayerId, onUpdate }: AlliancePanelProps) {
  const [showSendForm, setShowSendForm] = useState(false);
  const [playerId, setPlayerId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAccept = async (requestId: number) => {
    try {
      setLoading(true);
      await allianceApi.acceptRequest(requestId);
      onUpdate();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (requestId: number) => {
    try {
      setLoading(true);
      await allianceApi.rejectRequest(requestId);
      onUpdate();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSendRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await allianceApi.sendRequest(parseInt(playerId));
      setPlayerId('');
      setShowSendForm(false);
      onUpdate();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getAllyName = (alliance: Alliance) => {
    return alliance.player1_id === currentPlayerId
      ? alliance.player2_username
      : alliance.player1_username;
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>
      )}

      {/* Active Alliances */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold">Your Alliances</h3>
          <button
            onClick={() => setShowSendForm(!showSendForm)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Send Request
          </button>
        </div>

        {showSendForm && (
          <form onSubmit={handleSendRequest} className="bg-gray-50 p-4 rounded-lg mb-4">
            <div className="flex gap-2">
              <input
                type="number"
                value={playerId}
                onChange={(e) => setPlayerId(e.target.value)}
                placeholder="Enter player ID"
                className="flex-1 px-3 py-2 border rounded"
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </form>
        )}

        {alliances.length === 0 ? (
          <p className="text-gray-500">You have no active alliances.</p>
        ) : (
          <div className="grid gap-2">
            {alliances.map((alliance) => (
              <div
                key={alliance.id}
                className="bg-green-50 border border-green-200 p-4 rounded-lg flex items-center justify-between"
              >
                <div>
                  <div className="font-bold">{getAllyName(alliance)}</div>
                  <div className="text-sm text-gray-500">Allied players cannot attack each other</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Incoming Requests */}
      {pendingRequests.incoming.length > 0 && (
        <div>
          <h3 className="text-xl font-bold mb-4">Incoming Requests</h3>
          <div className="grid gap-2">
            {pendingRequests.incoming.map((request) => (
              <div
                key={request.id}
                className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg flex items-center justify-between"
              >
                <div>
                  <div className="font-bold">{request.from_username}</div>
                  <div className="text-sm text-gray-500">wants to form an alliance</div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleAccept(request.id)}
                    disabled={loading}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => handleReject(request.id)}
                    disabled={loading}
                    className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50"
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Outgoing Requests */}
      {pendingRequests.outgoing.length > 0 && (
        <div>
          <h3 className="text-xl font-bold mb-4">Outgoing Requests</h3>
          <div className="grid gap-2">
            {pendingRequests.outgoing.map((request) => (
              <div
                key={request.id}
                className="bg-gray-50 border border-gray-200 p-4 rounded-lg"
              >
                <div className="font-bold">{request.to_username}</div>
                <div className="text-sm text-gray-500">Request pending...</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
