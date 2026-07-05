import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { detectionService } from '../services/detectionService';
import { Badge, Button } from '../components/UI';
import { Radio, MapPin, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

const Detection = () => {
  const [filterStatus, setFilterStatus] = useState('all');

  const { data: persons, isLoading, refetch } = useQuery({
    queryKey: ['persons'],
    queryFn: () => detectionService.listPersons(0, 100),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: any) =>
      detectionService.updatePerson(id, data),
    onSuccess: () => {
      toast.success('Person updated successfully');
      refetch();
    },
  });

  const filteredPersons =
    filterStatus === 'all'
      ? persons
      : persons?.filter((p: any) => p.status === filterStatus);

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
        <h1 className="text-3xl font-bold gradient-text">Person Detection</h1>
        <p className="text-gray-400 mt-2">Real-time person tracking and monitoring</p>
      </div>

      {/* Filters */}
      <div className="glass p-6 rounded-xl">
        <div className="flex gap-2 flex-wrap">
          {['all', 'detected', 'in_queue', 'flagged', 'cleared'].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                filterStatus === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }`}
            >
              {status.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Detection List */}
      <div className="space-y-4">
        {filteredPersons?.map((person: any) => (
          <div
            key={person.id}
            className="glass p-6 rounded-xl hover:bg-white/15 transition-colors"
          >
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
              <div>
                <p className="text-gray-400 text-sm">Detection ID</p>
                <p className="font-semibold mt-1">{person.detection_id}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Age</p>
                <p className="font-semibold mt-1">{person.age_estimated || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Gender</p>
                <p className="font-semibold mt-1">{person.gender || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Confidence</p>
                <div className="mt-1 flex items-center gap-2">
                  <div className="w-12 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-400 to-cyan-400"
                      style={{
                        width: `${(person.detection_confidence || 0) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-sm">
                    {((person.detection_confidence || 0) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge
                  text={person.status}
                  color={{
                    detected: 'blue',
                    in_queue: 'yellow',
                    flagged: 'red',
                    cleared: 'green',
                  }[person.status] || 'blue'}
                />
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-white/10 flex gap-2">
              <Button
                size="sm"
                onClick={() =>
                  updateMutation.mutate({
                    id: person.id,
                    data: { status: 'flagged' },
                  })
                }
              >
                <Zap className="w-4 h-4" /> Flag
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() =>
                  updateMutation.mutate({
                    id: person.id,
                    data: { status: 'cleared' },
                  })
                }
              >
                <Radio className="w-4 h-4" /> Clear
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Detection;
