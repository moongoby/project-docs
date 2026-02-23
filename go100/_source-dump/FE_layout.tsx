// CUR-GO100-HOTFIX-006, 2026-02-23 — prerender 비활성화(force-dynamic), 클라이언트 UI는 ProtectedLayoutClient로
// CUR-GO100-HOTFIX-005, CUR-GO100-FINAL-FIX-001, CUR-GO100-HOTFIX-SAVE-500, CUR-GO100-PHASE2-STABILIZE STEP1
// CUR-GO100-HOTFIX-CRITICAL, CUR-GO100-UNIFIED-SAVE-FE, CUR-GO100-CHAT-WIDGET
// Modified by CUR-SIDEBAR-NAV-v1, CUR-NOTIFICATION-SYSTEM-v1, CUR-UI-AUDIT-FIX-v1, CUR-NOTIFICATION-UI-v1

export const dynamic = "force-dynamic";

import ProtectedLayoutClient from "./ProtectedLayoutClient";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <ProtectedLayoutClient>{children}</ProtectedLayoutClient>;
}
