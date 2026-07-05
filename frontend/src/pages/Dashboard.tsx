import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';
import {
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileCheck,
  Bell,
} from 'lucide-react';
import { StatCard, SimpleBarChart, SimplePieChart, SimpleLineChart } from '../components/Charts';
import { Alert, Badge } from '../components/UI';
import { format } from 'date-fns';

const Dashboard = () => {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardService.getStats,
    refetchInterval: 30000,
  });

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['dashboard-analytics'],
    queryFn: dashboardService.getAnalytics,
    refetchInterval: 30000,
  });

  const { data: alerts } = useQuery({
    queryKey: ['dashboard-alerts'],
    queryFn: dashboardService.getAlerts,
    refetchInterval: 10000,
  });

  if (statsLoading || analyticsLoading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const riskData = [
    { name: 'Critical', value: analytics?.risk_distribution?.critical || 0 },
    { name: 'High', value: analytics?.risk_distribution?.high || 0 },
    { name: 'Medium', value: analytics?.risk_distribution?.medium || 0 },
    { name: 'Low', value: analytics?.risk_distribution?.low || 0 },
  ];

  const personStatusData = [
    { name: 'Detected', value: analytics?.person_status?.detected || 0 },
    { name: 'In Queue', value: analytics?.person_status?.in_queue || 0 },
    { name: 'Cleared', value: analytics?.person_status?.cleared || 0 },
    { name: 'Flagged', value: analytics?.person_status?.flagged || 0 },
  ];

  return (
    <div className="p-8 space-y-8 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text">Dashboard</h1>
          <p className="text-gray-400 mt-2">Welcome back! Here's your system overview.</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Last updated:</p>
          <p className="text-lg font-semibold">{format(new Date(), 'PPpp')}</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Persons Detected"
          value={stats?.total_persons_detected || 0}
          trend={15}
          icon={Users}
          color="bg-blue-600"
        />
        <StatCard
          title="High Risk"
          value={stats?.high_risk_detected || 0}
          trend={-5}
          icon={AlertTriangle}
          color="bg-red-600"
        />
        <StatCard
          title="Cleared"
          value={stats?.persons_cleared || 0}
          trend={8}
          icon={CheckCircle}
          color="bg-green-600"
        />
        <StatCard
          title="Queue Waiting"
          value={stats?.queue_waiting || 0}
          trend={2}
          icon={Clock}
          color="bg-yellow-600"
        />
      </div>

      {/* Critical Alerts */}
      {alerts && alerts.length > 0 && (
        <div className="glass p-6 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <Bell className="w-5 h-5 text-red-400" />
            <h2 className="text-xl font-semibold">Active Alerts ({alerts.length})</h2>
          </div>
          <div className="space-y-3">
            {alerts.slice(0, 5).map((alert: any) => (
              <div
                key={alert.id}
                className="flex items-start gap-4 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
              >
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  alert.severity === 'critical'
                    ? 'bg-red-500 animate-pulse'
                    : alert.severity === 'warning'
                    ? 'bg-yellow-500'
                    : 'bg-blue-500'
                }`} />
                <div className="flex-1">
                  <h3 className="font-semibold">{alert.title}</h3>
                  <p className="text-sm text-gray-400 mt-1">{alert.description}</p>
                </div>
                <Badge
                  text={alert.severity}
                  color={alert.severity === 'critical' ? 'red' : 'yellow'}
                  size="sm"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SimplePieChart data={riskData} title="Risk Distribution" />
        <SimplePieChart data={personStatusData} title="Person Status" />
      </div>

      {/* Document Stats */}
      <div className="glass p-6 rounded-xl">
        <div className="flex items-center gap-2 mb-4">
          <FileCheck className="w-5 h-5" />
          <h2 className="text-xl font-semibold">Document Verification</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 bg-white/5 rounded-lg">
            <p className="text-gray-400 text-sm">Total Documents</p>
            <p className="text-2xl font-bold mt-2">{stats?.total_documents || 0}</p>
          </div>
          <div className="p-4 bg-white/5 rounded-lg">
            <p className="text-gray-400 text-sm">Verified</p>
            <p className="text-2xl font-bold mt-2 text-green-400">{stats?.documents_verified || 0}</p>
          </div>
          <div className="p-4 bg-white/5 rounded-lg">
            <p className="text-gray-400 text-sm">Critical Alerts</p>
            <p className="text-2xl font-bold mt-2 text-red-400 animate-pulse">{stats?.critical_alerts || 0}</p>
          </div>
          <div className="p-4 bg-white/5 rounded-lg">
            <p className="text-gray-400 text-sm">Today's Detections</p>
            <p className="text-2xl font-bold mt-2 text-blue-400">{stats?.persons_today || 0}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
