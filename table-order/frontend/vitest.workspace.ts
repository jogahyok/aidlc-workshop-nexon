import { defineWorkspace } from 'vitest/config';

export default defineWorkspace([
  'packages/shared/vitest.config.ts',
  'packages/customer-app/vitest.config.ts',
  'packages/admin-app/vitest.config.ts',
]);
