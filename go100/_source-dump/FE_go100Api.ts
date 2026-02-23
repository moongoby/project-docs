// CUR-GO100-HOTFIX-CRITICAL, 2026-02-23
// CUR-GO100-UNIFIED-SAVE-FE, 2026-02-23
// CUR-GO100-FIX-FRONTEND, 2026-02-22
// CUR-GO100-FRONTEND-FIX2, 2026-02-21
// CUR-GO100-FRONTEND-FIX, 2026-02-21
// Modified by: CUR-GO100-PHASE3B-FRONTEND-TYPES, 2026-02-21

import axios from "axios";
import type {
  Go100StrategyCard,
  Go100StrategyCardCreate,
  Go100StrategyCardUpdate,
  Go100StatusTransitionRequest,
  Go100CardListResponse,
  Go100StoreItem,
  Go100Portfolio,
  Go100PortfolioCreate,
  Go100Position,
  Go100BacktestRun,
  Go100BacktestRequest,
  ChatRequest,
  ChatResponse,
  PaperTradingConfig,
  PaperTradingStatus,
  PaperPortfolioSnapshot,
  Go100Trade,
  LiveTradingConfig,
  LiveTradingStatus,
  LiveExecutionResult,
  ReconciliationRecord,
  RiskProfile,
  EffectiveRiskConfig,
  DisclaimerRequest,
  DisclaimerRecord,
} from "../types";

// 상대경로 또는 환경변수 사용 — 외부 접속 시 localhost:8002 직접 호출 방지
const BASE = process.env.NEXT_PUBLIC_GO100_API_URL
  ? `${process.env.NEXT_PUBLIC_GO100_API_URL.replace(/\/$/, "")}/api/go100`
  : "/api/go100";
const go100BaseURL =
  typeof window !== "undefined"
    ? ""
    : (process.env.NEXT_PUBLIC_GO100_API_URL || "http://localhost:8002");

const go100Client = axios.create({
  baseURL: go100BaseURL,
  headers: { "Content-Type": "application/json" },
});

go100Client.interceptors.request.use((config) => {
  if (typeof window === "undefined") return config;
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 401 시 로그인 페이지 등 기존 apiClient와 동일한 동작을 위해 interceptor 사용 (선택)
go100Client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (typeof window !== "undefined" && err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/auth/login";
    }
    return Promise.reject(err);
  }
);

// ── 전략 카드 CRUD ──

export async function createStrategyCard(data: Go100StrategyCardCreate): Promise<Go100StrategyCard> {
  const { data: res } = await go100Client.post<Go100StrategyCard>(`${BASE}/strategy-cards`, data);
  return res;
}

export async function getStrategyCards(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  source_type?: string;
}): Promise<Go100CardListResponse> {
  const { data } = await go100Client.get<Go100CardListResponse>(`${BASE}/strategy-cards`, { params });
  return data;
}

export async function getStrategyCard(cardId: number): Promise<Go100StrategyCard> {
  const { data } = await go100Client.get<Go100StrategyCard>(`${BASE}/strategy-cards/${cardId}`);
  return data;
}

export async function updateStrategyCard(cardId: number, data: Go100StrategyCardUpdate): Promise<Go100StrategyCard> {
  const { data: res } = await go100Client.put<Go100StrategyCard>(`${BASE}/strategy-cards/${cardId}`, data);
  return res;
}

/** GO100 카드 활성/비활성 토글. CUR-GO100-HOTFIX-CRITICAL */
export async function toggleStrategyCardActive(cardId: number): Promise<{ go100_card_id: number; strategy_name: string; is_active: boolean }> {
  const { data } = await go100Client.patch<{ go100_card_id: number; strategy_name: string; is_active: boolean }>(
    `${BASE}/strategy-cards/${cardId}/toggle`
  );
  return data;
}

export async function transitionCardStatus(cardId: number, data: Go100StatusTransitionRequest): Promise<Go100StrategyCard> {
  const { data: res } = await go100Client.post<Go100StrategyCard>(`${BASE}/strategy-cards/${cardId}/transition`, data);
  return res;
}

export async function deleteStrategyCard(cardId: number): Promise<{ message: string; card_id: number }> {
  const { data } = await go100Client.delete<{ message: string; card_id: number }>(`${BASE}/strategy-cards/${cardId}`);
  return data;
}

// ── 스토어 (마켓플레이스) ──

