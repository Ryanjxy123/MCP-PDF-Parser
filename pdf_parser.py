import fitz  
import argparse
import os
import unicodedata
import gc
import sys
from collections import Counter

class TextHandler:
    @staticmethod
    def decode_text(text, font=None, encoding=None):
        try:
            if isinstance(text, bytes):
                try:
                    text = text.decode("utf-8")
                except UnicodeDecodeError:
                    text = text.decode("latin-1")
            text = unicodedata.normalize("NFKC", text)
            return text
        except Exception:
            return str(text)

class ImageHandler:
    def __init__(self):
        self.image_counter = 0

    def extract_image(self, xref, doc, images_dir, page_num):
        try:
            pix = fitz.Pixmap(doc, xref)
            if pix.n - pix.alpha < 4:
                img_name = f"page{page_num+1}_img{self.image_counter+1}.png"
                img_path = os.path.join(images_dir, img_name)
                pix.save(img_path)
            else:
                pix = fitz.Pixmap(fitz.csRGB, pix)
                img_name = f"page{page_num+1}_img{self.image_counter+1}.png"
                img_path = os.path.join(images_dir, img_name)
                pix.save(img_path)
            self.image_counter += 1
            return img_name
        except Exception as e:
            print(f"Image extraction failed: {e}", file=sys.stderr)
            return None
        finally:
            if 'pix' in locals():
                pix = None

class LayoutParser:
    math_ranges = [
        (0x2200, 0x22FF),  
        (0x2A00, 0x2AFF), 
        (0x27C0, 0x27EF),  
        (0x2980, 0x29FF), 
        (0x1D400, 0x1D7FF),  
        (0x0370, 0x03FF),  
    ]

    def __init__(self):
        self.base_font_size = 12
        self.text_handler = TextHandler()

    def extract_font_metrics(self, page):
        text_blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_IMAGES | fitz.TEXT_DEHYPHENATE | fitz.TEXT_INHIBIT_SPACES)["blocks"]
        font_sizes = []
        for block in text_blocks:
            if block["type"] == 0: 
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(round(span["size"], 1))
        if not font_sizes:
            return [], self.base_font_size
        size_counter = Counter(font_sizes)
        base_size = size_counter.most_common(1)[0][0]
        sorted_sizes = sorted(set(font_sizes), reverse=True)
        return sorted_sizes, base_size

    def determine_heading_level(self, font_size, base_size):
        if not base_size:
            return 0
        ratio = font_size / base_size
        if ratio >= 1.8:
            return 1
        elif ratio >= 1.5:
            return 2
        elif ratio >= 1.2:
            return 3
        return 0

    def format_text_block(self, block, base_size):
        output_lines = []
        max_font_size = 0
        for line in block["lines"]:
            for span in line["spans"]:
                span_size = round(span["size"], 1)
                if span_size > max_font_size:
                    max_font_size = span_size
        heading_level = self.determine_heading_level(max_font_size, base_size)
        last_line_bottom = None
        paragraph_words = []
        for line in block["lines"]:
            line_parts = []
            for span in line["spans"]:
                text = self.text_handler.decode_text(span.get("text", ""), span.get("font", None), span.get("encoding", None)).strip()
                if not text:
                    continue
                flags = span.get("flags", 0)
                if flags & 1 and flags & 2:
                    text = f"***{text}***"
                elif flags & 1:
                    text = f"**{text}**"
                elif flags & 2:
                    text = f"*{text}*"
                line_parts.append(text)
            line_text = " ".join(line_parts).strip()
            if not line_text:
                continue
            line_bbox = line["bbox"]
            line_top = line_bbox[1]
            if last_line_bottom is not None:
                vertical_gap = line_top - last_line_bottom
                if vertical_gap > base_size * 1.2:
                    if paragraph_words:
                        joined_para = " ".join(paragraph_words)
                        if heading_level > 0:
                            output_lines.append(f"{'#' * heading_level} {joined_para}")
                        else:
                            output_lines.append(joined_para)
                        output_lines.append("")
                        paragraph_words = []
            last_line_bottom = line_bbox[3]
            paragraph_words.append(line_text)
        if paragraph_words:
            joined_para = " ".join(paragraph_words)
            if heading_level > 0:
                output_lines.append(f"{'#' * heading_level} {joined_para}")
            else:
                output_lines.append(joined_para)
            output_lines.append("")
        return "\n".join(output_lines) + "\n"

