export type EligibilityStatus = "eligible" | "need_more_information" | "not_eligible";

export interface EligibilityProfile {
  district?: string;
  income?: number;
  annual_income?: number;
  location?: "rural" | "urban";
  has_rice_card?: boolean;
  has_ration_card?: boolean;
  farmer?: boolean;
  disabled?: boolean;
  widow?: boolean;
  student?: boolean;
  electricity_units?: number;
  land?: number;
  four_wheeler?: boolean;
  answers?: Record<string, boolean | string | number>;
}

export interface SchemeDecision {
  scheme_id: string;
  scheme_name: string;
  category?: string | null;
  status: EligibilityStatus;
  eligible: boolean;
  reasons: string[];
  missing_information: string[];
  missing_questions: string[];
  next_questions: string[];
  missing_documents: string[];
  benefits: string[];
  application_links: string[];
  processing_time?: string | null;
  confidence: number;
}

export interface EligibilityResponse {
  eligible: SchemeDecision[];
  need_more_information: SchemeDecision[];
  not_eligible: SchemeDecision[];
}

export interface SearchRequest {
  query?: string;
  keywords?: string[];
  category?: string;
  documents?: string[];
  benefits?: string[];
  top_k?: number;
}

export interface ServiceSearchResult {
  id: string;
  name: string;
  category?: string | null;
  description?: string | null;
  documents: string[];
  portal?: string | null;
  offices: string[];
  processing_time?: string | null;
  score: number;
}

export interface Office {
  name: string;
  address?: string | null;
  phone?: string | null;
  hours?: string | null;
  office_hours?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  office_type: string;
  rating?: number | null;
  notes?: string | null;
}

export interface OfficesResponse {
  district: string;
  offices: Office[];
  available_office_types: string[];
}

export interface PortalResponse {
  portal_id: string;
  name: string;
  portal_url?: string | null;
  status_url?: string | null;
  helpline?: string | null;
  description?: string | null;
  owner?: string | null;
  verify_before_use: boolean;
}

export interface RetrievedSource {
  source_type: "JSON" | "Web";
  title: string;
  content: string;
  score?: number | null;
  metadata: Record<string, unknown>;
  url?: string | null;
}

export interface ChatResponse {
  answer: string;
  confidence: number;
  sources: RetrievedSource[];
  used_web_search: boolean;
}
