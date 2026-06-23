---
name: pdf-to-crash-course
description: >
  Convert a textbook PDF into a beautiful, print-ready A4 crash-course PDF study guide.
  Trigger when the user provides a PDF textbook and asks for a 速成 (crash course),
  精讲 (intensive review), study guide, 复习资料, or similar. The skill reads the entire
  textbook, extracts key content chapter by chapter, restructures it using a color-coded
  box system (definitions, theorems, formulas, examples, warnings, tips, methods), handles
  images (redraw or extract), pre-renders math to SVG, and outputs a clean A4 PDF.
  Use this whenever a user wants to turn a textbook into a condensed study guide PDF.
context: fork
argument-hint: <path-to-textbook.pdf>
metadata:
  version: 2.0.0
---

# pdf-to-crash-course

Convert a textbook PDF into a crash-course A4 PDF study guide.

## Pipeline Overview

```
PDF textbook
  -> Stage 0: Pre-flight (auto-detect OCR need, auto-run if needed)
    -> Stage 1: Structure Analysis (TOC extraction, chapter outline)
      -> Stage 2: Content Generation (chapter-by-chapter, 8-box system)
        -> Stage 3: Assembly (HTML with sidebar, hero, all content)
          -> Stage 4: PDF Generation (MathJax → Playwright → A4 PDF)
            -> Stage 5: Verification (completeness, integrity, gap check)
              -> Deliver PDF
```

HTML is an intermediate artifact. The user receives only the PDF.

---

## Stage 0: Pre-flight (with Auto-OCR)

### 0.1 Parse & Verify

1. Parse `$ARGUMENTS` for the PDF path. If not provided, ask the user.
2. Verify the PDF exists and is readable.
3. Determine total page count via PyMuPDF (`fitz.open`).

### 0.2 Text Extractability Assessment (CRITICAL)

Use PyMuPDF to check text extractability. Do NOT rely on a single page — sample **at least 5 pages spread across the PDF** (e.g. pages 1, N/4, N/2, 3N/4, N).

```python
import fitz
doc = fitz.open(pdf_path)
for pg in [0, N//4, N//2, 3*N//4, N-1]:
    text = doc[pg].get_text()
    print(f"Page {pg+1}: {len(text)} chars, has_text={len(text.strip())>50}")
```

**Decision matrix:**

| Condition | Verdict | Action |
|-----------|---------|--------|
| All sampled pages have `>50` chars of extractable text | **Text OK** | Skip OCR, proceed to Stage 1 |
| Some pages have text, some don't | **Mixed** | Run OCR on image-only pages |
| No pages have extractable text | **Scanned PDF** | **Auto-run full OCR** (Stage 0.3) |
| PDF has DRM/encryption | **Blocked** | Report error, stop |

### 0.3 Auto-OCR (runs automatically when needed)

When OCR is needed, do NOT ask the user — just proceed. Use this priority order:

#### OCR Engine Selection

1. **EasyOCR** (preferred — pure Python, good Chinese support, no external deps):
   ```bash
   python -m pip install easyocr pymupdf pillow --quiet
   ```
   - Pro: Easy setup, good for Chinese + English
   - Con: Slower (5-10s/page on CPU), needs PyTorch (~2GB)
   - Use when: No Tesseract installed, or Chinese text expected

2. **Tesseract + pytesseract** (faster, needs system install):
   - Windows: Download installer from https://github.com/UB-Mannheim/tesseract/releases
   - Pro: Fast (1-2s/page), lightweight
   - Con: Requires separate install, Chinese language pack
   - Use when: Already installed, or for non-Chinese PDFs

3. **ocrmypdf** (best quality, slowest setup):
   - Requires Tesseract + poppler
   - Produces searchable PDF directly
   - Use when: Both Tesseract AND poppler are available

#### OCR Execution

Write and run `ocr_pdf.py` in the working directory. The script MUST:
- Use `fitz` (PyMuPDF) to render each page to an image (200-250 DPI)
- OCR each page and save text to `ocr_output/page_NNNN.txt`
- Maintain a `progress.json` file so interrupted runs can resume
- Show progress (current page / total, ETA)
- Process ALL pages (no skipping)

**Template script structure:**
```python
import fitz, easyocr, json, os, time
reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)
doc = fitz.open(PDF_PATH)
for i in range(total):
    if i in done: continue  # resume support
    pix = doc[i].get_pixmap(dpi=200)
    results = reader.readtext(pix.tobytes("png"), detail=0)
    text = "\n".join(results)
    # save to ocr_output/page_{i+1:04d}.txt
    # update progress.json
```

#### OCR Quality Note

OCR text will have garbled math symbols — this is expected. The crash course pipeline compensates by:
- Using Claude's knowledge of the subject to reconstruct formulas correctly
- Cross-referencing structure (definitions, theorems, examples) from OCR
- Math formulas are written in LaTeX from domain knowledge, not OCR

