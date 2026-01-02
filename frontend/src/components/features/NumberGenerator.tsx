import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import type { DocumentType, DocumentTypesListResponse, GeneratedNumber } from '@/types';

export function NumberGenerator() {
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [loading, setLoading] = useState(false);
  const [loadingTypes, setLoadingTypes] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Confirm modal state
  const [showConfirm, setShowConfirm] = useState(false);

  // Success modal state
  const [showSuccess, setShowSuccess] = useState(false);
  const [generatedNumber, setGeneratedNumber] = useState<GeneratedNumber | null>(null);
  const [copied, setCopied] = useState(false);

  // Generate year options (current year only)
  const currentYear = new Date().getFullYear();
  const yearOptions = [currentYear];

  const loadDocumentTypes = useCallback(async () => {
    try {
      setLoadingTypes(true);
      setError(null);
      const response = await api.get<DocumentTypesListResponse>('/document-types');
      setDocumentTypes(response.items);
      
      // Auto-select first type if available
      if (response.items.length > 0 && !selectedType) {
        setSelectedType(response.items[0].code);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar tipos de documento';
      setError(message);
      toast.error(message);
    } finally {
      setLoadingTypes(false);
    }
  }, [selectedType]);

  // Load document types on mount
  useEffect(() => {
    loadDocumentTypes();
  }, [loadDocumentTypes]);

  function handleGenerateClick() {
    if (!selectedType) {
      toast.error('Selecione um tipo de documento');
      return;
    }
    setShowConfirm(true);
  }

  async function handleConfirmGenerate() {
    if (!selectedType) return;

    try {
      setLoading(true);
      setError(null);
      setShowConfirm(false);

      const response = await api.post<GeneratedNumber>('/numbers/generate', {
        document_type_code: selectedType,
        year: selectedYear,
      });

      setGeneratedNumber(response);
      setShowSuccess(true);
      setCopied(false);
      toast.success('Número gerado com sucesso!');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao gerar número';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCopyNumber() {
    if (!generatedNumber) return;

    try {
      await navigator.clipboard.writeText(generatedNumber.formatted);
      setCopied(true);
      toast.success('Número copiado para a área de transferência!');
      
      // Reset copied state after 2 seconds
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for browsers that don't support clipboard API
      const textArea = document.createElement('textarea');
      textArea.value = generatedNumber.formatted;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        setCopied(true);
        toast.success('Número copiado para a área de transferência!');
        setTimeout(() => setCopied(false), 2000);
      } catch {
        toast.error('Erro ao copiar número');
      }
      document.body.removeChild(textArea);
    }
  }

  function handleCloseSuccess() {
    setShowSuccess(false);
    setGeneratedNumber(null);
    setCopied(false);
  }

  function getSelectedTypeName(): string {
    const type = documentTypes.find((t) => t.code === selectedType);
    return type ? type.name : selectedType;
  }

  return (
    <>
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
            >
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="12" y1="18" x2="12" y2="12" />
              <line x1="9" y1="15" x2="15" y2="15" />
            </svg>
            Gerar Número
          </CardTitle>
          <CardDescription>
            Selecione o tipo de documento e o ano para gerar um novo número sequencial.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="document-type">Tipo de Documento</Label>
            <Select
              value={selectedType}
              onValueChange={setSelectedType}
              disabled={loadingTypes || loading}
            >
              <SelectTrigger id="document-type" className="w-full">
                <SelectValue placeholder={loadingTypes ? 'Carregando...' : 'Selecione o tipo'} />
              </SelectTrigger>
              <SelectContent>
                {documentTypes.map((type) => (
                  <SelectItem key={type.code} value={type.code}>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono">
                        {type.code}
                      </Badge>
                      <span>{type.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="year">Ano</Label>
            <Select
              value={selectedYear.toString()}
              onValueChange={(v: string) => setSelectedYear(parseInt(v, 10))}
              disabled={loading}
            >
              <SelectTrigger id="year" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {yearOptions.map((year) => (
                  <SelectItem key={year} value={year.toString()}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button
            onClick={handleGenerateClick}
            disabled={!selectedType || loading || loadingTypes}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <svg
                  className="mr-2 h-4 w-4 animate-spin"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Gerando...
              </>
            ) : (
              'Gerar Número'
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Confirmation Modal */}
      <Dialog open={showConfirm} onOpenChange={setShowConfirm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Geração</DialogTitle>
            <DialogDescription>
              Você está prestes a gerar um novo número sequencial. Esta ação não pode ser desfeita.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2 rounded-lg bg-muted p-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Tipo:</span>
              <span className="font-medium">{getSelectedTypeName()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Código:</span>
              <Badge variant="outline" className="font-mono">
                {selectedType}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Ano:</span>
              <span className="font-medium">{selectedYear}</span>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirm(false)}>
              Cancelar
            </Button>
            <Button onClick={handleConfirmGenerate}>Confirmar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Success Modal */}
      <Dialog open={showSuccess} onOpenChange={handleCloseSuccess}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-green-600">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-5 w-5"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
              Número Gerado com Sucesso!
            </DialogTitle>
            <DialogDescription>
              O número foi gerado e registrado no sistema. Clique para copiar.
            </DialogDescription>
          </DialogHeader>

          {generatedNumber && (
            <div className="space-y-4">
              {/* Main number display */}
              <button
                onClick={handleCopyNumber}
                className="w-full rounded-lg border-2 border-dashed border-primary/50 bg-primary/5 p-6 text-center transition-colors hover:border-primary hover:bg-primary/10"
              >
                <div className="text-3xl font-bold tracking-wider text-primary">
                  {generatedNumber.formatted}
                </div>
                <div className="mt-2 text-sm text-muted-foreground">
                  {copied ? (
                    <span className="text-green-600">✓ Copiado!</span>
                  ) : (
                    'Clique para copiar'
                  )}
                </div>
              </button>

              {/* Details */}
              <div className="space-y-2 rounded-lg bg-muted p-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Tipo:</span>
                  <span>{generatedNumber.document_type_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Número:</span>
                  <span className="font-mono">{generatedNumber.number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ano:</span>
                  <span>{generatedNumber.year}</span>
                </div>
              </div>
            </div>
          )}

          <DialogFooter className="flex-col gap-2 sm:flex-row">
            <Button variant="outline" onClick={handleCopyNumber} className="flex-1">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="mr-2 h-4 w-4"
              >
                <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
              </svg>
              {copied ? 'Copiado!' : 'Copiar'}
            </Button>
            <Button onClick={handleCloseSuccess} className="flex-1">
              Fechar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
