#!/bin/bash
SRC="/data/shortflow/docs"
DST="/data/project-docs/shortflow"
cp ${SRC}/CONTEXT.md ${DST}/ 2>/dev/null
cp ${SRC}/plans/shortflow_v3.0_plan.md ${DST}/ 2>/dev/null
cp ${SRC}/plans/styleflow_v1.0_plan.md ${DST}/ 2>/dev/null
cp ${SRC}/architecture/system_architecture_v1.0.md ${DST}/architecture.md 2>/dev/null
ls -t ${SRC}/handover/2*.md 2>/dev/null | head -3 | while read f; do cp "$f" ${DST}/handover/; done
cd /data/project-docs && git add -A
git diff --cached --quiet || { git commit -m "[sync] shortflow $(date +%Y%m%d_%H%M)"; git push origin main; }