class PDFParser:
    def __init__(self):
        self.layout_parser = LayoutParser()
        self.image_handler = ImageHandler()

    def process_page(self, page, doc, images_dir):
        page_content = []
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_IMAGES | fitz.TEXT_DEHYPHENATE | fitz.TEXT_INHIBIT_SPACES)["blocks"]
        if not blocks:
            return ""

        blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
        _, base_size = self.layout_parser.extract_font_metrics(page)
        self.layout_parser.base_font_size = base_size or self.layout_parser.base_font_size

        image_list = page.get_images(full=True)
        image_map = []
        for idx, img in enumerate(image_list):
            if len(img) >= 4:
                xref = img[0]
                width = img[2]
                height = img[3]
                image_map.append({"xref": xref, "width": width, "height": height, "index": idx})

        used_images = set()
        image_idx = 0

        for block in blocks:
            if block["type"] == 0:
                md_text = self.layout_parser.format_text_block(block, base_size)
                if md_text.strip():
                    page_content.append(md_text)
            elif block["type"] == 1:
                while image_idx < len(image_map) and image_map[image_idx]["xref"] in used_images:
                    image_idx += 1
                if image_idx < len(image_map):
                    img_info = image_map[image_idx]
                    xref = img_info["xref"]
                    img_name = self.image_handler.extract_image(xref, doc, images_dir, page.number)
                    if img_name:
                        caption = f"Image {self.image_handler.image_counter} (Page {page.number+1})"
                        md_img_path = os.path.join(os.path.basename(images_dir), img_name).replace("\\", "/")
                        page_content.append(f"![{caption}]({md_img_path})\n\n")
                        used_images.add(xref)
                    image_idx += 1
        return "".join(page_content)

    def convert_pdf_to_markdown(self, pdf_path, output_path, split_by_page=False, page_separator="---"):
        markdown_content = []
        images_dir = os.path.splitext(output_path)[0] + "_images"
        os.makedirs(images_dir, exist_ok=True)
        try:
            with fitz.open(pdf_path) as doc:
                print(f"Processing: {os.path.basename(pdf_path)} ({doc.page_count} pages)")
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    page_md = self.process_page(page, doc, images_dir)
                    markdown_content.append(page_md)
                    if split_by_page and page_num < doc.page_count - 1:
                        
                        markdown_content.append(f"\n{page_separator}\n\n")
                    del page
                    gc.collect()
                    if (page_num + 1) % 10 == 0 or page_num == doc.page_count - 1:
                        print(f"Processed: {page_num + 1}/{doc.page_count} pages")
            with open(output_path, "w", encoding="utf-8") as md_file:
                md_file.write("".join(markdown_content))
            print(f"\nConversion complete: Markdown saved to {output_path}")
            print(f"Images directory: {images_dir}")
            return True
        except Exception as e:
            print(f"Error processing PDF: {str(e)}", file=sys.stderr)
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF to Markdown Parser with Advanced Layout and Encoding Support")
    parser.add_argument("input_pdf", help="Input PDF file path")
    parser.add_argument("output_md", help="Output Markdown file path")
    parser.add_argument("--split", action="store_true", help="Split output by page")
    parser.add_argument("--no-split", dest="split", action="store_false", help="Do not split output by page")
    parser.add_argument("--page-separator", default="---", help="Custom page separator string when splitting by page")
    parser.set_defaults(split=False)
    args = parser.parse_args()
    if not os.path.isfile(args.input_pdf):
        print(f"Error: Input file does not exist - {args.input_pdf}", file=sys.stderr)
        sys.exit(1)
    parser_obj = PDFParser()
    success = parser_obj.convert_pdf_to_markdown(args.input_pdf, args.output_md, args.split, args.page_separator)
    sys.exit(0 if success else 1)
