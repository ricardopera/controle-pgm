/**
 * Home/Dashboard page component.
 */

import { PageContainer } from '@/components/layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { NumberGenerator } from '@/components/features/NumberGenerator';
import { useAuth } from '@/lib/auth-context';

export function HomePage() {
  const { user } = useAuth();

  return (
    <PageContainer
      title="Início"
      description={`Bem-vindo(a), ${user?.name}!`}
    >
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Main action - Number Generator */}
        <div className="lg:col-span-1">
          <NumberGenerator />
        </div>

        {/* Info cards */}
        <div className="space-y-4 lg:col-span-1">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Sistema
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-semibold">Controle PGM</p>
              <p className="text-sm text-muted-foreground">
                Sistema de controle de numeração sequencial de documentos da
                Procuradoria-Geral do Município de Itajaí.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Instruções
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm text-muted-foreground">
                <strong>1.</strong> Selecione o tipo de documento desejado
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>2.</strong> Confirme o ano da numeração
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>3.</strong> Clique em "Gerar Número"
              </p>
              <p className="text-sm text-muted-foreground">
                <strong>4.</strong> Copie o número gerado para usar em seu documento
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Ajuda
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-semibold">Suporte</p>
              <p className="text-sm text-muted-foreground">
                Em caso de dúvidas ou problemas, entre em contato com a equipe de TI.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
