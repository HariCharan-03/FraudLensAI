export interface RiskIndicator {
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  title: string;
  description: string;
}

export interface FeatureExplanation {
  feature_name: string;
  display_name: string;
  description: string;
  feature_value: number | string;
  shap_impact: number;
  direction: 'increases_risk' | 'lowers_risk' | 'neutral';
  abs_impact: number;
  summary_text: string;
}

export interface DnsRecords {
  A: string[];
  AAAA: string[];
  MX: string[];
  TXT: string[];
  NS: string[];
}

export interface SslCertificate {
  status: string;
  issuer?: string;
  subject?: string;
  subject_alt_names?: string[];
  valid_from?: string;
  valid_to?: string;
  is_expired?: boolean;
  tls_version?: string;
  cipher?: string;
  error?: string;
}

export interface ServerLocation {
  status: string;
  ip?: string;
  country?: string;
  country_code?: string;
  region?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  isp?: string;
  org?: string;
  as_number?: string;
  timezone?: string;
  note?: string;
  error?: string;
}

export interface DomainIntel {
  domain: string;
  resolved_ips: string[];
  primary_ip?: string;
  dns_resolution_error?: string;
  dns_records: DnsRecords;
  dns_status: string;
  ssl_certificate: SslCertificate;
  server_location: ServerLocation;
}

export interface ThreatFeedItem {
  service: string;
  status: 'confirmed_match' | 'no_match_found' | 'unavailable' | 'error' | 'not_checked';
  details: string;
  confirmed_match: boolean;
  threat_types?: string[];
}

export interface ThreatIntel {
  has_confirmed_threat: boolean;
  confirmed_sources: string[];
  checked_feeds_count: number;
  unavailable_feeds_count: number;
  feeds: {
    google_safe_browsing: ThreatFeedItem;
    phishtank: ThreatFeedItem;
    openphish?: ThreatFeedItem;
  };
  interpretation_notice: string;
}

export interface ScanResult {
  id: string;
  url: string;
  normalized_url?: string;
  created_at: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'INCONCLUSIVE';
  risk_score: number;
  model_score?: number;
  model_version?: string;
  model_type?: string;
  is_phishing_predicted?: boolean;
  status: string;
  error_message?: string;
  plain_explanation?: string;

  features?: Record<string, number>;
  feature_explanations?: FeatureExplanation[];
  indicators?: RiskIndicator[];
  recommendations?: string[];
  domain_intel?: DomainIntel;
  threat_intel?: ThreatIntel;
}

export interface Citation {
  title: string;
  organization: string;
  source_url: string;
  citation: string;
  relevance?: number;
}

export interface ChatMessage {
  id: string;
  scan_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface DashboardStats {
  total_scans: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  inconclusive_count: number;
  distribution: {
    name: string;
    value: number;
    color: string;
  }[];
  recent_scans: ScanResult[];
}

export interface HealthStatus {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  database: { status: string };
  machine_learning: {
    status: string;
    model_type?: string;
    model_version?: string;
    features_loaded?: number;
    shap_explainer_loaded?: boolean;
  };
  threat_intelligence: {
    google_safe_browsing: string;
    phishtank: string;
    openphish?: string;
    live_dns_resolution: string;
  };
  rag_knowledge_base: {
    status: string;
    chunks_indexed: number;
    sources: string[];
  };
}