### 0.4 Environment Check

Before proceeding, verify the toolchain for later stages:

| Tool | Check command | Auto-fix |
|------|--------------|----------|
| Python 3 | `python --version` | Required for OCR + build scripts |
| Node.js | `node --version` | Required for MathJax + Playwright |
| mathjax-full | `node -e "require('mathjax-full')"` | `npm install mathjax-full` |
| playwright | `node -e "require('playwright')"` | `npm install playwright` |
| Chromium (Playwright) | `npx playwright install --dry-run` | `npx playwright install chromium` |
| PyMuPDF | `python -c "import fitz"` | `python -m pip install pymupdf` |

Auto-install missing dependencies without asking.

---

## Stage 1: Structure Analysis

1. Extract the table of contents from the PDF:
   - If OCR was run: read from `ocr_output/page_000{N}.txt` (TOC is usually in the first 10 pages)
   - If text is extractable: use `fitz` to get text from early pages
   - Look for patterns like "Chapter X", "第X章", "§X.Y", numbered headings
   - Build an outline with **page ranges per chapter** (important for Stage 2)

2. Present the outline to the user **in Chinese if the textbook is Chinese**. Ask for adjustments.

3. If the book has more than 12 chapters, suggest merging or skipping less critical ones.

4. Plan appendix sections based on content type:
   - Math/Engineering: formula cheatsheet, common mistakes, exam strategy
   - Humanities: key concept glossary, timeline

### Page Range Mapping

Build a mapping like:
```
Chapter 8: pages 1-40 (from OCR: §8.1 starts pg 1, §8.5 ends pg 40)
Chapter 9: pages 41-91
...
```

---

## Stage 2: Content Generation (per chapter)

Process one chapter at a time. For each chapter:

### 2.1 Read Source Material

1. If OCR was run: read the `ocr_output/page_NNNN.txt` files for that chapter's page range
2. If text is extractable: read PDF pages directly with Read tool
3. **Skim strategically**: Read key pages (chapter start, section starts, theorem pages) fully; skim others for structure

### 2.2 Classify into Box Types

Identify and classify content into the 8 box types (see `references/box-system.md`):

| Box | CSS Class | Color | Use For |
|-----|-----------|-------|---------|
| **定义** | `.box.def` | Blue `#1d6fa5` | Key terms, concepts |
| **定理** | `.box.thm` | Purple `#7c3aed` | Theorems, propositions, corollaries |
| **公式** | `.box.formula` | Teal `#0d7d6e` | Important equations |
| **例题** | `.box.eg` | Amber `#c2640a` | Worked examples with `.sol` block |
| **警示** | `.box.warn` | Red `#c92a2a` | Common mistakes, pitfalls |
| **技巧** | `.box.tip` | Green `#0b7b5b` | Mnemonics, study tips, chapter intros |
| **方法** | `.box.method` | Indigo `#4f46e5` | Step-by-step procedures |

### 2.3 Content Rules

- **Math formulas**: Always use `$...$` (inline) and `$$...$$` (display). Reconstruct from domain knowledge if OCR is garbled — do NOT copy garbled OCR math.
- **Density**: Each chapter output should be 1/4 to 1/3 of the original page count
- **Per chapter minimum**: At least 1 tip box (chapter intro), 1 method box (problem-solving flow), 2+ example boxes
- **Images**: Follow `references/image-strategy.md`. Redraw simple diagrams; extract complex ones.
- **Language**: Match the textbook's language (中文教材→中文输出, English→English)

### 2.4 Write Chapter HTML

Write to `parts/ch{NN}.html` (two-digit: `ch08.html`, `ch09.html`, ..., `ch12.html`).

Structure template (from `references/content-strategy.md`):
```html
<h2 class="chapter" id="chN">第N章 标题</h2>

<div class="box tip"><span class="label">本章导读</span>
[2-3 sentence overview + exam importance + key topics]
</div>

<h3 class="section" id="chN-M">§N.M 小节标题</h3>
[definitions → theorems → formulas → examples → warnings → tips, as needed]

<div class="box method"><span class="label">本章解题流程</span>
[1-2-3 step summary]
</div>
```

### 2.5 Appendices

After all chapters are done, generate `parts/appendices.html` containing:

1. **A. 公式速查总表** — All key formulas organized by chapter, each in a formula box
2. **B. 常见错误汇总** — All warnings consolidated, each as a `.miss` div
3. **C. 考试策略与检查清单** — Time allocation + pre-submission checklist
4. Optionally: **D. 关键数据表** (distribution tables, etc.)

---

## Stage 3: Assembly

### 3.1 Read Template

Read `templates/crash-course.html` to get the skeleton (CSS + JS + placeholder structure).

