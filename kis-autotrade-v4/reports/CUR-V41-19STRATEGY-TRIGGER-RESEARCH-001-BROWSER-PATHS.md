# 19전략 트리거 검증 보고서 — 브라우저/경로 안내

## 1. GitHub에서 보기 (브라우저)

저장소에 로그인한 뒤 아래 주소로 접속하세요.

**go100 메인 레포 (푸시된 브랜치)**  
https://github.com/moongoby/go100/blob/phase-2c-command-center/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md

- 비공개 레포면 로그인 후 같은 URL로 접속하면 됩니다.
- Raw(원문):  
  https://raw.githubusercontent.com/moongoby/go100/phase-2c-command-center/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md

# 19전략 트리거 검증 보고서 — 브라우저/경로 안내

## 1. GitHub에서 보기 (브라우저)

저장소에 로그인한 뒤 아래 주소로 접속하세요.

**go100 메인 레포 (푸시된 브랜치)**  
https://github.com/moongoby/go100/blob/phase-2c-command-center/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md

- 비공개 레포면 로그인 후 같은 URL로 접속하면 됩니다.
- Raw(원문):  
  https://raw.githubusercontent.com/moongoby/go100/phase-2c-command-center/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md

---

## 2. 문서 레포(project-docs) 경로

문서 전용 퍼블릭 레포 **moongoby/project-docs** 기준 경로입니다.  
(보고서를 project-docs에 복사·푸시한 후 아래 URL로 접근 가능합니다.)

| 항목 | 경로 / URL |
|------|-------------|
| **문서 레포 트리 (브라우저)** | https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md |
| **문서 레포 Raw URL** | https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md |
| **문서 레포 로컬 복사본** | `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md` |
| **문서 레포 내 상대 경로** | `kis-autotrade-v4/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md` |

**project-docs에 반영하는 방법**

```bash
cp /root/kis-autotrade-v4/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md \
   /root/project-docs/kis-autotrade-v4/reports/
cd /root/project-docs && git add kis-autotrade-v4/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md && git commit -m "docs: 19전략 트리거 검증 보고서" && git push
```

---

## 3. 로컬 워크스페이스 경로 (메인 레포 kis-autotrade-v4)

| 용도 | 경로 |
|------|------|
| 보고서 마크다운 | `reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md` |
| 전체 경로 | `/root/kis-autotrade-v4/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md` |
| HANDOVER v4.9 | `docs/HANDOVER.md` |

Cursor/VS Code에서는 **파일 탐색기**에서 위 경로로 열면 됩니다.

---

## 4. 로컬에서 브라우저로 보기 (선택)

프로젝트 루트에서 간이 서버를 띄우면 브라우저로 마크다운을 볼 수 있습니다.

```bash
cd /root/kis-autotrade-v4
python3 -m http.server 8765
```

브라우저에서:  
http://localhost:8765/reports/CUR-V41-19STRATEGY-TRIGGER-RESEARCH-001-20260301.md  

(마크다운이 HTML로 렌더되지 않으면 그냥 텍스트로 보입니다. 미리보기는 Cursor/IDE에서 마크다운 미리보기 사용을 권장합니다.)
