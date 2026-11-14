#!/bin/bash
# concatenate build/pages/*.html -> build/meridian163.html
set -e
cd "$(dirname "$0")/.."
cat build/pages/*.html > build/meridian163.html
cp meridian.css build/
echo "assembled $(grep -c 'class=\"page' build/meridian163.html) pages, $(wc -c < build/meridian163.html) bytes"