### 3.2 Build Sidebar

Extract all chapter and section headings from the generated HTML parts to build the sidebar navigation:

```html
<a href="#ch8" class="chap">第八章 标题</a>
<a href="#ch8-1" class="sec">§8.1 小节标题</a>
...
```

### 3.3 Fill Placeholders

| Placeholder | Content |
|-------------|---------|
| `{{TITLE}}` | "Textbook Name — Crash Course" |
| `{{SIDEBAR_TITLE}}` | Book name |
| `{{SIDEBAR_SUBTITLE}}` | "Crash Course Guide" |
| `{{SIDEBAR}}` | Generated TOC links |
| `{{HERO_TITLE}}` | Full course title |
| `{{HERO_SUBTITLE}}` | Subtitle with book/school info |
| `{{HERO_META}}` | Chapter count, page estimate, feature tags |
| `{{CONTENT}}` | All chapter HTML + appendices concatenated |

### 3.4 Assembly Script

Write `assemble.py` to automate this. **CRITICAL**: Verify that ALL chapter files are read and included. Use exact filename matching — check with `os.path.exists()` for each file. Print summary after assembly:
```
Assembled: crash_course.html (XX KB)
Sidebar links: N
Chapters included: ch08 ✓, ch09 ✓, ch10 ✓, ...
```

### 3.5 Manual Spot-Check

After assembly, grep the HTML for key markers:
```bash
grep -c 'class="chapter"' crash_course.html   # should equal chapter count
grep -c 'class="box"' crash_course.html        # should be substantial (>50)
```

---

## Stage 4: PDF Generation

### 4.1 Image Extraction (if needed)

If any images were marked for extraction in Stage 2:
```bash
python scripts/extract_images.py <pdf_path> <page> images/
```

### 4.2 Build Pipeline

```bash
python scripts/build_pdf.py crash_course.html <output_name>.pdf --clean
```

This auto-detects math and runs:
1. `mathjax_to_svg.js` — pre-renders all `$$...$$` and `$...$` to SVG
2. `playwright_to_pdf.js` — renders HTML to A4 PDF

### 4.3 First-Pass Verification

Verify the output:
- PDF exists and has reasonable size (> 100 KB, < 50 MB)
- Page count is reasonable (roughly 1/4 to 1/3 of original, or 15-50 pages for a typical textbook)
- If page count seems off, investigate before Stage 5

---

## Stage 5: Integrity Verification (NEW — MANDATORY)

This stage MUST be completed before delivering the PDF. Do not skip.

### 5.1 Chapter Completeness Check

**Method**: Use PyMuPDF to extract text from the generated PDF and verify every chapter from the Stage 1 outline appears.

```python
import fitz
doc = fitz.open(output_pdf)
full_text = ""
for page in doc:
    full_text += page.get_text()

# Check each expected chapter heading
for ch in ["第八章", "第九章", "第十章", "第十一章", "第十二章"]:
    if ch in full_text:
        print(f"  ✓ {ch} — present")
    else:
        print(f"  ✗ {ch} — MISSING!")
doc.close()
```

**Action on failure**: If any chapter is missing, trace back through the assembly process:
1. Check `parts/ch{NN}.html` exists and has content
2. Check `assemble.py` correctly reads that file
3. Fix the issue and re-run Assembly → PDF Generation

### 5.2 Content Coverage Check

For each chapter, verify the minimum content requirements:

- [ ] At least one **本章导读** (`.box.tip`) at the chapter start
- [ ] At least one **本章解题流程** (`.box.method`) at the chapter end
- [ ] At least two **例题** (`.box.eg`) per chapter
- [ ] At least one **易错警示** (`.box.warn`) per chapter (or consolidated in appendix)
- [ ] Each section has at least one definition or theorem box
- [ ] No empty boxes (`.box` with no meaningful content inside)
- [ ] No placeholder text like "TODO", "FIXME", "待补充", "(add content)"

**Quick check** (run on the HTML before PDF generation):
```bash
grep -c 'class="box def"' crash_course.html    # definitions
grep -c 'class="box thm"' crash_course.html     # theorems
grep -c 'class="box eg"' crash_course.html      # examples
grep -c 'class="box warn"' crash_course.html    # warnings
grep -c 'class="box tip"' crash_course.html     # tips
grep -c 'class="box method"' crash_course.html  # methods
```

If any category has 0 counts, flag as a coverage gap.

### 5.3 Structural Integrity Check

- [ ] **Sidebar links**: Every `<a href="#...">` in the sidebar points to an existing `id` in the content
- [ ] **Chapter IDs**: Every `<h2 class="chapter" id="chN">` has a matching sidebar link
- [ ] **Section IDs**: Every `<h3 class="section" id="...">` has a matching sidebar link
- [ ] **No broken references**: No `<img src="...">` pointing to non-existent files
- [ ] **LaTeX syntax**: No unclosed `$$` or `$` (quick check: count of `$$` should be even)

