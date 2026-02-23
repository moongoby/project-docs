// Created by CUR-Y-LLM-CHAT-PAGE-v1, 2026-02-19
// Modified by CUR-LLM-CHAT-v1, 2026-02-19 — 모바일 퍼스트, 세션·스트리밍
// Modified by CUR-UI-AUDIT-FIX-v1, 2026-02-20
// Modified by CUR-BAEKUK-UI-v1, 2026-02-20 — 백억이 프리미엄 다크 리디자인, 채널/세션/법적고지
// Modified by CUR-BAEKUK-WELCOME-GUARD-v1, 2026-02-20 — 웰컴 화면, 카드 클릭 시 입력창 채움
// Modified by CUR-FRONTEND-QA-WELCOME-v1, 2026-02-20 — 새 대화 시 웰컴 카드 4장 표시
// Modified by CUR-USAGE-DISPLAY-REALAPI-v1, 2026-02-20 — 사용량 API 기반 입력 차단(remaining 0)
// Modified by CUR-STRATEGY-FLOW-v1, 2026-02-20 — 채널 전환·계좌·전략카드 저장 연동
// Modified by CUR-MOBILE-RESPONSIVE-v1, 2026-02-20 — 채팅 영역 패딩 모바일
"use client";

import { useRef, useEffect, useState } from "react";
import { useChatStore } from "@/lib/store/chat-store";
import { sendMessageStream } from "@/lib/api/llm";
import { useQueryClient } from "@tanstack/react-query";
import { useUsage } from "@/lib/hooks/useLLM";
import { useAccounts } from "@/lib/hooks/useAccounts";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChannelSelector } from "@/components/chat/ChannelSelector";
import { SessionList } from "@/components/chat/SessionList";
import { WelcomeScreen } from "@/components/chat/WelcomeScreen";
import { LegalNotice } from "@/components/chat/LegalNotice";
import { UsagePanel } from "@/components/llm/UsagePanel";
import { ModelSelector } from "@/components/llm/ModelSelector";
import type { Account } from "@/types";
import { Menu, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";

const USAGE_QUERY_KEY = ["llm", "usage"];
const SESSIONS_QUERY_KEY = ["llm", "sessions"];

function MobileSessionDrawer() {
  const [open, setOpen] = useState(false);
  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="shrink-0 rounded-xl border-gray-800 bg-gray-900/80 text-gray-300 hover:border-blue-500/30"
        >
          <Menu className="h-4 w-4" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-[280px] border-gray-800 bg-gray-950 p-4">
        <SessionList />
      </SheetContent>
    </Sheet>
  );
}

function MobileUsageDrawer() {
  const [open, setOpen] = useState(false);
  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="shrink-0 rounded-xl border-gray-800 bg-gray-900/80 text-gray-300 hover:border-blue-500/30"
        >
          <BarChart3 className="h-4 w-4" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[280px] border-gray-800 bg-gray-950 p-4">
        <UsagePanel />
      </SheetContent>
    </Sheet>
  );
}

