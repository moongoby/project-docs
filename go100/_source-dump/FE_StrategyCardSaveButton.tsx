// CUR-GO100-PHASE2-STABILIZE STEP2, 2026-02-23 — ISS-003: 최소 필수 필드, 에러 응답 로깅, 성공 시 링크
// CUR-GO100-UNIFIED-SAVE-FE, 2026-02-23 — 전략 저장 → POST /api/go100/strategy-cards
// Modified by CUR-STRATEGY-FLOW-v1, 2026-02-20
// Modified by CUR-STRATEGY-JSON-ENFORCE-v1, 2026-02-20 — 폴백 파싱, 부분 데이터 저장 모달
// Modified by CUR-STRATEGY-CARD-MAPPING-FIX-v1, 2026-02-20 — 필드 매핑 보강 (name/amount/params/strategy_type)
// 전략설계 응답의 strategy_json 파싱 후 전략카드로 저장 버튼
"use client";

import { useState } from "react";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { createStrategyCard } from "@/go100/api/go100Api";
import type { Go100StrategyCardCreate } from "@/go100/types/strategy";
import { CATALOG_KEY } from "@/lib/hooks/useStrategyCards";
import type { Account } from "@/types";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

const STRATEGY_JSON_REGEX = /```strategy_json\s*([\s\S]*?)```/;

export interface ParsedStrategyJson {
  strategy_name: string;
  description?: string;
  ticker?: string;
  ticker_name?: string;
  strategy_type?: string;
  params?: Record<string, unknown>;
  entry_condition?: string;
  exit_condition?: string;
  risk_management?: string;
}

export function parseStrategyJsonFromContent(content: string): ParsedStrategyJson | null {
  const match = content.match(STRATEGY_JSON_REGEX);
  if (!match || !match[1]) return null;
  try {
    const parsed = JSON.parse(match[1].trim()) as unknown;
    if (parsed && typeof parsed === "object") {
      return parsed as ParsedStrategyJson;
    }
  } catch {
    // ignore
  }
  return null;
}

/** CUR-STRATEGY-JSON-ENFORCE-v1: strategy_json 블록 없을 때 응답 텍스트에서 전략명·종목·조건 추출 */
export function parseStrategyFallbackFromContent(content: string): ParsedStrategyJson | null {
  if (!content?.trim()) return null;
  const lines = content.trim().split("\n").map((l) => l.trim()).filter(Boolean);
  let strategy_name = "";
  const tickerMatch = content.match(/\b(\d{6})\b/);
  const ticker = tickerMatch ? tickerMatch[1] : "";
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^#+\s*전략/.test(line) || /전략명|전략 이름|전략\s*[:：]/.test(line)) {
      if (lines[i + 1]) strategy_name = lines[i + 1].slice(0, 80);
      break;
    }
    if (line.length >= 2 && line.length <= 60 && !line.startsWith("```") && !/^[-*]\s/.test(line)) {
      strategy_name = line;
      break;
    }
  }
  if (!strategy_name && lines[0] && lines[0].length <= 80) strategy_name = lines[0];
  if (!strategy_name) strategy_name = "전략 (미작성)";
  return {
    strategy_name,
    description: undefined,
    ticker: ticker || undefined,
    ticker_name: undefined,
    strategy_type: "custom",
    params: {},
    entry_condition: undefined,
    exit_condition: undefined,
    risk_management: undefined,
  };
}

/** 전략카드 저장 버튼 표시 가능 여부 (JSON 또는 폴백 파싱 성공 시) */
export function canShowStrategySave(content: string): boolean {
  return parseStrategyJsonFromContent(content) != null || parseStrategyFallbackFromContent(content) != null;
}

export interface StrategyCardSaveButtonProps {
  content: string;
  accounts: Account[];
  onSaved?: () => void;
  className?: string;
}

const BAD_STRATEGY_NAMES = ["", "(직접 입력)", "전략 (미작성)", "제공된 내용은 다음과 같습니다"];
function isBadStrategyName(name: string | undefined): boolean {
  if (!name || !name.trim()) return true;
  const t = name.trim();
  return BAD_STRATEGY_NAMES.some((b) => t === b || t.includes("제공된 내용") || t.includes("다음과 같"));
}
function normalizeStrategyName(name: string | undefined): string {
  if (!isBadStrategyName(name)) return (name as string).trim().slice(0, 100);
  return "AI 설계 전략";
}
const NEEDS_MODAL = (p: ParsedStrategyJson) =>
  isBadStrategyName(p.strategy_name) || p.strategy_name === "(직접 입력)" || p.strategy_name === "전략 (미작성)";