### 5.4 Math Rendering Check

- [ ] `mathjax_to_svg.js` ran without errors (check build output for "ERROR" lines)
- [ ] Display math count > 0 (if textbook has math)
- [ ] Inline math count > 0 (if textbook has math)
- [ ] SVG output file is significantly larger than input HTML (math expanded to SVG)

### 5.5 PDF Quality Check

- [ ] PDF opens without errors (`fitz.open()` succeeds)
- [ ] Page count is reasonable:
  - For a 200-300 page textbook: expect 20-50 PDF pages
  - If < 15 pages: content is likely truncated — check assembly
  - If < 10 pages: almost certainly missing chapters — go back to Stage 3
- [ ] First page contains the hero/cover content (not blank, not raw HTML)
- [ ] Last page contains appendix or chapter content (not blank)
- [ ] File size is reasonable:
  - < 100 KB: likely missing content or math rendering failed
  - 500 KB - 5 MB: normal range
  - > 20 MB: may have too many embedded images

### 5.6 Verification Report

Print a summary verification report in Chinese (if textbook is Chinese):

```
## 完整性检验报告

| 检验项 | 结果 |
|--------|------|
| 章节完整性 | ✓ 5/5 章全部包含 |
| 定义盒子 | 15 个 |
| 定理盒子 | 12 个 |
| 公式盒子 | 28 个 |
| 例题盒子 | 11 个 |
| 警示盒子 | 14 个 |
| 技巧盒子 | 8 个 |
| 方法盒子 | 12 个 |
| 数学公式(显示) | 126 个 |
| 数学公式(行内) | 483 个 |
| PDF 页数 | 36 页 |
| PDF 大小 | 1.9 MB |
| 断链检查 | ✓ 无断链 |
| 空盒子检查 | ✓ 无空盒 |
| 结论 | ✅ 通过，可以交付 |
```

### 5.7 Remediation

If verification fails on any item:
1. Report the specific failure to the user
2. Explain the root cause
3. Fix the issue (go back to the relevant stage)
4. Re-run the verification
5. Only deliver the PDF when ALL checks pass OR the user explicitly accepts remaining issues

---

## Error Handling

| Condition | Action |
|-----------|--------|
| PDF not found | Ask user for correct path |
| Scanned PDF (no text) | **Auto-run OCR** (Stage 0.3) — do NOT just warn |
| Mixed text/image PDF | Auto-run OCR on image-only pages |
| DRM encrypted | Report error, stop |
| OCR runs too slow (>1 hr) | Offer to skip OCR and generate from domain knowledge only |
| No math in textbook | Pipeline skips MathJax pre-render automatically |
| MathJax render fails on a formula | Skip that formula, keep LaTeX source as fallback |
| Playwright browser missing | Auto-install: `npx playwright install chromium` |
| Image extraction fails | Skip that image, add note in output |
| Chapter file missing during assembly | Log error, re-check file naming (leading zeros!) |
| PDF generation produces < 10 pages | Likely assembly bug — check Stage 3 before re-running |
| Verification finds a gap | Fix root cause, re-generate, re-verify |

---

## Key Lessons Learned (from real runs)

1. **File naming consistency**: Use zero-padded numbers (`ch08.html`, `ch09.html`) consistently between content generation and assembly scripts. The mismatch `ch8` vs `ch08` is a classic bug.

2. **Encoding**: On Windows with Chinese locale, subprocess pipes default to GBK. Use `encoding="utf-8"` in Python subprocess calls, or ignore stderr decode errors (they don't affect output).

3. **EasyOCR model loading**: EasyOCR downloads models on first use (~10-30 seconds). Run a single-page test first to trigger model download, then run the full batch.

4. **OCR for math textbooks**: OCR quality for math symbols is poor, but the pipeline compensates by using Claude's domain knowledge. OCR text provides structure (which section, what type of content); formulas are reconstructed from knowledge.

5. **Verification is essential**: Always run Stage 5. The first run of this skill on a 256-page textbook produced a 20-page PDF missing 2 full chapters due to a filename mismatch that would have been caught by verification.

6. **assemble.py anti-pattern**: Do NOT hardcode chapter IDs without verifying file existence. Loop over actual files in `parts/` directory instead: `sorted(glob.glob("parts/ch*.html"))`.

---

## Design System

The HTML uses a clean, modern design with:
- **Single left border** on all boxes (no full borders, no shadows)
- **Triple-line tables** (top line, header line, bottom line only - no cell borders)
- Color-coded labels for instant visual recognition
- Fixed sidebar navigation with scroll-spy highlighting
- Reading progress bar
- A4-optimized print stylesheet

See `references/box-system.md` for the complete box type reference with HTML examples.
