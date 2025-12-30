import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { DocumentType, NumberLog, HistoryResponse } from '@/types';

interface HistoryTableProps {
  onExport?: () => void;
}

export function HistoryTable({ onExport }: HistoryTableProps) {
  const [history, setHistory] = useState<NumberLog[]>([]);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Filters
  const [filterType, setFilterType] = useState<string>('');
  const [filterYear, setFilterYear] = useState<string>('');
  const [filterAction, setFilterAction] = useState<string>('');

  // Year options
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 5 }, (_, i) => currentYear - i);

  const loadHistory = useCallback(async () => {
    try {
      setLoading(true);

      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('page_size', pageSize.toString());

      if (filterType) params.append('document_type_code', filterType);
      if (filterYear) params.append('year', filterYear);
      if (filterAction) params.append('action', filterAction);

      const response = await api.get<HistoryResponse>(`/api/history?${params.toString()}`);

      setHistory(response.items);
      setTotalPages(response.total_pages);
      setTotal(response.total);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar histórico';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, filterType, filterYear, filterAction]);

  const loadDocumentTypes = async () => {
    try {
      const response = await api.get<DocumentType[]>('/api/document-types?all=true');
      setDocumentTypes(response);
    } catch {
      // Silently fail - filters will just not show types
    }
  };

  useEffect(() => {
    loadDocumentTypes();
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleFilterChange = () => {
    setPage(1);
  };

  const handleExport = async () => {
    try {
      setExporting(true);

      const params = new URLSearchParams();
      if (filterType) params.append('document_type_code', filterType);
      if (filterYear) params.append('year', filterYear);
      if (filterAction) params.append('action', filterAction);

      const response = await fetch(`/api/history/export?${params.toString()}`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Erro ao exportar histórico');
      }

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'historico.csv';
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/);
        if (match) filename = match[1];
      }

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success('Exportação concluída!');
      onExport?.();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao exportar';
      toast.error(message);
    } finally {
      setExporting(false);
    }
  };

  const clearFilters = () => {
    setFilterType('');
    setFilterYear('');
    setFilterAction('');
    setPage(1);
  };

  const getActionBadge = (action: string) => {
    if (action === 'generated') {
      return <Badge variant="default">Gerado</Badge>;
    }
    return <Badge variant="secondary">Corrigido</Badge>;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-medium">Histórico de Numeração</CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={handleExport}
          disabled={exporting || loading}
        >
          {exporting ? (
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
              Exportando...
            </>
          ) : (
            <>
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
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Exportar CSV
            </>
          )}
        </Button>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filters */}
        <div className="grid gap-4 md:grid-cols-4">
          <div className="space-y-2">
            <Label htmlFor="filter-type">Tipo de Documento</Label>
            <Select
              value={filterType}
              onValueChange={(value: string) => {
                setFilterType(value === 'all' ? '' : value);
                handleFilterChange();
              }}
            >
              <SelectTrigger id="filter-type">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                {documentTypes.map((type) => (
                  <SelectItem key={type.code} value={type.code}>
                    {type.code} - {type.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="filter-year">Ano</Label>
            <Select
              value={filterYear}
              onValueChange={(value: string) => {
                setFilterYear(value === 'all' ? '' : value);
                handleFilterChange();
              }}
            >
              <SelectTrigger id="filter-year">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                {yearOptions.map((year) => (
                  <SelectItem key={year} value={year.toString()}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="filter-action">Ação</Label>
            <Select
              value={filterAction}
              onValueChange={(value: string) => {
                setFilterAction(value === 'all' ? '' : value);
                handleFilterChange();
              }}
            >
              <SelectTrigger id="filter-action">
                <SelectValue placeholder="Todas" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                <SelectItem value="generated">Gerado</SelectItem>
                <SelectItem value="corrected">Corrigido</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-end">
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="w-full"
            >
              Limpar Filtros
            </Button>
          </div>
        </div>

        {/* Results summary */}
        <div className="text-sm text-muted-foreground">
          {loading ? 'Carregando...' : `${total} registro(s) encontrado(s)`}
        </div>

        {/* Table */}
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Data/Hora</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Número</TableHead>
                <TableHead>Ano</TableHead>
                <TableHead>Ação</TableHead>
                <TableHead>Usuário</TableHead>
                <TableHead>Observações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-24 text-center">
                    <div className="flex items-center justify-center">
                      <svg
                        className="h-6 w-6 animate-spin text-muted-foreground"
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
                    </div>
                  </TableCell>
                </TableRow>
              ) : history.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-24 text-center">
                    Nenhum registro encontrado.
                  </TableCell>
                </TableRow>
              ) : (
                history.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="whitespace-nowrap">
                      {formatDate(log.created_at)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="font-mono">
                        {log.document_type_code}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono font-medium">
                      {log.number.toString().padStart(4, '0')}
                    </TableCell>
                    <TableCell>{log.year}</TableCell>
                    <TableCell>{getActionBadge(log.action)}</TableCell>
                    <TableCell>{log.user_name}</TableCell>
                    <TableCell className="max-w-[200px] truncate">
                      {log.action === 'corrected' && log.previous_number && (
                        <span className="text-muted-foreground">
                          Anterior: {log.previous_number}
                          {log.notes && ` - ${log.notes}`}
                        </span>
                      )}
                      {log.action === 'generated' && '-'}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Página {page} de {totalPages}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1 || loading}
              >
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages || loading}
              >
                Próxima
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
