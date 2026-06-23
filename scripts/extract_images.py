"""
Extract embedded images from specific pages of a PDF.
Usage: python extract_images.py <pdf_path> <page_number> <output_dir>

Extracts all images found on the given page (1-based) and saves them as PNG files.
Output files are named: page{N}_{img_index}.png
"""
import sys
import os

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is required. Install with: pip install PyMuPDF")
    sys.exit(1)


def extract_images(pdf_path, page_num, output_dir):
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    if page_num < 1 or page_num > len(doc):
        print(f"Error: page {page_num} out of range (1-{len(doc)})")
        doc.close()
        sys.exit(1)

    page = doc[page_num - 1]  # 0-based
    images = page.get_images(full=True)

    if not images:
        print(f"No images found on page {page_num}")
        doc.close()
        return []

    saved = []
    for i, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        img_bytes = base_image["image"]
        ext = base_image["ext"]

        out_name = f"page{page_num}_{i+1}.{ext}"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, "wb") as f:
            f.write(img_bytes)

        size_kb = len(img_bytes) / 1024
        print(f"  Extracted: {out_name} ({size_kb:.1f} KB, {base_image.get('width','?')}x{base_image.get('height','?')})")
        saved.append(out_path)

    doc.close()
    print(f"Extracted {len(saved)} image(s) from page {page_num}")
    return saved


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python extract_images.py <pdf_path> <page_number> <output_dir>")
        print("  page_number: 1-based page number to extract images from")
        print("  output_dir: directory to save extracted PNG files")
        sys.exit(1)

    pdf_path = sys.argv[1]
    page_num = int(sys.argv[2])
    output_dir = sys.argv[3]

    extract_images(pdf_path, page_num, output_dir)
