/**
 * TypeScript type definitions for Controle PGM.
 * Based on OpenAPI/backend contracts.
 */

// ============================================================================
// User Types
// ============================================================================

export type UserRole = 'admin' | 'user';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  is_active: boolean;
  must_change_password: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreateRequest {
  email: string;
  name: string;
  password: string;
  role?: UserRole;
}

export interface UserUpdateRequest {
  name?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface UsersListResponse {
  items: User[];
  total: number;
}

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user_id: string;
  email: string;
  name: string;
  role: UserRole;
  must_change_password: boolean;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ResetPasswordResponse {
  temporary_password: string;
}

// ============================================================================
// Document Type Types
// ============================================================================

export interface DocumentType {
  id: string;
  code: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DocumentTypeCreateRequest {
  code: string;
  name: string;
}

export interface DocumentTypeUpdateRequest {
  name?: string;
  is_active?: boolean;
}

export interface DocumentTypesListResponse {
  items: DocumentType[];
  total: number;
}

// ============================================================================
// Sequence Types
// ============================================================================

export interface Sequence {
  document_type_code: string;
  year: number;
  current_number: number;
  updated_at: string;
}

export interface SequencesListResponse {
  items: Sequence[];
  total: number;
}

// ============================================================================
// Number Generation Types
// ============================================================================

export interface GenerateNumberRequest {
  document_type_code: string;
  year: number;
}

export interface GenerateNumberResponse {
  number: number;
  document_type_code: string;
  document_type_name: string;
  year: number;
  formatted: string;
}

/** Alias for UI component usage - matches API response */
export type GeneratedNumber = GenerateNumberResponse;

export interface CorrectionRequest {
  document_type_code: string;
  year: number;
  new_number: number;
  notes: string;
}

export interface CorrectionResponse {
  previous_number: number;
  new_number: number;
  document_type_code: string;
  year: number;
  notes: string;
}

// ============================================================================
// History/Audit Log Types
// ============================================================================

export type LogAction = 'generated' | 'corrected';

export interface NumberLog {
  id: string;
  document_type_code: string;
  year: number;
  number: number;
  action: LogAction;
  user_id: string;
  user_name: string;
  previous_number: number | null;
  notes: string | null;
  created_at: string;
}

export interface HistoryFilter {
  document_type_code?: string;
  year?: number;
  user_id?: string;
  action?: LogAction;
  page?: number;
  page_size?: number;
}

export interface HistoryResponse {
  items: NumberLog[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============================================================================
// API Error Types
// ============================================================================

export interface ApiErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

// ============================================================================
// Health Check Types
// ============================================================================

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export interface SortConfig<T> {
  key: keyof T;
  direction: 'asc' | 'desc';
}

export interface TableColumn<T> {
  key: keyof T | string;
  header: string;
  sortable?: boolean;
  render?: (item: T) => React.ReactNode;
}
