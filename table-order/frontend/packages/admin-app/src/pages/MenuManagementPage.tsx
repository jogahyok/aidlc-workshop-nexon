import { Box, Typography } from '@mui/material';
import { EmptyState } from '@table-order/shared';
import RestaurantMenuIcon from '@mui/icons-material/RestaurantMenu';

/**
 * 메뉴 관리 페이지 (US-10)
 * TODO: 카테고리 사이드바, 메뉴 목록, 추가/수정/삭제, 순서 조정 구현
 */
export default function MenuManagementPage() {
  return (
    <Box data-testid="menu-management-page">
      <Typography variant="h5" sx={{ mb: 3 }}>메뉴 관리</Typography>
      <EmptyState
        icon={<RestaurantMenuIcon />}
        title="메뉴 관리 기능"
        description="백엔드 API 연동 후 구현 예정 (메뉴 CRUD, 옵션 관리, 이미지 업로드)"
      />
    </Box>
  );
}
