export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'officer' | 'analyst' | 'viewer';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Person {
  id: number;
  detection_id: string;
  status: 'detected' | 'in_queue' | 'under_review' | 'cleared' | 'flagged' | 'detained';
  age_estimated: number | null;
  gender: string | null;
  height: number | null;
  distinguishing_marks: string | null;
  detection_confidence: number | null;
  detected_at: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: number;
  person_id: number | null;
  document_type: 'passport' | 'visa' | 'id_card' | 'driver_license' | 'travel_permit' | 'other';
  status: 'pending' | 'verified' | 'rejected' | 'expired' | 'suspicious';
  document_number: string | null;
  holder_name: string | null;
  issuing_country: string | null;
  is_authentic: boolean | null;
  verification_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface RiskAssessment {
  id: number;
  person_id: number;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  behavioral_risk: number | null;
  document_risk: number | null;
  biometric_risk: number | null;
  intelligence_match_risk: number | null;
  flagged_indicators: string[];
  assessment_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface QueueEntry {
  id: number;
  person_id: number;
  queue_number: number;
  priority: 'low' | 'normal' | 'high' | 'critical';
  status: 'waiting' | 'in_progress' | 'completed' | 'cancelled' | 'escalated';
  assigned_officer: string | null;
  notes: string | null;
  is_escalated: boolean;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  id: number;
  person_id: number | null;
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
  status: 'active' | 'acknowledged' | 'resolved';
  alert_type: string;
  created_at: string;
}

export interface DashboardStats {
  total_persons_detected: number;
  persons_today: number;
  high_risk_detected: number;
  persons_cleared: number;
  queue_waiting: number;
  total_documents: number;
  documents_verified: number;
  critical_alerts: number;
}
