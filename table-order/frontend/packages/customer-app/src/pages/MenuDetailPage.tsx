import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Box, Typography, Button, Checkbox, Radio, FormControlLabel, FormGroup, Chip, Divider } from '@mui/material';
import { Loading, PriceDisplay, QuantityControl, useToast, type SelectedOption, type OptionGroup } from '@table-order/shared';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import { getMenus, getMenuOptions } from '../api/menuApi';

export default function MenuDetailPage() {
  const { menuId } = useParams<{ menuId: string }>();
  const navigate = useNavigate();
  const { storeId } = useAuth();
  const { addItem } = useCart();
  const { showToast } = useToast();

  const [selectedOptions, setSelectedOptions] = useState<Map<string, SelectedOption[]>>(new Map());
  const [quantity, setQuantity] = useState(1);

  const { data: menus = [] } = useQuery({
    queryKey: ['menus', storeId],
    queryFn: () => getMenus(storeId!),
    enabled: !!storeId,
    staleTime: 5 * 60 * 1000,
  });

  const { data: optionGroups = [], isLoading } = useQuery({
    queryKey: ['options', menuId],
    queryFn: () => getMenuOptions(menuId!),
    enabled: !!menuId,
  });

  const menuItem = menus.find((m) => m.id === menuId);

  const allSelectedOptions = useMemo(() => {
    return Array.from(selectedOptions.values()).flat();
  }, [selectedOptions]);

  const totalPrice = useMemo(() => {
    if (!menuItem) return 0;
    const optionsTotal = allSelectedOptions.reduce((sum, opt) => sum + opt.additionalPrice, 0);
    return (menuItem.price + optionsTotal) * quantity;
  }, [menuItem, allSelectedOptions, quantity]);

  const isValid = useMemo(() => {
    return optionGroups.every((group) => {
      if (!group.isRequired) return true;
      const selected = selectedOptions.get(group.id) || [];
      return selected.length >= group.minSelections;
    });
  }, [optionGroups, selectedOptions]);

  const handleOptionToggle = (group: OptionGroup, optionId: string, optionName: string, price: number) => {
    setSelectedOptions((prev) => {
      const newMap = new Map(prev);
      const current = newMap.get(group.id) || [];
      const exists = current.find((o) => o.optionId === optionId);

      if (exists) {
        newMap.set(group.id, current.filter((o) => o.optionId !== optionId));
      } else {
        if (current.length >= group.maxSelections) {
          showToast({ message: `최대 ${group.maxSelections}개까지 선택 가능합니다`, severity: 'warning' });
          return prev;
        }
        newMap.set(group.id, [...current, {
          groupId: group.id,
          groupName: group.name,
          optionId,
          optionName,
          additionalPrice: price,
        }]);
      }
      return newMap;
    });
  };

  const handleAddToCart = () => {
    if (!menuItem || !isValid) return;
    addItem({ ...menuItem, optionGroups }, allSelectedOptions, quantity);
    showToast({ message: '장바구니에 추가되었습니다', severity: 'success' });
    navigate('/menu');
  };

  if (isLoading || !menuItem) return <Loading />;

  return (
    <Box data-testid="menu-detail-page" sx={{ p: 2, pb: 12 }}>
      {menuItem.imageUrl && (
        <Box component="img" src={menuItem.imageUrl} alt={menuItem.name}
          sx={{ width: '100%', maxHeight: 250, objectFit: 'cover', borderRadius: 2, mb: 2 }} />
      )}
      <Typography variant="h5">{menuItem.name}</Typography>
      {menuItem.description && (
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>{menuItem.description}</Typography>
      )}
      <PriceDisplay amount={menuItem.price} variant="h6" sx={{ mt: 1 }} />

      <Divider sx={{ my: 2 }} />

      {/* 옵션 그룹 */}
      {optionGroups.map((group) => (
        <Box key={group.id} sx={{ mb: 3 }} data-testid={`option-group-${group.id}`}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Typography variant="subtitle1" fontWeight="bold">{group.name}</Typography>
            {group.isRequired && <Chip label="필수" size="small" color="error" />}
          </Box>
          <FormGroup>
            {group.options.map((option) => {
              const isSelected = (selectedOptions.get(group.id) || []).some((o) => o.optionId === option.id);
              return (
                <FormControlLabel
                  key={option.id}
                  control={
                    group.maxSelections === 1
                      ? <Radio checked={isSelected} onChange={() => handleOptionToggle(group, option.id, option.name, option.additionalPrice)} />
                      : <Checkbox checked={isSelected} onChange={() => handleOptionToggle(group, option.id, option.name, option.additionalPrice)} />
                  }
                  label={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                      <span>{option.name}</span>
                      {option.additionalPrice > 0 && <Typography color="primary">+₩{option.additionalPrice.toLocaleString()}</Typography>}
                    </Box>
                  }
                  sx={{ minHeight: 44 }}
                  data-testid={`option-item-${option.id}`}
                />
              );
            })}
          </FormGroup>
        </Box>
      ))}

      {/* 수량 + 담기 버튼 */}
      <Box sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, p: 2, bgcolor: 'background.paper', borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <QuantityControl value={quantity} onChange={setQuantity} />
          <PriceDisplay amount={totalPrice} variant="h6" />
        </Box>
        <Button
          variant="contained"
          fullWidth
          size="large"
          disabled={!isValid}
          onClick={handleAddToCart}
          data-testid="add-to-cart-button"
          sx={{ minHeight: 48 }}
        >
          장바구니 담기
        </Button>
      </Box>
    </Box>
  );
}
