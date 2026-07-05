import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { queueService } from '../services/queueService';
import { Badge, Button } from '../components/UI';
import { Play, CheckCircle, AlertTriangle } from 'lucide-react';

const Queue = () => {
  const { data: queueEntries, isLoading } = useQuery({
    queryKey: ['queue'],
    queryFn: () => queueService.listQueue(0, 100),
  });

  const { data: status } = useQuery({
    queryKey: ['queue-status'],
    queryFn: queueService.getStatus,
    refetchInterval: 10000,
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'red';
      case 'high':
        return 'red';
      case 'normal':
        return 'blue';
      case 'low':
        return 'green';
      default:
        return 'blue';
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Queue Management</h1>
        <p className="text-gray-400 mt-2">Intelligent queue prioritization and processing</p>
      </div>

      {/* Queue Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass p-6 rounded-xl">
          <p className="text-gray-400 text-sm">Waiting</p>
          <p className="text-3xl font-bold mt-2 text-yellow-400">{status?.waiting || 0}</p>
        </div>
        <div className="glass p-6 rounded-xl">
          <p className="text-gray-400 text-sm">In Progress</p>
          <p className="text-3xl font-bold mt-2 text-blue-400">{status?.in_progress || 0}</p>
        </div>
        <div className="glass p-6 rounded-xl">
          <p className="text-gray-400 text-sm">Completed</p>
          <p className="text-3xl font-bold mt-2 text-green-400">{status?.completed || 0}</p>
        </div>
        <div className="glass p-6 rounded-xl">
          <p className="text-gray-400 text-sm">Utilization</p>
          <p className="text-3xl font-bold mt-2 text-purple-400">
            {Math.round((status?.queue_utilization || 0) * 100)}%
          </p>
        </div>
      </div>

      {/* Queue List */}
      <div className="space-y-3">
        {queueEntries?.map((entry: any, index: number) => (
          <div
            key={entry.id}
            className={`glass p-4 rounded-xl border-l-4 ${
              entry.status === 'waiting'
                ? 'border-l-yellow-500'
                : entry.status === 'in_progress'
                ? 'border-l-blue-500'
                : 'border-l-green-500'
            }`}
          >
            <div className="grid grid-cols-1 md:grid-cols-7 gap-4 items-center">
              <div className="text-center">
                <p className="text-4xl font-bold text-blue-400">#{entry.queue_number}</p>
                <p className="text-xs text-gray-400 mt-1">Position</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Person ID</p>
                <p className="font-semibold mt-1">{entry.person_id}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Priority</p>
                <Badge
                  text={entry.priority}
                  color={getPriorityColor(entry.priority)}
                  size="sm"
                />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Status</p>
                <Badge
                  text={entry.status}
                  color={entry.status === 'waiting' ? 'yellow' : entry.status === 'in_progress' ? 'blue' : 'green'}
                  size="sm"
                />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Officer</p>
                <p className="font-semibold mt-1">{entry.assigned_officer || 'Unassigned'}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Escalated</p>
                <Badge text={entry.is_escalated ? 'Yes' : 'No'} color={entry.is_escalated ? 'red' : 'green'} size="sm" />
              </div>
              <div className="flex gap-2 justify-end">
                {entry.status === 'waiting' && (
                  <Button size="sm" variant="primary">
                    <Play className="w-4 h-4" /> Start
                  </Button>
                )}
                {entry.status === 'in_progress' && (
                  <Button size="sm" variant="secondary">
                    <CheckCircle className="w-4 h-4" /> Complete
                  </Button>
                )}
              </div>
            </div>
            {entry.notes && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <p className="text-sm text-gray-400">
                  <span className="font-semibold">Notes:</span> {entry.notes}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Queue;