export async function getStoreList(): Promise<Go100StoreItem[]> {
  const { data } = await go100Client.get<Go100StoreItem[]>(`${BASE}/store`);
  return data;
}

export async function subscribeFromStore(storeId: number, data?: { account_id?: number }): Promise<Go100StrategyCard> {
  const { data: res } = await go100Client.post<Go100StrategyCard>(`${BASE}/store/${storeId}/subscribe`, data ?? {});
  return res;
}

// ── 포트폴리오 ──

export async function createPortfolio(data: Go100PortfolioCreate): Promise<Go100Portfolio> {
  const { data: res } = await go100Client.post<Go100Portfolio>(`${BASE}/portfolios`, data);
  return res;
}

export async function getPortfolios(): Promise<Go100Portfolio[]> {
  const { data } = await go100Client.get<Go100Portfolio[]>(`${BASE}/portfolios`);
  return data;
}

export async function getPortfolio(id: number): Promise<Go100Portfolio> {
  const { data } = await go100Client.get<Go100Portfolio>(`${BASE}/portfolios/${id}`);
  return data;
}

export async function updatePortfolio(id: number, body: Partial<Go100PortfolioCreate>): Promise<Go100Portfolio> {
  const { data: res } = await go100Client.put<Go100Portfolio>(`${BASE}/portfolios/${id}`, body);
  return res;
}

export async function deletePortfolio(id: number): Promise<{ message: string }> {
  const { data } = await go100Client.delete<{ message: string }>(`${BASE}/portfolios/${id}`);
  return data;
}

export async function getPortfolioPositions(id: number): Promise<Go100Position[]> {
  const { data } = await go100Client.get<Go100Position[]>(`${BASE}/portfolios/${id}/positions`);
  return data;
}

export async function getPortfolioSummary(id: number): Promise<{ total_equity: number; total_return_pct: number;[k: string]: unknown }> {
  const { data } = await go100Client.get(`${BASE}/portfolios/${id}/summary`);
  return data;
}

// ── 백테스트 ──

export async function runBacktest(req: Go100BacktestRequest): Promise<{ run_id: number }> {
  const { data } = await go100Client.post<{ run_id: number }>(`${BASE}/backtest/run`, req);
  return data;
}

export async function getBacktestResult(runId: number): Promise<Go100BacktestRun> {
  const { data } = await go100Client.get<Go100BacktestRun>(`${BASE}/backtest/${runId}`);
  return data;
}

export async function getBacktestList(params?: { go100_card_id?: number }): Promise<{ items: Go100BacktestRun[] }> {
  const { data } = await go100Client.get<{ items: Go100BacktestRun[] }>(`${BASE}/backtest`, { params });
  return data;
}

// ── AI ──

export async function chatWithAI(req: ChatRequest): Promise<ChatResponse> {
  const { data } = await go100Client.post<ChatResponse>(`${BASE}/ai/chat`, req);
  return data;
}

export async function aiUnderstand(body: { message: string; user_id: number }): Promise<unknown> {
  const { data } = await go100Client.post(`${BASE}/ai/understand`, body);
  return data;
}

export async function aiDesign(body: { message: string; user_id: number; session_id?: string }): Promise<unknown> {
  const { data } = await go100Client.post(`${BASE}/ai/design`, body);
  return data;
}

export async function aiEvaluate(body: { strategy_card_id: number }): Promise<unknown> {
  const { data } = await go100Client.post(`${BASE}/ai/evaluate`, body);
  return data;
}

export async function aiOptimize(body: { strategy_card_id: number }): Promise<unknown> {
  const { data } = await go100Client.post(`${BASE}/ai/optimize`, body);
  return data;
}

// ── Paper Trading ──

export async function startPaperTrading(config: PaperTradingConfig): Promise<PaperTradingStatus> {
  const { data } = await go100Client.post<PaperTradingStatus>(`${BASE}/paper-trading/start`, config);
  return data;
}

export async function getPaperPortfolios(): Promise<PaperTradingStatus[]> {
  const { data } = await go100Client.get<PaperTradingStatus[]>(`${BASE}/paper-trading`);
  return data;
}

export async function getPaperStatus(id: number): Promise<PaperTradingStatus> {
  const { data } = await go100Client.get<PaperTradingStatus>(`${BASE}/paper-trading/${id}`);
  return data;
}

