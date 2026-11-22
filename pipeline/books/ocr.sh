#!/bin/bash
# ocr.sh CODE PDF : OCR every page into CODE/NNNN.txt (resumable)
code=$1; pdf=$2; mkdir -p $code
n=$(pdfinfo "$pdf" | awk '/Pages/{print $2}')
seq 1 $n | xargs -P 2 -I{} bash -c '
p=$(printf %04d {}); [ -s '"$code"'/$p.txt ] && exit 0
pdftoppm -f {} -l {} -r 200 -gray "'"$pdf"'" /tmp/'"$code"'_$p
tesseract /tmp/'"$code"'_$p*.pgm '"$code"'/$p -l ara --tessdata-dir ~/tessdata >/dev/null 2>&1
rm -f /tmp/'"$code"'_$p*.pgm'
