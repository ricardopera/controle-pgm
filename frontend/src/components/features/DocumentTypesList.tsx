import { useState, useEffect } from 'react';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { DocumentType, DocumentTypesListResponse } from '@/types';

interface DocumentTypeFormData {
  code: string;
  name: string;
}

export function DocumentTypesList() {
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Dialog states
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Form state
  const [formData, setFormData] = useState<DocumentTypeFormData>({ code: '', name: '' });
  const [formError, setFormError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<DocumentType | null>(null);

  useEffect(() => {
    loadDocumentTypes();
  }, []);

  async function loadDocumentTypes() {
    try {
      setLoading(true);
      const response = await api.get<DocumentTypesListResponse>('/document-types?all=true');
      setDocumentTypes(response.items);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar tipos de documento';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  function handleAddClick() {
    setFormData({ code: '', name: '' });
    setFormError(null);
    setShowAddDialog(true);
  }

  function handleEditClick(type: DocumentType) {
    setSelectedType(type);
    setFormData({ code: type.code, name: type.name });
    setFormError(null);
    setShowEditDialog(true);
  }

  async function handleToggleActive(type: DocumentType) {
    try {
      if (type.is_active) {
        await api.delete(`/document-types/${type.id}`);
        toast.success(`Tipo "${type.name}" desativado!`);
      } else {
        await api.put(`/document-types/${type.id}`, { is_active: true });
        toast.success(`Tipo "${type.name}" ativado!`);
      }
      await loadDocumentTypes();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao alterar status';
      toast.error(message);
    }
  }

  async function handleAddSubmit() {
    if (!formData.code.trim() || !formData.name.trim()) {
      setFormError('Código e nome são obrigatórios');
      return;
    }

    if (formData.code.length > 10) {
      setFormError('Código deve ter no máximo 10 caracteres');
      return;
    }

    try {
      setSaving(true);
      setFormError(null);

      await api.post('/document-types', {
        code: formData.code.toUpperCase().trim(),
        name: formData.name.trim(),
      });

      toast.success('Tipo de documento criado com sucesso!');
      setShowAddDialog(false);
      await loadDocumentTypes();
    } catch (err) {
      const message =
        err instanceof ApiError
          ? (err.data?.error as string) || 'Erro ao criar tipo de documento'
          : 'Erro ao criar tipo de documento';
      setFormError(message);
    } finally {
      setSaving(false);
    }
  }

  async function handleEditSubmit() {
    if (!selectedType) return;

    if (!formData.name.trim()) {
      setFormError('Nome é obrigatório');
      return;
    }

    try {
      setSaving(true);
      setFormError(null);

      await api.put(`/document-types/${selectedType.id}`, {
        name: formData.name.trim(),
      });

      toast.success('Tipo de documento atualizado com sucesso!');
      setShowEditDialog(false);
      await loadDocumentTypes();
    } catch (err) {
      const message =
        err instanceof ApiError
          ? (err.data?.error as string) || 'Erro ao atualizar tipo de documento'
          : 'Erro ao atualizar tipo de documento';
      setFormError(message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteConfirm() {
    if (!selectedType) return;

    try {
      setSaving(true);
      await api.delete(`/document-types/${selectedType.id}`);

      toast.success(`Tipo "${selectedType.name}" desativado!`);
      setShowDeleteDialog(false);
      await loadDocumentTypes();
    } catch (err) {
      const message =
        err instanceof ApiError
          ? (err.data?.error as string) || 'Erro ao desativar tipo de documento'
          : 'Erro ao desativar tipo de documento';
      toast.error(message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-lg font-medium">Tipos de Documento</CardTitle>
          <Button onClick={handleAddClick}>
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
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Adicionar Tipo
          </Button>
        </CardHeader>

        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Nome</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Criado em</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={5} className="h-24 text-center">
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
                ) : documentTypes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="h-24 text-center">
                      Nenhum tipo de documento cadastrado.
                    </TableCell>
                  </TableRow>
                ) : (
                  documentTypes.map((type) => (
                    <TableRow key={type.id}>
                      <TableCell>
                        <Badge variant="outline" className="font-mono">
                          {type.code}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium">{type.name}</TableCell>
                      <TableCell>
                        {type.is_active ? (
                          <Badge variant="default">Ativo</Badge>
                        ) : (
                          <Badge variant="secondary">Inativo</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatDate(type.created_at)}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditClick(type)}
                          >
                            Editar
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleActive(type)}
                          >
                            {type.is_active ? 'Desativar' : 'Ativar'}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Add Dialog */}
      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Adicionar Tipo de Documento</DialogTitle>
            <DialogDescription>
              Preencha os dados do novo tipo de documento.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {formError && (
              <Alert variant="destructive">
                <AlertDescription>{formError}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="add-code">Código</Label>
              <Input
                id="add-code"
                placeholder="Ex: OF, MEM, PAR"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                maxLength={10}
                disabled={saving}
              />
              <p className="text-xs text-muted-foreground">
                Código curto de 2-10 caracteres (será convertido para maiúsculas)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="add-name">Nome</Label>
              <Input
                id="add-name"
                placeholder="Ex: Ofício, Memorando, Parecer"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                disabled={saving}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddDialog(false)} disabled={saving}>
              Cancelar
            </Button>
            <Button onClick={handleAddSubmit} disabled={saving}>
              {saving ? 'Salvando...' : 'Adicionar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Tipo de Documento</DialogTitle>
            <DialogDescription>
              Altere o nome do tipo de documento. O código não pode ser alterado.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {formError && (
              <Alert variant="destructive">
                <AlertDescription>{formError}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label>Código</Label>
              <div className="flex items-center rounded-md border bg-muted px-3 py-2">
                <span className="font-mono">{selectedType?.code}</span>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-name">Nome</Label>
              <Input
                id="edit-name"
                placeholder="Ex: Ofício, Memorando, Parecer"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                disabled={saving}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)} disabled={saving}>
              Cancelar
            </Button>
            <Button onClick={handleEditSubmit} disabled={saving}>
              {saving ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Desativar Tipo de Documento</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja desativar o tipo "{selectedType?.name}"?
              Os números já gerados serão mantidos.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={saving}
            >
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={saving}
            >
              {saving ? 'Desativando...' : 'Desativar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
