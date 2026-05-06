import { Box, IconButton, Typography } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';

interface QuantityControlProps {
  value: number;
  min?: number;
  max?: number;
  onChange: (newValue: number) => void;
}

export function QuantityControl({ value, min = 1, max = 99, onChange }: QuantityControlProps) {
  const handleDecrease = () => {
    if (value > min) {
      onChange(value - 1);
    }
  };

  const handleIncrease = () => {
    if (value < max) {
      onChange(value + 1);
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }} data-testid="quantity-control">
      <IconButton
        onClick={handleDecrease}
        disabled={value <= min}
        size="small"
        aria-label="수량 감소"
        data-testid="quantity-decrease"
        sx={{ minWidth: 44, minHeight: 44 }}
      >
        <RemoveIcon />
      </IconButton>
      <Typography
        variant="body1"
        sx={{ minWidth: 32, textAlign: 'center' }}
        data-testid="quantity-value"
      >
        {value}
      </Typography>
      <IconButton
        onClick={handleIncrease}
        disabled={value >= max}
        size="small"
        aria-label="수량 증가"
        data-testid="quantity-increase"
        sx={{ minWidth: 44, minHeight: 44 }}
      >
        <AddIcon />
      </IconButton>
    </Box>
  );
}
