import { Box, Typography } from '@mui/material';
import { EmptyState } from '@table-order/shared';
import TableBarIcon from '@mui/icons-material/TableBar';

/**
 * 테이블 관리 페이지 (US-09)
 * TODO: 테이블 목록, 추가, 이용 완료, 과거 내역 조회 구현
 */
export default function TableManagementPage() {
  return (
    <Box data-testid="table-management-page">
      <Typography variant="h5" sx={{ mb: 3 }}>테이블 관리</Typography>
      <EmptyState
        icon={<TableBarIcon />}
        title="테이블 관리 기능"
        description="백엔드 API 연동 후 구현 예정 (테이블 CRUD, 세션 관리, 과거 내역)"
      />
    </Box>
  );
}
