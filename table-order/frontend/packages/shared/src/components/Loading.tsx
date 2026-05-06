import { Box, CircularProgress } from '@mui/material';

interface LoadingProps {
  size?: number;
  fullScreen?: boolean;
}

export function Loading({ size = 40, fullScreen = false }: LoadingProps) {
  if (fullScreen) {
    return (
      <Box
        data-testid="loading-fullscreen"
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          width: '100vw',
        }}
      >
        <CircularProgress size={size} />
      </Box>
    );
  }

  return (
    <Box
      data-testid="loading-inline"
      sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 4 }}
    >
      <CircularProgress size={size} />
    </Box>
  );
}
