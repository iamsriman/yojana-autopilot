import { api } from "./client";
import type {
  ChatResponse,
  EligibilityProfile,
  EligibilityResponse,
  OfficesResponse,
  PortalResponse,
  SearchRequest,
  ServiceSearchResult,
} from "../types/api";

export async function askAssistant(question: string, district?: string) {
  const { data } = await api.post<ChatResponse>("/chat", { question, district, top_k: 5 });
  return data;
}

export async function checkEligibility(profile: EligibilityProfile) {
  const { data } = await api.post<EligibilityResponse>("/eligibility", profile);
  return data;
}

export async function searchServices(request: SearchRequest) {
  const { data } = await api.post<ServiceSearchResult[]>("/services/search", request);
  return data;
}

export async function getOffices(district: string, officeType?: string) {
  const { data } = await api.get<OfficesResponse>(`/offices/${encodeURIComponent(district)}`, {
    params: officeType ? { office_type: officeType } : undefined,
  });
  return data;
}

export async function getPortal(portalId: string) {
  const { data } = await api.get<PortalResponse>(`/portal/${encodeURIComponent(portalId)}`);
  return data;
}