export default function BaekukPage() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const { data: usageData } = useUsage();
  const { data: accountsData } = useAccounts();
  const {
    messages,
    selectedChannel,
    sessionId,
    addMessage,
    setSessionId,
    setSelectedChannel,
  } = useChatStore();
  const [streamingContent, setStreamingContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prefillText, setPrefillText] = useState("");

  const accounts: Account[] = (accountsData as { accounts?: Account[] } | undefined)?.accounts ?? [];

  const remainingForChannel = usageData?.channels?.[selectedChannel]?.remaining;
  const quotaExceeded = remainingForChannel !== undefined && remainingForChannel === 0;

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const handleSubmit = (text: string) => {
    if (!text.trim() || isStreaming) return;
    const userMsg = { role: "user" as const, content: text.trim() };
    addMessage(userMsg);
    setError(null);
    setIsStreaming(true);
    setStreamingContent("");

    sendMessageStream(
      {
        sessionId,
        message: text.trim(),
        category: selectedChannel,
      },
      (chunk) => setStreamingContent((prev) => prev + chunk),
      (payload) => {
        setSessionId(payload.session_id);
        addMessage({ role: "assistant", content: payload.content });
        setStreamingContent("");
        setIsStreaming(false);
        queryClient.invalidateQueries({ queryKey: USAGE_QUERY_KEY });
        queryClient.invalidateQueries({ queryKey: SESSIONS_QUERY_KEY });
      },
      (detail) => {
        setError(detail);
        addMessage({ role: "assistant", content: `오류: ${detail}` });
        setStreamingContent("");
        setIsStreaming(false);
      }
    );
  };

  return (
    <div className="flex flex-col min-h-0 min-w-0 h-[calc(100dvh-7rem)] sm:h-[calc(100dvh-8rem)] rounded-2xl border border-gray-800/50 bg-[#0a0a0f] shadow-lg shadow-blue-500/5">
      {/* 페이지 타이틀 + 채널/모바일 메뉴 */}
      <header className="flex flex-col gap-3 border-b border-gray-800/50 bg-gray-950/80 px-4 py-4 shrink-0">
        <div className="flex items-center gap-2">
          <div className="flex lg:hidden items-center gap-1">
            <MobileSessionDrawer />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg font-semibold bg-gradient-to-r from-amber-400 to-purple-400 bg-clip-text text-transparent">
              백억이
            </h1>
            <p className="text-xs text-gray-500">AI 투자학습 어시스턴트</p>
          </div>
          <div className="flex items-center gap-1">
            <div className="hidden sm:block max-w-[180px]">
              <ModelSelector />
            </div>
            <div className="flex lg:hidden">
              <MobileUsageDrawer />
            </div>
          </div>
        </div>
        <LegalNotice />
        <ChannelSelector value={selectedChannel} onChange={setSelectedChannel} />
      </header>

      <div className="flex flex-1 min-h-0">
        {/* 데스크톱: 좌측 세션 목록 */}
        <aside className="hidden lg:flex lg:w-64 lg:flex-col lg:border-r lg:border-gray-800/50 lg:bg-gray-900/30 lg:p-3 shrink-0">
          <SessionList />
        </aside>

        {/* 중앙: 채팅 영역 */}
        <main className="flex-1 min-w-0 flex flex-col bg-gray-950">
          <ScrollArea className="flex-1 p-3 sm:p-4">
            <div className="space-y-4">
              {messages.length === 0 && !streamingContent && (
                <WelcomeScreen onSelectPrompt={setPrefillText} />
              )}
              {messages.map((msg, i) => (
                <ChatMessage
                  key={i}
                  role={msg.role === "system" ? "assistant" : msg.role}
                  content={msg.content}
                  channel={selectedChannel}
                  onSwitchToDesignChannel={() => setSelectedChannel("design-chat")}
                  accounts={accounts}
                />
              ))}
              {streamingContent && (
                <ChatMessage
                  role="assistant"
                  content={streamingContent}
                  isStreaming
                  channel={selectedChannel}
                  accounts={accounts}
                />
              )}
              {error && (
                <p className="text-center text-sm text-red-400">{error}</p>
              )}
              <div ref={scrollRef} />
            </div>
          </ScrollArea>
          {quotaExceeded && (
            <p className="px-3 py-2 text-center text-sm text-red-400 bg-red-950/30 border-t border-gray-800/50 shrink-0">
              오늘의 사용량을 모두 소진했습니다.
            </p>
          )}
          <ChatInput
            onSubmit={handleSubmit}
            disabled={isStreaming || quotaExceeded}
            placeholder="메시지 입력..."
            prefill={prefillText}
            onPrefillApplied={() => setPrefillText("")}
          />
        </main>

        {/* 데스크톱: 우측 사용량 */}
        <aside className="hidden lg:flex lg:w-[280px] lg:flex-col lg:border-l lg:border-gray-800/50 lg:bg-gray-900/30 lg:p-4 shrink-0">
          <UsagePanel />
        </aside>
      </div>
    </div>
  );
}
