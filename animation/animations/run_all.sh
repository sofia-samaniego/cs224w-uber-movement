#!/bin/bash
#
# Author: Javier Sagastuy
# Stand: 09.12.2017
#

for f in *.tex; do
  pdflatex -synctex=1 -shell-escape -interaction=nonstopmode $f;
  bibtex $f;
  pdflatex -synctex=1 -shell-escape -interaction=nonstopmode $f;
  pdflatex -synctex=1 -shell-escape -interaction=nonstopmode $f;
done
