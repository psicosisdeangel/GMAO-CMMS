import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { authApi } from '../../api/auth';
import { useAuth } from '../../hooks/useAuth';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';

const loginSchema = z.object({
  username: z.string().min(1, 'El usuario es obligatorio'),
  password: z.string().min(1, 'La contraseña es obligatoria'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isSupervisor } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const onSubmit = async (formData: LoginFormData) => {
    // Manual zod validation
    const result = loginSchema.safeParse(formData);
    if (!result.success) {
      setError('Datos de formulario inválidos');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await authApi.login(
        formData.username,
        formData.password
      );
      login(response.user, response.access, response.refresh);
      // Redirect based on role
      if (response.user.rol === 'SUPERVISOR') {
        navigate('/dashboard');
      } else {
        navigate('/work-orders');
      }
    } catch (err: unknown) {
      const axiosError = err as {
        response?: { data?: { detail?: string; non_field_errors?: string[] } };
      };
      const msg =
        axiosError.response?.data?.detail ||
        axiosError.response?.data?.non_field_errors?.[0] ||
        'Credenciales incorrectas. Intente nuevamente.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Avoid unused variable warning
  void isSupervisor;

  return (
    <div className="login-form">
      <h2 className="login-title">Iniciar Sesión</h2>

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
            placeholder="Ingrese su usuario"
            autoComplete="username"
            {...register('username')}
          />
          {errors.username && (
            <span className="form-error">{errors.username.message}</span>
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
            placeholder="Ingrese su contraseña"
            autoComplete="current-password"
            {...register('password')}
          />
          {errors.password && (
            <span className="form-error">{errors.password.message}</span>
          )}
        </div>

        <Button
          type="submit"
          variant="primary"
          loading={loading}
          className="btn-full"
        >
          Ingresar al Sistema
        </Button>
      </form>

      <p className="login-footer">
        Sistema GMAO — Gestión de Mantenimiento Industrial
      </p>
      <p style={{ textAlign: 'center', marginTop: '0.75rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
        ¿No tienes cuenta?{' '}
        <a href="/register" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
          Regístrate aquí
        </a>
      </p>
    </div>
  );
};
