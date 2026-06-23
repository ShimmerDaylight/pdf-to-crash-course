"""
Build pipeline: HTML → (optional MathJax pre-render) → PDF
Usage: python build_pdf.py <input.html> <output.pdf> [--no-math] [--clean]
"""
import sys
import os
import subprocess
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def has_math(html_path):
    """Detect if HTML contains math formulas."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    patterns = [r'\$\$', r'\$[^$]+\$', r'\\begin\{', r'\\frac', r'\\sum', r'\\int']
    return any(re.search(p, content) for p in patterns)


def run_node(script_name, *args):
    """Run a Node.js script from the scripts directory."""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    cmd = ["node", script_path] + list(args)
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SCRIPT_DIR)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python build_pdf.py <input.html> <output.pdf> [--no-math] [--clean]")
        print("  --no-math  Skip MathJax pre-rendering")
        print("  --clean    Remove intermediate HTML files after PDF generation")
        sys.exit(1)

    input_html = os.path.abspath(sys.argv[1])
    output_pdf = os.path.abspath(sys.argv[2])
    skip_math = "--no-math" in sys.argv
    do_clean = "--clean" in sys.argv

    if not os.path.exists(input_html):
        print(f"Error: Input HTML not found: {input_html}")
        sys.exit(1)

    # Determine the working HTML (pre-rendered or original)
    work_html = input_html

    if not skip_math and has_math(input_html):
        print("[1/2] Pre-rendering math formulas (MathJax → SVG)...")
        prerender_html = input_html.replace(".html", "_prerendered.html")
        run_node("mathjax_to_svg.js", input_html, prerender_html)
        work_html = prerender_html
    else:
        if skip_math:
            print("[1/2] Skipping math pre-render (--no-math)")
        else:
            print("[1/2] No math detected, skipping pre-render")

    print("[2/2] Generating PDF (Playwright)...")
    run_node("playwright_to_pdf.js", work_html, output_pdf)

    # Clean up intermediate files
    if do_clean and work_html != input_html:
        os.remove(work_html)
        print(f"  Cleaned: {work_html}")

    # Verify output
    if os.path.exists(output_pdf):
        size_mb = os.path.getsize(output_pdf) / (1024 * 1024)
        print(f"\n[OK] PDF generated: {output_pdf} ({size_mb:.1f} MB)")
    else:
        print(f"\n[FAIL] PDF not created!")
        sys.exit(1)


if __name__ == "__main__":
    main()
