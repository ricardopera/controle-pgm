/**
 * Change Password Dialog component.
 * Shown when user has must_change_password flag set.
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { api, ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';

const changePasswordSchema = z
  .object({
    currentPassword: z.string().min(1, 'Senha atual é obrigatória'),
    newPassword: z
      .string()
      .min(8, 'A nova senha deve ter pelo menos 8 caracteres')
      .regex(/[A-Z]/, 'A nova senha deve conter pelo menos uma letra maiúscula')
      .regex(/[a-z]/, 'A nova senha deve conter pelo menos uma letra minúscula')
      .regex(/[0-9]/, 'A nova senha deve conter pelo menos um número'),
    confirmPassword: z.string().min(1, 'Confirmação de senha é obrigatória'),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: 'As senhas não conferem',
    path: ['confirmPassword'],
  });

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

interface ChangePasswordDialogProps {
  open: boolean;
}

export function ChangePasswordDialog({ open }: ChangePasswordDialogProps) {
  const { updateUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: ChangePasswordFormData) => {
    setError(null);
    setIsLoading(true);

    try {
      await api.post('/api/auth/change-password', {
        current_password: data.currentPassword,
        new_password: data.newPassword,
      });
      updateUser({ must_change_password: false });
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError('Senha atual incorreta');
        } else {
          setError(
            (err.data?.message as string) || 'Erro ao alterar senha'
          );
        }
      } else {
        setError('Erro de conexão. Tente novamente.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open}>
      <DialogContent className="sm:max-w-[425px] [&>button]:hidden">
        <DialogHeader>
          <DialogTitle>Alterar Senha</DialogTitle>
          <DialogDescription>
            Por segurança, você precisa alterar sua senha temporária antes de
            continuar.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <FormField
              control={form.control}
              name="currentPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Senha Atual</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Digite sua senha atual"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="newPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nova Senha</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Digite a nova senha"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirmar Nova Senha</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Confirme a nova senha"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Alterar Senha
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
