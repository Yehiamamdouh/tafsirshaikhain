#!/bin/bash
# ocr2.sh CODE PDF : OCR every page into CODE/NNNN.txt (resumable, single-threaded tesseract x2)
code=$1; pdf=$2; mkdir -p $code tmp_$code
n=$(pdfinfo "$pdf" | awk '/Pages/{print $2}')
export OMP_THREAD_LIMIT=1
seq 1 $n | xargs -P 2 -I{} bash -c '
p=$(printf %04d {}); [ -s '"$code"'/$p.txt ] && exit 0
pdftoppm -f {} -l {} -r 200 -gray "'"$pdf"'" tmp_'"$code"'/$p
tesseract tmp_'"$code"'/$p*.pgm '"$code"'/$p -l ara --tessdata-dir ~/tessdata >/dev/null 2>&1
rm -f tmp_'"$code"'/$p*.pgm'
echo DONE $(ls $code | wc -l)
