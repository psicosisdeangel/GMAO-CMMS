import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { authApi } from '../../api/auth';
import { useAuth } from '../../hooks/useAuth';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';

const signUpSchema = z
  .object({
    username: z.string().min(3, 'El usuario debe tener al menos 3 caracteres'),
    nombre_completo: z.string().min(2, 'El nombre es obligatorio'),
    email: z.string().email('Correo inválido').optional().or(z.literal('')),
    password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
    confirm_password: z.string().min(1, 'Confirme su contraseña'),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: 'Las contraseñas no coinciden',
    path: ['confirm_password'],
  });

type SignUpFormData = z.infer<typeof signUpSchema>;

export const SignUpPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignUpFormData>();

  const onSubmit = async (formData: SignUpFormData) => {
    const result = signUpSchema.safeParse(formData);
    if (!result.success) {
      setError('Revise los campos del formulario');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await authApi.register({
        username: formData.username,
        password: formData.password,
        nombre_completo: formData.nombre_completo,
        email: formData.email || undefined,
      });
      login(response.user, response.access, response.refresh);
      navigate('/work-orders');
    } catch (err: unknown) {
      const axiosError = err as {
        response?: { data?: { error?: string; detail?: string } };
      };
      const msg =
        axiosError.response?.data?.error ||
        axiosError.response?.data?.detail ||
        'Error al crear la cuenta. Intente nuevamente.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-form">
      <h2 className="login-title">Crear Cuenta</h2>
      <p style={{ textAlign: 'center', marginBottom: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
        Las cuentas nuevas se crean como <strong>Técnico</strong>. Un supervisor puede cambiar el rol después.
      </p>

      {error && (
        <Alert variant="error" onDismiss={() => setError(null)}>
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <div className="form-group">
          <label htmlFor="username" className="form-label">
            Usuario
          </label>
          <input
            id="username"
            type="text"
            className={`form-input ${errors.username ? 'form-input-error' : ''}`}
            placeholder="Nombre de usuario"
            autoComplete="username"
            {...register('username')}
          />
          {errors.username && (
            <span className="form-error">{errors.username.message}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="nombre_completo" className="form-label">
            Nombre completo
          </label>
          <input
            id="nombre_completo"
            type="text"
            className={`form-input ${errors.nombre_completo ? 'form-input-error' : ''}`}
            placeholder="Tu nombre completo"
            autoComplete="name"
            {...register('nombre_completo')}
          />
          {errors.nombre_completo && (
            <span className="form-error">{errors.nombre_completo.message}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="email" className="form-label">
            Correo electrónico <span style={{ color: 'var(--text-secondary)' }}>(opcional)</span>
          </label>
          <input
            id="email"
            type="email"
            className={`form-input ${errors.email ? 'form-input-error' : ''}`}
            placeholder="correo@ejemplo.com"
            autoComplete="email"
            {...register('email')}
          />
          {errors.email && (
            <span className="form-error">{errors.email.message}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="password" className="form-label">
            Contraseña
          </label>
          <input
            id="password"
            type="password"
            className={`form-input ${errors.password ? 'form-input-error' : ''}`}
            placeholder="Mínimo 8 caracteres"
            autoComplete="new-password"
            {...register('password')}
          />
          {errors.password && (
            <span className="form-error">{errors.password.message}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="confirm_password" className="form-label">
            Confirmar contraseña
          </label>
          <input
            id="confirm_password"
            type="password"
            className={`form-input ${errors.confirm_password ? 'form-input-error' : ''}`}
            placeholder="Repite la contraseña"
            autoComplete="new-password"
            {...register('confirm_password')}
          />
          {errors.confirm_password && (
            <span className="form-error">{errors.confirm_password.message}</span>
          )}
        </div>

        <Button
          type="submit"
          variant="primary"
          loading={loading}
          className="btn-full"
        >
          Crear cuenta
        </Button>
      </form>

      <p style={{ textAlign: 'center', marginTop: '0.75rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
        ¿Ya tienes cuenta?{' '}
        <a href="/login" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
          Inicia sesión
        </a>
      </p>
    </div>
  );
};
