// CUR-GO100-HOTFIX-003, 2026-02-23 — FAB SSR/Portal: mounted 후 createPortal 유지, 마운트 시 API 호출 없음
// CUR-GO100-HOTFIX-002A, 2026-02-23 — ChatWidget FAB 미노출 수정 (클라이언트 마운트 후 body 포탈만 사용)
// CUR-GO100-HOTFIX-002, 2026-02-23 — FAB Portal로 body 렌더링(ISS-008 전페이지 노출)
// CUR-GO100-PHASE2-STABILIZE STEP1, 2026-02-23 — ISS-001: ChatWidget 표시 수정 (fixed/z-[9999] 확인)
// CUR-GO100-HOTFIX-CRITICAL, 2026-02-23
// CUR-GO100-UNIFIED-SAVE-FE, 2026-02-23
// CUR-GO100-MY-STRATEGY-FIX, 2026-02-22 — 채팅 위젯 우하단(bottom-6 right-6) 병합
// CUR-GO100-CHAT-POSITION-FIX, 2026-02-22

"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { useRouter } from "next/navigation";
import { MessageSquare, X, Maximize2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { chatWithAI } from "../api";
import type { ChatResponse, RiskTolerance } from "../types";
import { ChatMessage } from "./ChatMessage";

const WIDGET_SESSION_KEY = "go100_chat_widget_session_id";
const DEFAULT_USER_ID = 1;
const DEFAULT_RISK: RiskTolerance = "medium";

type Msg = { role: "user" | "assistant"; content: string };

function getStoredSessionId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(WIDGET_SESSION_KEY);
}

function setStoredSessionId(id: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(WIDGET_SESSION_KEY, id);
}

export function ChatWidget() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    setSessionId(getStoredSessionId());
  }, []);

  useEffect(() => {
    if (!open) return;
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [open, messages, loading]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await chatWithAI({
        message: text,
        user_id: DEFAULT_USER_ID,
        risk_tolerance: DEFAULT_RISK,
        session_id: sessionId ?? undefined,
      });
      const reply =
        (res as ChatResponse & { reply_to_user?: string }).reply_to_user ??
        res.message ??
        (res.status === "completed" ? "전략 생성이 완료되었습니다." : "응답을 생성 중입니다.");
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      if (res.session_id) {
        setSessionId(res.session_id);
        setStoredSessionId(res.session_id);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "오류가 났어요. 다시 시도해 주세요." },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, sessionId]);

  const goFullscreen = useCallback(() => {
    setOpen(false);
    router.push("/llm");
  }, [router]);

  // CUR-GO100-HOTFIX-002A: 클라이언트 마운트 후에만 FAB/패널 렌더. SSR 시 인라인 렌더로 인한 부모 overflow/z-index 미노출 방지.
  if (!mounted || typeof document === "undefined") {
    return null;
  }

  const fab = (
    <button
      type="button"
      onClick={() => setOpen((o) => !o)}
      className="fixed bottom-6 right-6 z-[9999] flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
      aria-label={open ? "채팅 패널 닫기" : "백억이 채팅 열기"}
      data-testid="chat-widget-fab"
    >
      {open ? <X className="h-6 w-6" /> : <MessageSquare className="h-6 w-6" />}
    </button>
  );

  const panel = open ? (
    <div
      ref={panelRef}
      className={[
        "fixed z-[9998] flex flex-col overflow-hidden bg-gray-900",
        "inset-0 sm:inset-auto sm:bottom-24 sm:right-6 sm:w-96 sm:h-[500px] sm:rounded-lg sm:border sm:border-gray-700 sm:shadow-2xl",
      ].join(" ")}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-700 px-3 py-2">
        <span className="flex items-center gap-2 text-sm font-medium text-white">
          🤖 백억이
        </span>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-8 text-gray-300 hover:text-white"
            onClick={goFullscreen}
            title="전체 화면"
          >
            <Maximize2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 text-gray-300 hover:text-white"
            onClick={() => setOpen(false)}
            title="닫기"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
        {messages.length === 0 && !loading && (
          <p className="text-center text-sm text-gray-400 py-4">
            전략에 대해 말씀해 주세요.
          </p>
        )}
        {messages.map((m, i) => (
          <ChatMessage
            key={i}
            role={m.role}
            content={m.content}
            className={
              m.role === "user"
                ? "[&>div]:bg-blue-600 [&>div]:text-white"
                : "[&>div]:bg-gray-800 [&>div]:text-gray-100"
            }
          />
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-gray-800 px-4 py-3 text-sm text-gray-300">
              <span className="animate-pulse">...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-2 flex gap-2">
        <Textarea
          placeholder="메시지 입력..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          className="min-h-[40px] max-h-24 resize-none border-gray-600 bg-gray-800 text-white placeholder:text-gray-400"
          rows={1}
          disabled={loading}
        />
        <Button
          size="icon"
          className="h-10 w-10 shrink-0 bg-blue-600 hover:bg-blue-700"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          title="전송"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  ) : null;

  return (
    <>
      {createPortal(fab, document.body)}
      {panel != null ? createPortal(panel, document.body) : null}
    </>
  );
}
