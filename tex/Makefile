SHELL := /bin/sh
LATEXMK := latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error
SPANISH_LATEXMK := $(LATEXMK) -e '$$makeindex = "python3 \"$(abspath tools/make_spanish_index.py)\" %O -o %D %S";'

.PHONY: en pilot chapter01 chapter02 check spanish spanish-chapter01 spanish-chapter02 check-spanish prose-spanish extract-pilot figures
en: figures
	mkdir -p build/en/en
	$(LATEXMK) -outdir=build/en en/main.tex

pilot: figures
	mkdir -p build/pilot/en
	$(LATEXMK) -outdir=build/pilot en/pilot.tex

chapter01 chapter02 chapter03 chapter04 chapter05 chapter06 chapter07 chapter08: figures
	mkdir -p build/$@
	$(LATEXMK) -outdir=build/$@ en/$@.tex

check: en
	python3 tools/validate_pilot.py

.PHONY: chapter03 spanish-chapter03 check-chapter03
check-chapter03: chapter03 spanish-chapter03
	python3 tools/validate_chapter03.py

spanish: figures
	mkdir -p build/spanish/spanish
	$(SPANISH_LATEXMK) -outdir=build/spanish spanish/main.tex

spanish-chapter01 spanish-chapter02 spanish-chapter03 spanish-chapter04 spanish-chapter05 spanish-chapter06 spanish-chapter07 spanish-chapter08: figures
	mkdir -p build/$@
	$(SPANISH_LATEXMK) -outdir=build/$@ spanish/$(patsubst spanish-%,%,$@).tex

check-spanish: spanish spanish-chapter01 spanish-chapter02
	python3 tools/validate_spanish.py

prose-spanish:
	python3 tools/export_spanish_prose.py

# Extraction is a separate action and refuses to overwrite existing chapters.
extract-pilot:
	python3 tools/extract_pilot.py

FIGURES03 := $(foreach n,01 02 03 04 05 06 09 10,../figs/pdf/en/fig-03-$(n).pdf)
FIGURES04 := $(foreach n,01 02,../figs/pdf/en/fig-04-$(n).pdf)
FIGURES05 := $(foreach n,04 05 06,../figs/pdf/en/fig-05-$(n).pdf)
FIGURES06 := $(foreach n,01 02 03,../figs/pdf/en/fig-06-$(n).pdf)
FIGURES07 := $(foreach n,03 06 07 08 09 10 12 14 15,../figs/pdf/en/fig-07-$(n).pdf)
figures: ../figs/pdf/en/fig-02-01.pdf $(FIGURES03) $(FIGURES04) $(FIGURES05) $(FIGURES06) $(FIGURES07)

../figs/pdf/en/fig-03-%.pdf: ../figs/source/en/fig-03-%.svg
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

../figs/pdf/en/fig-02-01.pdf: ../figs/source/en/fig-02-01.svg
	mkdir -p ../figs/pdf/en
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

.PHONY: chapter04 spanish-chapter04 check-chapter04
check-chapter04: chapter04 spanish-chapter04
	python3 tools/validate_chapter04.py

../figs/pdf/en/fig-04-%.pdf: ../figs/source/en/fig-04-%.svg
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

.PHONY: chapter05 spanish-chapter05 check-chapter05
check-chapter05: chapter05 spanish-chapter05
	python3 tools/validate_chapter05.py

../figs/pdf/en/fig-05-%.pdf: ../figs/source/en/fig-05-%.svg
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

.PHONY: chapter06 spanish-chapter06 check-chapter06
check-chapter06: chapter06 spanish-chapter06
	python3 tools/validate_chapter06.py

../figs/pdf/en/fig-06-%.pdf: ../figs/source/en/fig-06-%.svg
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

.PHONY: chapter07 spanish-chapter07 check-chapter07
check-chapter07: chapter07 spanish-chapter07
	python3 tools/validate_chapter07.py

../figs/pdf/en/fig-07-%.pdf: ../figs/source/en/fig-07-%.svg
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

# Embedded DOCX artwork avoids SVG label clipping and overlap.
../figs/pdf/en/fig-07-07.pdf: ../figs/source/en/fig-07-07.emf
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

../figs/pdf/en/fig-07-08.pdf: ../figs/source/en/fig-07-08.emf
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

../figs/pdf/en/fig-07-14.pdf: ../figs/source/en/fig-07-14.emf
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<


# Flatten existing PDF annotations so LuaLaTeX retains all original labels.
../figs/pdf/en/fig-07-03.pdf: ../figs/source/en/fig-07-03.pdf
	gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 -dPreserveAnnots=false -dShowAnnots=true -sOutputFile=$@ $<

../figs/pdf/en/fig-07-06.pdf: ../figs/source/en/fig-07-06.pdf
	gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 -dPreserveAnnots=false -dShowAnnots=true -sOutputFile=$@ $<

../figs/pdf/en/fig-07-15.pdf: ../figs/source/en/fig-07-15.pdf
	gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 -dPreserveAnnots=false -dShowAnnots=true -sOutputFile=$@ $<


.PHONY: chapter08 spanish-chapter08 check-chapter08
check-chapter08: chapter08 spanish-chapter08
	python3 tools/validate_chapter08.py

FIGURES08 := $(foreach n,01 02 05 06 07,../figs/pdf/en/fig-08-$(n).pdf)
figures: $(FIGURES08)

../figs/pdf/en/fig-08-%.pdf: ../figs/source/en/fig-08-%.svg
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

../figs/pdf/en/fig-08-%.pdf: ../figs/source/en/fig-08-%.pdf
	gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 -dPreserveAnnots=false -dShowAnnots=true -sOutputFile=$@ $<

# Preserve the DOCX plot labels without SVG font-substitution clipping.
../figs/pdf/en/fig-08-05.pdf: ../figs/source/en/fig-08-05.emf
	inkscape --export-type=pdf --export-area-drawing --export-text-to-path --export-filename=$@ $<

.PHONY: supporting spanish-supporting check-supporting
supporting:
	mkdir -p build/supporting
	$(LATEXMK) -outdir=build/supporting en/supporting.tex
spanish-supporting:
	mkdir -p build/spanish-supporting
	$(SPANISH_LATEXMK) -outdir=build/spanish-supporting spanish/supporting.tex
check-supporting: supporting spanish-supporting en spanish prose-spanish
	python3 tools/validate_supporting.py

.PHONY: check-book
check-book: check check-spanish check-chapter03 check-chapter04 check-chapter05 check-chapter06 check-chapter07 check-chapter08 check-supporting
	python3 tools/validate_book_review.py
