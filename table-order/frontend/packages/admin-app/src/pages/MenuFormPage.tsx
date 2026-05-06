import { Box, Typography } from '@mui/material';

/**
 * 메뉴 등록/수정 폼 페이지 (US-10)
 * TODO: React Hook Form + Zod 검증, 이미지 업로드, 옵션 그룹 에디터 구현
 */
export default function MenuFormPage() {
  return (
    <Box data-testid="menu-form-page">
      <Typography variant="h5" sx={{ mb: 3 }}>메뉴 등록/수정</Typography>
      <Typography color="text.secondary">
        백엔드 API 연동 후 구현 예정
      </Typography>
    </Box>
  );
}
