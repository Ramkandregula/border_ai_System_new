import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { riskService } from '../services/riskService';
import { Badge, Button } from '../components/UI';
import { TrendingUp, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';

const RiskAssessment = () => {
  const { data: assessments, isLoading } = useQuery({
    queryKey: ['risk-assessments'],
    queryFn: () => riskService.getHistory(undefined, 0, 100),
  });

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'text-red-400';
      case 'high':
        return 'text-orange-400';
      case 'medium':
        return 'text-yellow-400';
      case 'low':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  const getRiskBg = (level: string) => {
    switch (level) {
      case 'critical':
        return 'bg-red-500/10 border-red-500/20';
      case 'high':
        return 'bg-orange-500/10 border-orange-500/20';
      case 'medium':
        return 'bg-yellow-500/10 border-yellow-500/20';
      case 'low':
        return 'bg-green-500/10 border-green-500/20';
      default:
        return 'bg-gray-500/10 border-gray-500/20';
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
        <h1 className="text-3xl font-bold gradient-text">Risk Assessment</h1>
        <p className="text-gray-400 mt-2">AI-powered threat and risk analysis</p>
      </div>

      <div className="space-y-4">
        {assessments?.map((assessment: any) => (
          <div
            key={assessment.id}
            className={`glass p-6 rounded-xl border ${getRiskBg(assessment.risk_level)}`}
          >
            <div className="grid grid-cols-1 md:grid-cols-6 gap-4 items-start">
              <div>
                <p className="text-gray-400 text-sm">Person ID</p>
                <p className="font-semibold mt-1">{assessment.person_id}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Risk Score</p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        assessment.risk_score > 0.8
                          ? 'bg-red-500'
                          : assessment.risk_score > 0.6
                          ? 'bg-orange-500'
                          : assessment.risk_score > 0.4
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${assessment.risk_score * 100}%` }}
                    />
                  </div>
                  <span className="font-semibold min-w-fit">
                    {(assessment.risk_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Risk Level</p>
                <Badge
                  text={assessment.risk_level}
                  color={{
                    critical: 'red',
                    high: 'red',
                    medium: 'yellow',
                    low: 'green',
                  }[assessment.risk_level] || 'blue'}
                  size="md"
                />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Behavioral</p>
                <p className={`font-semibold mt-1 ${
                  (assessment.behavioral_risk || 0) > 0.5
                    ? 'text-red-400'
                    : 'text-green-400'
                }`}>
                  {((assessment.behavioral_risk || 0) * 100).toFixed(0)}%
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Document</p>
                <p className={`font-semibold mt-1 ${
                  (assessment.document_risk || 0) > 0.5
                    ? 'text-red-400'
                    : 'text-green-400'
                }`}>
                  {((assessment.document_risk || 0) * 100).toFixed(0)}%
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Intelligence</p>
                <p className={`font-semibold mt-1 ${
                  (assessment.intelligence_match_risk || 0) > 0.5
                    ? 'text-red-400'
                    : 'text-green-400'
                }`}>
                  {((assessment.intelligence_match_risk || 0) * 100).toFixed(0)}%
                </p>
              </div>
            </div>

            {assessment.flagged_indicators?.length > 0 && (
              <div className="mt-4 pt-4 border-t border-white/10">
                <p className="text-sm text-gray-400 mb-2">Flagged Indicators:</p>
                <div className="flex flex-wrap gap-2">
                  {assessment.flagged_indicators.map((indicator: string, idx: number) => (
                    <Badge key={idx} text={indicator} color="red" size="sm" />
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RiskAssessment;
