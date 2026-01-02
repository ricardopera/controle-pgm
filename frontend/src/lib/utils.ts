import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combines class names using clsx and tailwind-merge.
 * This is the standard utility for Shadcn/UI components.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a document number with leading zeros.
 * @param number - The number to format
 * @param digits - Number of digits (default: 4)
 * @returns Formatted number string (e.g., "0042")
 */
export function formatNumber(number: number, digits: number = 4): string {
  return String(number).padStart(digits, '0');
}

/**
 * Format a full document number with type code and year.
 * @param code - Document type code (e.g., "OF")
 * @param number - The sequence number
 * @param year - The year
 * @returns Formatted document number (e.g., "OF 0042/2025")
 */
export function formatDocumentNumber(
  code: string,
  number: number,
  year: number
): string {
  return `${code} ${formatNumber(number)}/${year}`;
}

/**
 * Format a date string for display in pt-BR locale.
 * @param dateString - ISO date string
 * @returns Formatted date (e.g., "15/01/2025 14:30")
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format a date string for display (date only).
 * @param dateString - ISO date string
 * @returns Formatted date (e.g., "15/01/2025")
 */
export function formatDateOnly(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

/**
 * Format a date string for display (time only).
 * @param dateString - ISO date string
 * @returns Formatted time (e.g., "14:30")
 */
export function formatTimeOnly(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Get the current year.
 * @returns Current year as number
 */
export function getCurrentYear(): number {
  return new Date().getFullYear();
}

/**
 * Generate an array of years for selection (current year + 1 to current year - 5).
 * @returns Array of years
 */
export function getYearOptions(): number[] {
  const currentYear = getCurrentYear();
  const years: number[] = [];
  for (let year = currentYear + 1; year >= currentYear - 5; year--) {
    years.push(year);
  }
  return years;
}

/**
 * Capitalize the first letter of a string.
 * @param str - Input string
 * @returns Capitalized string
 */
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Translate role to Portuguese.
 * @param role - Role key ('admin' | 'user')
 * @returns Role in Portuguese
 */
export function translateRole(role: 'admin' | 'user'): string {
  return role === 'admin' ? 'Administrador' : 'Usuário';
}

/**
 * Translate action to Portuguese.
 * @param action - Action key ('generated' | 'corrected')
 * @returns Action in Portuguese
 */
export function translateAction(action: 'generated' | 'corrected'): string {
  return action === 'generated' ? 'Gerado' : 'Corrigido';
}

/**
 * Validate password according to policy.
 * @param password - Password to validate
 * @returns Object with isValid and errors array
 */
export function validatePassword(password: string): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('A senha deve ter pelo menos 8 caracteres');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('A senha deve conter pelo menos uma letra maiúscula');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('A senha deve conter pelo menos uma letra minúscula');
  }

  if (!/[0-9]/.test(password)) {
    errors.push('A senha deve conter pelo menos um número');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Debounce a function call.
 * @param fn - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}