export async function pausePaper(id: number): Promise<PaperTradingStatus> {
  const { data } = await go100Client.post<PaperTradingStatus>(`${BASE}/paper-trading/${id}/pause`);
  return data;
}

export async function resumePaper(id: number): Promise<PaperTradingStatus> {
  const { data } = await go100Client.post<PaperTradingStatus>(`${BASE}/paper-trading/${id}/resume`);
  return data;
}

export async function stopPaper(id: number): Promise<PaperTradingStatus> {
  const { data } = await go100Client.post<PaperTradingStatus>(`${BASE}/paper-trading/${id}/stop`);
  return data;
}

export async function runPaperNow(id: number): Promise<PaperTradingStatus> {
  const { data } = await go100Client.post<PaperTradingStatus>(`${BASE}/paper-trading/${id}/run-now`);
  return data;
}

export async function getPaperPositions(id: number): Promise<Go100Position[]> {
  const { data } = await go100Client.get<Go100Position[]>(`${BASE}/paper-trading/${id}/positions`);
  return data;
}

export async function getPaperTrades(id: number): Promise<Go100Trade[]> {
  const { data } = await go100Client.get<Go100Trade[]>(`${BASE}/paper-trading/${id}/trades`);
  return data;
}

export async function getPaperSnapshots(id: number): Promise<PaperPortfolioSnapshot[]> {
  const { data } = await go100Client.get<PaperPortfolioSnapshot[]>(`${BASE}/paper-trading/${id}/snapshots`);
  return data;
}

// ── Live Trading ──

export async function startLiveTrading(config: LiveTradingConfig): Promise<LiveTradingStatus> {
  const { data } = await go100Client.post<LiveTradingStatus>(`${BASE}/live-trading/start`, config);
  return data;
}

export async function getLivePortfolios(): Promise<LiveTradingStatus[]> {
  const { data } = await go100Client.get<LiveTradingStatus[]>(`${BASE}/live-trading`);
  return data;
}

export async function getLiveStatus(id: number): Promise<LiveTradingStatus> {
  const { data } = await go100Client.get<LiveTradingStatus>(`${BASE}/live-trading/${id}`);
  return data;
}

export async function pauseLive(id: number): Promise<LiveTradingStatus> {
  const { data } = await go100Client.post<LiveTradingStatus>(`${BASE}/live-trading/${id}/pause`);
  return data;
}

export async function resumeLive(id: number): Promise<LiveTradingStatus> {
  const { data } = await go100Client.post<LiveTradingStatus>(`${BASE}/live-trading/${id}/resume`);
  return data;
}

export async function stopLive(id: number): Promise<LiveTradingStatus> {
  const { data } = await go100Client.post<LiveTradingStatus>(`${BASE}/live-trading/${id}/stop`);
  return data;
}

export async function runLiveNow(id: number, dryRun?: boolean): Promise<LiveExecutionResult> {
  const { data } = await go100Client.post<LiveExecutionResult>(`${BASE}/live-trading/${id}/run-now`, { dry_run: dryRun });
  return data;
}

export async function reconcileLive(id: number): Promise<ReconciliationRecord[]> {
  const { data } = await go100Client.post<ReconciliationRecord[]>(`${BASE}/live-trading/${id}/reconcile`);
  return data;
}

export async function emergencyStopLive(id: number): Promise<LiveTradingStatus> {
  const { data } = await go100Client.post<LiveTradingStatus>(`${BASE}/live-trading/${id}/emergency-stop`);
  return data;
}

// ── Risk ──

export async function getRiskDefaults(tolerance: string): Promise<RiskProfile> {
  const { data } = await go100Client.get<RiskProfile>(`${BASE}/risk/defaults/${tolerance}`);
  return data;
}

export async function getEffectiveRisk(cardId: number, overrides?: Record<string, number>): Promise<EffectiveRiskConfig> {
  const { data } = await go100Client.get<EffectiveRiskConfig>(`${BASE}/risk/effective`, {
    params: { card_id: cardId, ...overrides },
  });
  return data;
}

export async function submitDisclaimer(req: DisclaimerRequest): Promise<{ message: string }> {
  const { data } = await go100Client.post<{ message: string }>(`${BASE}/risk/disclaimer`, req);
  return data;
}

export async function getDisclaimers(): Promise<DisclaimerRecord[]> {
  const { data } = await go100Client.get<DisclaimerRecord[]>(`${BASE}/risk/disclaimers`);
  return data;
}
