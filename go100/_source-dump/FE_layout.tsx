// CUR-GO100-FINAL-FIX-001, 2026-02-23 — ChatWidget 조건부 렌더링 + /llm 제외
// CUR-GO100-HOTFIX-SAVE-500, 2026-02-23
// CUR-GO100-PHASE2-STABILIZE STEP1, 2026-02-23 — ISS-001: ChatWidget 표시 수정
// CUR-GO100-HOTFIX-CRITICAL, 2026-02-23
// CUR-GO100-UNIFIED-SAVE-FE, 2026-02-23
// CUR-GO100-CHAT-WIDGET, 2026-02-22
// Modified by CUR-SIDEBAR-NAV-v1, 2026-02-20
// Modified by CUR-NOTIFICATION-SYSTEM-v1, 2026-02-20 — 알림 unread count API 연동
// Modified by CUR-UI-AUDIT-FIX-v1, 2026-02-20 — h-dvh flex, 스크롤 영역 분리, 모바일 pb/pt
// Modified by CUR-NOTIFICATION-UI-v1, 2026-02-20 — unread count refetch 30초
"use client";

import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import { getUnreadCount } from "@/lib/api/notifications";
import { Sidebar } from "@/components/layout/Sidebar";
import { BottomNav } from "@/components/layout/BottomNav";
import { Header } from "@/components/layout/Header";
import { ChatWidget } from "@/go100/components/ChatWidget";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isLlmPage = pathname === "/llm";
  const { isAuthenticated, isLoading } = useAuth(true);
  const { data: notifData } = useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: getUnreadCount,
    enabled: isAuthenticated,
    refetchInterval: 30000,
  });
  const unreadNotificationCount = notifData?.count ?? 0;

  if (isLoading) {
    return (
      <>
        <div className="flex min-h-screen items-center justify-center bg-gradient-dark">
          <p className="text-muted-foreground">로딩 중...</p>
        </div>
        {/* ISS-001: 로딩 중에도 FAB 노출 (/llm 제외) */}
        {!isLlmPage && <ChatWidget />}
      </>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <div className="flex min-h-screen items-center justify-center bg-gradient-dark">
          <p className="text-muted-foreground">로그인이 필요합니다.</p>
        </div>
        {/* ISS-001: 미인증 시에도 FAB 노출 (/llm 제외) */}
        {!isLlmPage && <ChatWidget />}
      </>
    );
  }

  return (
    <>
      <div className="h-dvh flex bg-gradient-dark">
        {/* Desktop Sidebar */}
        <Sidebar
          className="hidden lg:flex"
          unreadNotificationCount={unreadNotificationCount}
        />

        {/* Main Area */}
        <div className="flex-1 flex flex-col min-w-0 lg:min-w-0">
          {/* Mobile Header */}
          <Header className="lg:hidden sticky top-0 z-40" unreadNotificationCount={unreadNotificationCount} />

          {/* Scrollable Content */}
          <main className="flex-1 overflow-y-auto">
            <div className="p-4 lg:p-6 pb-24 lg:pb-6 animate-fadeIn">
              {children}
            </div>
          </main>

          {/* Mobile Bottom Nav */}
          <BottomNav
            className="lg:hidden"
            unreadNotificationCount={unreadNotificationCount}
          />
        </div>
      </div>
      {/* ISS-001: ChatWidget은 overflow 컨테이너 밖 최상위에 두어 항상 표시. /llm 페이지는 전체화면이라 FAB 제외. */}
      {!isLlmPage && <ChatWidget />}
    </>
  );
}
