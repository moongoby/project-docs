"use client";

export interface ModelOption {
  id: string;
  name: string;
  icon: string;
  cost: string;
  desc: string;
  provider: "anthropic" | "google";
}

// API 연동된 모델만 (Claude, Gemini). GPT는 미연동으로 제외.
export const MODEL_OPTIONS: ModelOption[] = [
  // Claude (Anthropic)
  { id: "claude-opus-4-6", name: "Claude Opus 4.6", icon: "🟣", cost: "$5/$25", desc: "복잡한 전략·설계", provider: "anthropic" },
  { id: "claude-sonnet-4-6", name: "Claude Sonnet 4.6", icon: "🔵", cost: "$3/$15", desc: "일반 개발·분석", provider: "anthropic" },
  { id: "claude-haiku-4-5-20251001", name: "Claude Haiku 4.5", icon: "💙", cost: "$0.80/$4", desc: "빠른 조회·정리", provider: "anthropic" },
  { id: "claude-opus-4-5", name: "Claude Opus 4.5", icon: "🟣", cost: "$5/$25", desc: "Anthropic", provider: "anthropic" },
  { id: "claude-sonnet-4-5", name: "Claude Sonnet 4.5", icon: "🔵", cost: "$3/$15", desc: "Anthropic", provider: "anthropic" },
  { id: "claude-3-5-sonnet-20241022", name: "Claude 3.5 Sonnet", icon: "🔵", cost: "$3/$15", desc: "Anthropic", provider: "anthropic" },
  { id: "claude-3-5-haiku-20241022", name: "Claude 3.5 Haiku", icon: "💙", cost: "$0.80/$4", desc: "Anthropic", provider: "anthropic" },
  { id: "claude-3-opus-20240229", name: "Claude 3 Opus", icon: "🟣", cost: "$15/$75", desc: "Anthropic", provider: "anthropic" },
  { id: "claude-3-sonnet-20240229", name: "Claude 3 Sonnet", icon: "🔵", cost: "$3/$15", desc: "Anthropic", provider: "anthropic" },
  { id: "claude-3-haiku-20240307", name: "Claude 3 Haiku", icon: "💙", cost: "$0.25/$1.25", desc: "Anthropic", provider: "anthropic" },
  { id: "claude-2.1", name: "Claude 2.1", icon: "🔵", cost: "$8/$24", desc: "Anthropic", provider: "anthropic" },
  // Gemini (Google)
  { id: "gemini-2.5-pro", name: "Gemini 2.5 Pro", icon: "🟡", cost: "$7/$21", desc: "Google 고성능", provider: "google" },
  { id: "gemini-3.1-pro-preview", name: "Gemini 3.1 Pro Preview", icon: "🟡", cost: "$2/$12", desc: "Google", provider: "google" },
  { id: "gemini-2.5-flash", name: "Gemini 2.5 Flash", icon: "🟡", cost: "$0.30/$2.50", desc: "가벼운 조회·요약", provider: "google" },
  { id: "gemini-2.0-flash", name: "Gemini 2.0 Flash", icon: "🟡", cost: "$0.075/$0.30", desc: "Google", provider: "google" },
  { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro", icon: "🟡", cost: "$3.50/$10.50", desc: "Google", provider: "google" },
  { id: "gemini-1.5-flash", name: "Gemini 1.5 Flash", icon: "🟡", cost: "$0.075/$0.30", desc: "Google", provider: "google" },
  // 자동 라우팅
  { id: "mixture", name: "혼합 에이전트 (자동)", icon: "🔴", cost: "자동", desc: "내용에 따라 최적 모델 자동 선택", provider: "anthropic" },
];

export const DEFAULT_MODEL = "claude-sonnet-4-6";

interface Props {
  value: string;
  onChange: (modelId: string) => void;
}

export default function ModelSelector({ value, onChange }: Props) {
  const selected = MODEL_OPTIONS.find((m) => m.id === value) ?? MODEL_OPTIONS.find((m) => m.id === DEFAULT_MODEL)!;
  const claudeModels = MODEL_OPTIONS.filter((m) => m.provider === "anthropic" && m.id !== "mixture");
  const geminiModels = MODEL_OPTIONS.filter((m) => m.provider === "google");
  const mixtureOption = MODEL_OPTIONS.find((m) => m.id === "mixture");

  return (
    <div className="flex flex-wrap items-center gap-2 mb-2">
      <span className="text-xs" style={{ color: "var(--text-secondary)" }}>모델:</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="text-xs px-3 py-1.5 rounded-lg min-w-[200px] max-w-full font-medium"
        style={{
          background: "var(--bg-main)",
          color: "var(--text-primary)",
          border: "1px solid var(--border)",
        }}
        title={`${selected.name} — ${selected.desc} (${selected.cost})`}
      >
        <optgroup label="🟣 Claude (Anthropic)">
          {claudeModels.map((m) => (
            <option key={m.id} value={m.id}>
              {m.icon} {m.name} — {m.cost}
            </option>
          ))}
        </optgroup>
        <optgroup label="🟡 Gemini (Google)">
          {geminiModels.map((m) => (
            <option key={m.id} value={m.id}>
              {m.icon} {m.name} — {m.cost}
            </option>
          ))}
        </optgroup>
        {mixtureOption && (
          <optgroup label="자동">
            <option value={mixtureOption.id}>{mixtureOption.icon} {mixtureOption.name}</option>
          </optgroup>
        )}
      </select>
      <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
        {selected.cost} /M
      </span>
    </div>
  );
}
