import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Box, Paper, Typography, TextField, Button, Alert } from '@mui/material';
import { Loading } from '@table-order/shared';
import { useAuth } from '../contexts/AuthContext';

const loginSchema = z.object({
  storeIdentifier: z.string().min(1, '매장 식별자를 입력해주세요'),
  username: z.string().min(1, '사용자명을 입력해주세요'),
  password: z.string().min(1, '비밀번호를 입력해주세요'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setError(null);
    setIsSubmitting(true);
    try {
      await login(data.storeIdentifier, data.username, data.password);
    } catch (err: unknown) {
      const axiosError = err as { response?: { status: number } };
      if (axiosError.response?.status === 401) {
        setError('아이디 또는 비밀번호가 올바르지 않습니다');
      } else if (axiosError.response?.status === 429) {
        setError('로그인 시도 제한을 초과했습니다. 잠시 후 다시 시도해주세요.');
      } else {
        setError('로그인에 실패했습니다. 다시 시도해주세요.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box data-testid="login-page" sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', bgcolor: 'grey.100' }}>
      <Paper sx={{ p: 4, width: '100%', maxWidth: 400 }}>
        <Typography variant="h5" textAlign="center" sx={{ mb: 3 }}>
          테이블오더 관리자
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }} data-testid="login-error">{error}</Alert>}

        <form onSubmit={handleSubmit(onSubmit)}>
          <TextField
            {...register('storeIdentifier')}
            label="매장 식별자"
            fullWidth
            margin="normal"
            error={!!errors.storeIdentifier}
            helperText={errors.storeIdentifier?.message}
            data-testid="login-store-input"
          />
          <TextField
            {...register('username')}
            label="사용자명"
            fullWidth
            margin="normal"
            error={!!errors.username}
            helperText={errors.username?.message}
            data-testid="login-username-input"
          />
          <TextField
            {...register('password')}
            label="비밀번호"
            type="password"
            fullWidth
            margin="normal"
            error={!!errors.password}
            helperText={errors.password?.message}
            data-testid="login-password-input"
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            size="large"
            disabled={isSubmitting}
            sx={{ mt: 2, minHeight: 48 }}
            data-testid="login-submit-button"
          >
            {isSubmitting ? <Loading size={24} /> : '로그인'}
          </Button>
        </form>
      </Paper>
    </Box>
  );
}
