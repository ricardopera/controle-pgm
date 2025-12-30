/**
 * History page component.
 */

import { PageContainer } from '@/components/layout';
import { HistoryTable } from '@/components/features/HistoryTable';

export function HistoryPage() {
  return (
    <PageContainer
      title="Histórico"
      description="Visualize o histórico de números gerados e correções realizadas."
    >
      <HistoryTable />
    </PageContainer>
  );
}
