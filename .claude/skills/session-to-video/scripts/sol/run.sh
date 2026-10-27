#!/bin/bash
# usage: run.sh NN NN NN ...   (кадры по очереди)
cd "$(dirname "$0")"
for NN in "$@"; do
  OUT=$(cat n_${NN}.txt | tr -d '\r\n'); [ -f "$OUT" ] && continue
  IMGS=""; for r in $(cat r_${NN}.txt); do IMGS="$IMGS -i $r"; done
  { echo "Use your built-in image generation tool (image_gen) to draw ONE new illustration from the description below, using the attached images (if any) as references exactly as described. Pass the description to the image tool faithfully; do not embellish it or add elements. Save the final result as a PNG named ${OUT} in the current working directory (copy the generated file here if the tool saves it elsewhere). Do not write code that processes pixels. When done, reply with just the saved file name."; echo; cat p_${NN}.txt; } > q_${NN}.txt
  start=$(date +%s)
  codex exec --ignore-user-config -m gpt-6.1-sol -c model_reasoning_effort=high -c windows.sandbox=elevated \
    --sandbox workspace-write --skip-git-repo-check -C "$(pwd -W)" --ephemeral --color never $IMGS - < q_${NN}.txt > log_${NN}.txt 2>&1
  echo "${NN} $(( $(date +%s)-start ))s $([ -f "$OUT" ] && echo ok || echo MISSING)" >> times.txt
done
