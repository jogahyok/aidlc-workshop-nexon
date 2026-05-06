import { Component, type ReactNode, type ErrorInfo } from 'react';
import { Box, Typography, Button } from '@mui/material';
import { reportError } from '../utils/errorReporter';

interface Props {
  children: ReactNode;
  pageName: string;
}

interface State {
  hasError: boolean;
}

export class PageErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    reportError({
      errorType: 'runtime',
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack ?? undefined,
      context: { pageName: this.props.pageName },
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box
          data-testid="error-boundary-fallback"
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '50vh',
            p: 4,
            textAlign: 'center',
          }}
        >
          <Typography variant="h6" gutterBottom>
            문제가 발생했습니다
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            페이지를 새로고침하거나 다시 시도해주세요.
          </Typography>
          <Button
            variant="contained"
            onClick={this.handleRetry}
            data-testid="error-boundary-retry"
          >
            다시 시도
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
