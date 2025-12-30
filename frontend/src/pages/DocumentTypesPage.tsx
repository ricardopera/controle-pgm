/**
 * Document Types settings page component.
 */

import { PageContainer } from '@/components/layout';
import { DocumentTypesList } from '@/components/features/DocumentTypesList';

export function DocumentTypesPage() {
  return (
    <PageContainer
      title="Tipos de Documento"
      description="Gerencie os tipos de documentos disponíveis para geração de números."
    >
      <DocumentTypesList />
    </PageContainer>
  );
}
