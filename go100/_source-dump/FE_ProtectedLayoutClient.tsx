// CUR-GO100-HOTFIX-006, 2026-02-23 — layout에서 분리한 클라이언트 UI (force-dynamic은 layout.tsx에서)
// CUR-GO100-HOTFIX-005, 2026-02-23 — ChatWidget FAB 미노출: dynamic import ssr:false
"use client";

import dynamic from "next/dynamic";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import { getUnreadCount } from "@/lib/api/notifications";
import { Sidebar } from "@/components/layout/Sidebar";
import { BottomNav } from "@/components/layout/BottomNav";
import { Header } from "@/components/layout/Header";

const ChatWidget = dynamic(
  () => import("@/go100/components/ChatWidget").then((m) => ({ default: m.ChatWidget })),
  { ssr: false }
);

export default function ProtectedLayoutClient({
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
        {!isLlmPage && <ChatWidget />}
      </>
    );
  }

  return (
    <>
      <div className="h-dvh flex bg-gradient-dark">
        <Sidebar
          className="hidden lg:flex"
          unreadNotificationCount={unreadNotificationCount}
        />
        <div className="flex-1 flex flex-col min-w-0 lg:min-w-0">
          <Header className="lg:hidden sticky top-0 z-40" unreadNotificationCount={unreadNotificationCount} />
          <main className="flex-1 overflow-y-auto">
            <div className="p-4 lg:p-6 pb-24 lg:pb-6 animate-fadeIn">
              {children}
            </div>
          </main>
          <BottomNav
            className="lg:hidden"
            unreadNotificationCount={unreadNotificationCount}
          />
        </div>
      </div>
      {!isLlmPage && <ChatWidget />}
    </>
  );
}
