/**
 * Page container component.
 * Provides consistent page layout with title and optional actions.
 */

import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface PageContainerProps {
  /** Page title displayed at the top */
  title: string;
  /** Optional subtitle or description */
  description?: string;
  /** Optional action buttons displayed on the right side of the header */
  actions?: ReactNode;
  /** Page content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

export function PageContainer({
  title,
  description,
  actions,
  children,
  className,
}: PageContainerProps) {
  return (
    <div className={cn('flex flex-col gap-6', className)}>
      {/* Page header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
          {description && (
            <p className="text-muted-foreground">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>

      {/* Page content */}
      <div className="flex-1">{children}</div>
    </div>
  );
}

/**
 * Page section component.
 * Used for grouping related content within a page.
 */
interface PageSectionProps {
  /** Section title */
  title?: string;
  /** Section description */
  description?: string;
  /** Section content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

export function PageSection({
  title,
  description,
  children,
  className,
}: PageSectionProps) {
  return (
    <section className={cn('space-y-4', className)}>
      {(title || description) && (
        <div className="space-y-1">
          {title && <h2 className="text-lg font-semibold">{title}</h2>}
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
      )}
      {children}
    </section>
  );
}

/**
 * Loading state component.
 * Displays a centered loading spinner.
 */
export function PageLoading() {
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  );
}

/**
 * Error state component.
 * Displays an error message with optional retry action.
 */
interface PageErrorProps {
  /** Error message to display */
  message?: string;
  /** Retry callback */
  onRetry?: () => void;
}

export function PageError({
  message = 'Ocorreu um erro ao carregar os dados.',
  onRetry,
}: PageErrorProps) {
  return (
    <div className="flex h-64 flex-col items-center justify-center gap-4 text-center">
      <p className="text-muted-foreground">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm font-medium text-primary hover:underline"
        >
          Tentar novamente
        </button>
      )}
    </div>
  );
}

/**
 * Empty state component.
 * Displays a message when there's no data.
 */
interface PageEmptyProps {
  /** Message to display */
  message?: string;
  /** Optional icon */
  icon?: ReactNode;
  /** Optional action */
  action?: ReactNode;
}

export function PageEmpty({
  message = 'Nenhum item encontrado.',
  icon,
  action,
}: PageEmptyProps) {
  return (
    <div className="flex h-64 flex-col items-center justify-center gap-4 text-center">
      {icon && <div className="text-muted-foreground">{icon}</div>}
      <p className="text-muted-foreground">{message}</p>
      {action}
    </div>
  );
}
