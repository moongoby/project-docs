#!/bin/bash
SRC="/data/shortflow/docs"
DST="/data/project-docs/shortflow"

# CONTEXT, 기획서, 아키텍처
cp ${SRC}/CONTEXT.md ${DST}/ 2>/dev/null
cp ${SRC}/plans/shortflow_v3.0_plan.md ${DST}/ 2>/dev/null
cp ${SRC}/plans/styleflow_v1.0_plan.md ${DST}/ 2>/dev/null
cp ${SRC}/architecture/system_architecture_v1.0.md ${DST}/architecture.md 2>/dev/null

# cursorrules
cp /data/shortflow/.cursorrules ${DST}/cursorrules.md 2>/dev/null

# INDEX.md 동기화 (shortflow 루트)
cp /data/shortflow/docs/reports/INDEX.md ${DST}/INDEX.md 2>/dev/null || true
cp /data/shortflow/reports/INDEX.md ${DST}/INDEX.md 2>/dev/null || true

# 인계서 (최신 3개)
mkdir -p ${DST}/handover
ls -t ${SRC}/handover/2*.md 2>/dev/null | head -3 | while read f; do cp "$f" ${DST}/handover/; done

# 보고서: docs/reports + shortflow 루트 reports (INDEX·전체 보고서)
mkdir -p ${DST}/reports
cp ${SRC}/reports/INDEX.md ${DST}/reports/ 2>/dev/null
cp ${SRC}/reports/2*.md ${DST}/reports/ 2>/dev/null
cp ${SRC}/reports/REPORT_TEMPLATE.md ${DST}/reports/ 2>/dev/null
cp /data/shortflow/reports/INDEX.md ${DST}/reports/ 2>/dev/null
cp /data/shortflow/reports/2*.md ${DST}/reports/ 2>/dev/null
cp /data/shortflow/reports/REPORT_TEMPLATE.md ${DST}/reports/ 2>/dev/null

# Git push
cd /data/project-docs && git add -A
git diff --cached --quiet || { git commit -m "[sync] shortflow $(date +%Y%m%d_%H%M)"; git push origin master; }
