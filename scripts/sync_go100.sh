#!/bin/bash
SRC="/root/kis-autotrade-v4/docs"
DST="/root/project-docs/go100"
mkdir -p ${DST}/handover
cp ${SRC}/CONTEXT.md ${DST}/ 2>/dev/null
ls -t ${SRC}/handover/2*.md 2>/dev/null | head -3 | while read f; do cp "$f" ${DST}/handover/; done
cd /root/project-docs && git pull origin master && git add -A
git diff --cached --quiet || { git commit -m "[sync] go100 $(date +%Y%m%d_%H%M)"; git push origin master; }
