import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Box, Tabs, Tab, Grid, Card, CardMedia, CardContent, Typography, Skeleton } from '@mui/material';
import { PriceDisplay } from '@table-order/shared';
import { useAuth } from '../contexts/AuthContext';
import { getCategories, getMenus } from '../api/menuApi';

export default function MenuPage() {
  const { storeId } = useAuth();
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const { data: categories = [] } = useQuery({
    queryKey: ['categories', storeId],
    queryFn: () => getCategories(storeId!),
    enabled: !!storeId,
    staleTime: 5 * 60 * 1000,
  });

  const { data: menus = [], isLoading } = useQuery({
    queryKey: ['menus', storeId, selectedCategory],
    queryFn: () => getMenus(storeId!, selectedCategory || undefined),
    enabled: !!storeId,
    staleTime: 5 * 60 * 1000,
  });

  // 첫 카테고리 자동 선택
  if (categories.length > 0 && !selectedCategory) {
    setSelectedCategory(categories[0].id);
  }

  return (
    <Box data-testid="menu-page" sx={{ pb: 8 }}>
      {/* 카테고리 탭 */}
      <Tabs
        value={selectedCategory}
        onChange={(_, value) => setSelectedCategory(value)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
        data-testid="category-tabs"
      >
        {categories.map((cat) => (
          <Tab key={cat.id} label={cat.name} value={cat.id} sx={{ minHeight: 44 }} />
        ))}
      </Tabs>

      {/* 메뉴 그리드 */}
      <Grid container spacing={2} sx={{ px: 2 }}>
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => (
              <Grid item xs={6} sm={4} key={i}>
                <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
              </Grid>
            ))
          : menus.map((menu) => (
              <Grid item xs={6} sm={4} key={menu.id}>
                <Card
                  onClick={() => navigate(`/menu/${menu.id}`)}
                  sx={{ cursor: 'pointer', height: '100%', minHeight: 44 }}
                  data-testid={`menu-card-${menu.id}`}
                >
                  {menu.imageUrl && (
                    <CardMedia
                      component="img"
                      height="140"
                      image={menu.imageUrl}
                      alt={menu.name}
                      loading="lazy"
                    />
                  )}
                  <CardContent>
                    <Typography variant="subtitle1" noWrap>
                      {menu.name}
                    </Typography>
                    {menu.description && (
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {menu.description}
                      </Typography>
                    )}
                    <PriceDisplay amount={menu.price} variant="body1" color="primary" />
                  </CardContent>
                </Card>
              </Grid>
            ))}
      </Grid>
    </Box>
  );
}
