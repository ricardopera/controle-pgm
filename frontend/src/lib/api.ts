/**
 * API client for Controle PGM backend.
 * Uses fetch with credentials for HttpOnly cookie authentication.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

/**
 * Custom error class for API errors.
 */
export class ApiError extends Error {
  status: number;
  statusText: string;
  data?: Record<string, unknown>;

  constructor(
    status: number,
    statusText: string,
    data?: Record<string, unknown>
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
    this.data = data;
  }
}

/**
 * Event emitter for authentication events.
 */
type AuthEventListener = () => void;
const authEventListeners: AuthEventListener[] = [];

export const onUnauthorized = (listener: AuthEventListener): (() => void) => {
  authEventListeners.push(listener);
  return () => {
    const index = authEventListeners.indexOf(listener);
    if (index > -1) {
      authEventListeners.splice(index, 1);
    }
  };
};

const emitUnauthorized = () => {
  authEventListeners.forEach((listener) => listener());
};

/**
 * Generic fetch wrapper with authentication and error handling.
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Send HttpOnly cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  // Handle 401 Unauthorized - emit event for global handling
  if (response.status === 401) {
    emitUnauthorized();
    throw new ApiError(response.status, response.statusText);
  }

  // Handle other error responses
  if (!response.ok) {
    let data: Record<string, unknown> | undefined;
    try {
      data = await response.json();
    } catch {
      // Response may not be JSON
    }
    throw new ApiError(response.status, response.statusText, data);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

/**
 * API client methods organized by resource.
 */
export const api = {
  /**
   * Generic GET request.
   */
  get: <T>(endpoint: string, options?: RequestInit): Promise<T> =>
    apiFetch<T>(endpoint, { ...options, method: 'GET' }),

  /**
   * Generic POST request.
   */
  post: <T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  /**
   * Generic PUT request.
   */
  put: <T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),

  /**
   * Generic PATCH request.
   */
  patch: <T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  /**
   * Generic DELETE request.
   */
  delete: <T>(endpoint: string, options?: RequestInit): Promise<T> =>
    apiFetch<T>(endpoint, { ...options, method: 'DELETE' }),

  // Health check
  health: {
    check: () => apiFetch<{ status: string; timestamp: string }>('/health'),
  },

  // Authentication
  auth: {
    login: (email: string, password: string) =>
      apiFetch<{
        user_id: string;
        email: string;
        name: string;
        role: 'admin' | 'user';
        must_change_password: boolean;
      }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),

    logout: () =>
      apiFetch<void>('/auth/logout', {
        method: 'POST',
      }),

    me: () =>
      apiFetch<{
        user_id: string;
        email: string;
        name: string;
        role: 'admin' | 'user';
        must_change_password: boolean;
      }>('/auth/me'),

    changePassword: (currentPassword: string, newPassword: string) =>
      apiFetch<void>('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      }),
  },

  // Users (admin only)
  users: {
    list: () =>
      apiFetch<{
        items: Array<{
          id: string;
          email: string;
          name: string;
          role: 'admin' | 'user';
          is_active: boolean;
          must_change_password: boolean;
          created_at: string;
          updated_at: string;
        }>;
        total: number;
      }>('/users'),

    get: (id: string) =>
      apiFetch<{
        id: string;
        email: string;
        name: string;
        role: 'admin' | 'user';
        is_active: boolean;
        must_change_password: boolean;
        created_at: string;
        updated_at: string;
      }>(`/users/${id}`),

    create: (data: {
      email: string;
      name: string;
      password: string;
      role?: 'admin' | 'user';
    }) =>
      apiFetch<{
        id: string;
        email: string;
        name: string;
        role: 'admin' | 'user';
        is_active: boolean;
        must_change_password: boolean;
        created_at: string;
        updated_at: string;
      }>('/users', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (
      id: string,
      data: { name?: string; role?: 'admin' | 'user'; is_active?: boolean }
    ) =>
      apiFetch<{
        id: string;
        email: string;
        name: string;
        role: 'admin' | 'user';
        is_active: boolean;
        must_change_password: boolean;
        created_at: string;
        updated_at: string;
      }>(`/users/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),

    resetPassword: (id: string) =>
      apiFetch<{ temporary_password: string }>(`/users/${id}/reset-password`, {
        method: 'POST',
      }),
  },

  // Document types (admin only)
  documentTypes: {
    list: () =>
      apiFetch<{
        items: Array<{
          id: string;
          code: string;
          name: string;
          is_active: boolean;
          created_at: string;
          updated_at: string;
        }>;
        total: number;
      }>('/document-types'),

    get: (id: string) =>
      apiFetch<{
        id: string;
        code: string;
        name: string;
        is_active: boolean;
        created_at: string;
        updated_at: string;
      }>(`/document-types/${id}`),

    create: (data: { code: string; name: string }) =>
      apiFetch<{
        id: string;
        code: string;
        name: string;
        is_active: boolean;
        created_at: string;
        updated_at: string;
      }>('/document-types', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (id: string, data: { name?: string; is_active?: boolean }) =>
      apiFetch<{
        id: string;
        code: string;
        name: string;
        is_active: boolean;
        created_at: string;
        updated_at: string;
      }>(`/document-types/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
  },

  // Numbers (document numbering)
  numbers: {
    generate: (documentTypeCode: string, year: number) =>
      apiFetch<{
        number: number;
        document_type_code: string;
        year: number;
        formatted: string;
      }>('/numbers/generate', {
        method: 'POST',
        body: JSON.stringify({
          document_type_code: documentTypeCode,
          year,
        }),
      }),

    current: (documentTypeCode: string, year: number) =>
      apiFetch<{
        document_type_code: string;
        year: number;
        current_number: number;
        updated_at: string;
      }>(`/numbers/current?document_type_code=${documentTypeCode}&year=${year}`),

    sequences: () =>
      apiFetch<{
        items: Array<{
          document_type_code: string;
          year: number;
          current_number: number;
          updated_at: string;
        }>;
        total: number;
      }>('/numbers/sequences'),

    correct: (data: {
      document_type_code: string;
      year: number;
      new_number: number;
      notes: string;
    }) =>
      apiFetch<{
        previous_number: number;
        new_number: number;
        document_type_code: string;
        year: number;
        notes: string;
      }>('/numbers/correct', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // History (audit log)
  history: {
    list: (params?: {
      document_type_code?: string;
      year?: number;
      user_id?: string;
      action?: 'generated' | 'corrected';
      page?: number;
      page_size?: number;
    }) => {
      const searchParams = new URLSearchParams();
      if (params?.document_type_code) {
        searchParams.set('document_type_code', params.document_type_code);
      }
      if (params?.year) {
        searchParams.set('year', String(params.year));
      }
      if (params?.user_id) {
        searchParams.set('user_id', params.user_id);
      }
      if (params?.action) {
        searchParams.set('action', params.action);
      }
      if (params?.page) {
        searchParams.set('page', String(params.page));
      }
      if (params?.page_size) {
        searchParams.set('page_size', String(params.page_size));
      }

      const query = searchParams.toString();
      return apiFetch<{
        items: Array<{
          id: string;
          document_type_code: string;
          year: number;
          number: number;
          action: 'generated' | 'corrected';
          user_id: string;
          user_name: string;
          previous_number: number | null;
          notes: string | null;
          created_at: string;
        }>;
        total: number;
        page: number;
        page_size: number;
        total_pages: number;
      }>(`/history${query ? `?${query}` : ''}`);
    },
  },
};

export default api;
