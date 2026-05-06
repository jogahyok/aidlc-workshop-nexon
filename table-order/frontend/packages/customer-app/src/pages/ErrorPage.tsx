import { Box, Typography, Paper } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

export default function ErrorPage() {
  return (
    <Box
      data-testid="error-page"
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        p: 3,
      }}
    >
      <Paper sx={{ p: 4, textAlign: 'center', maxWidth: 400 }}>
        <ErrorOutlineIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          인증 오류
        </Typography>
        <Typography variant="body1" color="text.secondary">
          테이블 인증 정보가 유효하지 않습니다.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          매장 관리자에게 태블릿 재설정을 요청해주세요.
        </Typography>
      </Paper>
    </Box>
  );
}