export function StrategyCardSaveButton({
  content,
  accounts,
  onSaved,
  className,
}: StrategyCardSaveButtonProps) {
  const [status, setStatus] = useState<"idle" | "saving" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalStrategyName, setModalStrategyName] = useState("");
  const [modalAllocated, setModalAllocated] = useState<string>("0");
  const [savedStrategyName, setSavedStrategyName] = useState<string>("");
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const parsedFromJson = parseStrategyJsonFromContent(content);
  const parsedFromFallback = parseStrategyFallbackFromContent(content);
  const parsed = parsedFromJson ?? parsedFromFallback;
  if (!parsed) return null;

  const needsModal = NEEDS_MODAL(parsed);

  const doSave = async (strategyName: string, _allocatedAmount: number) => {
    setStatus("saving");
    setErrorMessage(null);
    const params = parsed.params ?? {};
    const maxStocks = typeof params.max_stocks === "number" ? Math.min(50, Math.max(1, params.max_stocks)) : 5;
    const finalName =
      (strategyName && strategyName.trim() ? strategyName.trim() : null) || normalizeStrategyName(parsed.strategy_name);

    const body: Go100StrategyCardCreate = {
      strategy_name: finalName || `GO100 AI 전략 - ${new Date().toLocaleString("ko-KR")}`,
      description: parsed.description ?? "AI가 설계한 전략",
      source_type: "LLM",
      strategy_type: "GO100_AI",
      universe_filter: (params.universe_filter as Go100StrategyCardCreate["universe_filter"]) ?? undefined,
      entry_rules: parsed.entry_condition
        ? { text: parsed.entry_condition, ...(params.entry_rules as object) }
        : (params.entry_rules as Record<string, unknown>) ?? undefined,
      exit_rules: parsed.exit_condition
        ? { text: parsed.exit_condition, ...(params.exit_rules as object) }
        : (params.exit_rules as Record<string, unknown>) ?? undefined,
      risk_params: parsed.risk_management
        ? { text: parsed.risk_management, ...(params.risk_params as object) }
        : (params.risk_params as Record<string, unknown>) ?? undefined,
      strategy_params: {
        ...params,
        description: parsed.description,
        ticker: parsed.ticker,
        ticker_name: parsed.ticker_name,
        entry_condition: parsed.entry_condition,
        exit_condition: parsed.exit_condition,
        risk_management: parsed.risk_management,
      },
      max_stocks: maxStocks,
    };

    try {
      await createStrategyCard(body);
      setStatus("success");
      setModalOpen(false);
      setSavedStrategyName(finalName);
      queryClient.invalidateQueries({ queryKey: CATALOG_KEY });
      toast?.({ title: "전략카드 저장 완료", description: `전략카드 '${finalName}'이(가) 저장되었습니다.`, variant: "default" });
      onSaved?.();
    } catch (err: unknown) {
      const res = err && typeof err === "object" && "response" in err ? (err as { response?: { data?: unknown; status?: number } }).response : undefined;
      const detail = res?.data && typeof res.data === "object" && "detail" in res.data ? String((res.data as { detail: unknown }).detail) : undefined;
      if (res) {
        console.error("GO100 전략카드 저장 실패 응답:", res.status, res.data);
        const bodyText = typeof res.data === "string" ? res.data : JSON.stringify(res.data ?? {});
        console.error("GO100 전략카드 저장 실패 상세(응답 본문):", bodyText);
      }
      const msg = detail || (err instanceof Error ? err.message : "저장에 실패했습니다.");
      setStatus("error");
      setErrorMessage(msg);
      toast?.({ title: "저장 실패", description: msg, variant: "destructive" });
    }
  };

  const defaultAllocated =
    (parsed.params as { investment_amount?: number })?.investment_amount ??
    (parsed as { investment_amount?: number }).investment_amount ??
    1_000_000;

  const handleSave = () => {
    if (needsModal) {
      setModalStrategyName(normalizeStrategyName(parsed.strategy_name) === "AI 설계 전략" ? "" : (parsed.strategy_name || "").trim());
      setModalAllocated(String(defaultAllocated));
      setModalOpen(true);
      return;
    }
    doSave(normalizeStrategyName(parsed.strategy_name), defaultAllocated);
  };

  const handleModalSubmit = () => {
    const amt = Math.max(0, Number(modalAllocated) || 0);
    doSave(modalStrategyName.trim() || "AI 설계 전략", amt);
  };

  if (status === "success") {
    return (
      <div className={className} data-status="saved">
        <p className="mb-2">
          ✅ 전략카드 &apos;{savedStrategyName || "전략"}&apos;이(가) 저장되었습니다.
        </p>
        <Button variant="outline" size="sm" asChild>
          <Link href="/strategy-cards?tab=my">내 전략 보기</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className={className}>
      <Button
        type="button"
        size="sm"
        className="bg-blue-600 hover:bg-blue-700 text-white gap-1.5"
        onClick={handleSave}
        disabled={status === "saving"}
      >
        <span aria-hidden>💾</span>
        {status === "saving" ? "저장 중..." : "전략카드로 저장"}
      </Button>
      {errorMessage && <p className="mt-1 text-xs text-red-400">{errorMessage}</p>}
      {modalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          role="dialog"
          aria-label="전략 정보 입력"
        >
          <div className="w-full max-w-sm rounded-lg bg-gray-900 border border-gray-700 p-4 shadow-xl">
            <h3 className="text-sm font-medium text-gray-100 mb-3">저장할 전략 정보 (최소 입력)</h3>
            <label className="block text-xs text-gray-400 mb-1">전략 이름</label>
            <input
              type="text"
              value={modalStrategyName}
              onChange={(e) => setModalStrategyName(e.target.value)}
              className="w-full rounded border border-gray-600 bg-gray-800 text-gray-100 px-3 py-2 text-sm mb-3"
              placeholder="전략 이름"
            />
            <label className="block text-xs text-gray-400 mb-1">투자금액 (원)</label>
            <input
              type="number"
              min={0}
              value={modalAllocated}
              onChange={(e) => setModalAllocated(e.target.value)}
              className="w-full rounded border border-gray-600 bg-gray-800 text-gray-100 px-3 py-2 text-sm mb-4"
              placeholder="0"
            />
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" size="sm" onClick={() => setModalOpen(false)}>
                취소
              </Button>
              <Button type="button" size="sm" className="bg-blue-600 hover:bg-blue-700" onClick={handleModalSubmit} disabled={status === "saving"}>
                저장
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
