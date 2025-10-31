import sys
import os
from PIL import Image, ImageDraw, ImageFont  # 最小导入 Pillow

# 最小 Tkinter：只导入 filedialog 和 messagebox，不创建 full root
import tkinter as tk
from tkinter import filedialog, messagebox

# 可选 PDF 支持：条件导入
try:
    from PyPDF2 import PdfReader, PdfWriter
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import Color
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    messagebox.showwarning("警告", "未安装 PyPDF2 或 ReportLab，PDF 水印功能不可用。只支持图像。")

# 字体路径：运行时选择，不默认嵌入
FONT_PATH = None
FONT_NAME = 'ChineseFont'

def load_font():
    global FONT_PATH
    root = tk.Tk()  # 临时 root 只为 filedialog
    root.withdraw()  # 隐藏窗口
    if FONT_PATH and os.path.exists(FONT_PATH):
        root.destroy()
        return
    FONT_PATH = filedialog.askopenfilename(title="选择中文字体 (.ttf)", filetypes=[("TTF Fonts", "*.ttf")])
    root.destroy()
    if not FONT_PATH:
        messagebox.showerror("错误", "未选择字体，无法继续")
        sys.exit(1)
    if not os.path.exists(FONT_PATH):
        messagebox.showerror("错误", f"字体文件 {FONT_PATH} 不存在")
        sys.exit(1)
    if PDF_SUPPORT:
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
        except Exception as e:
            messagebox.showerror("错误", f"加载字体失败: {e}")
            sys.exit(1)

def add_watermark(image, text):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, 40)
    width, height = image.size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    draw.text((width - text_width - 10, height - text_height - 10), text, font=font, fill=(255, 0, 0, 128))
    return image

def add_watermark_to_pdf(input_pdf_path, output_path, text):
    if not PDF_SUPPORT:
        messagebox.showerror("错误", "PDF 支持不可用。请安装 PyPDF2 和 ReportLab。")
        return
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        media_box = page.mediabox
        width, height = float(media_box.width), float(media_box.height)
        
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        c.setFont(FONT_NAME, 40)
        c.setFillColor(Color(1, 0, 0, alpha=0.5))
        c.drawString(width - 200, height - 80, text)
        c.save()
        
        packet.seek(0)
        watermark_reader = PdfReader(packet)
        page.merge_page(watermark_reader.pages[0])
        writer.add_page(page)
    
    with open(output_path, "wb") as output_stream:
        writer.write(output_stream)

def process_and_save(file_path, text, output_path):
    ext = file_path.lower().split('.')[-1]
    try:
        if ext in ['png', 'jpg', 'jpeg']:
            img = Image.open(file_path).convert('RGB')
            watermarked = add_watermark(img, text)
            watermarked.save(output_path, format='JPEG', quality=85)  # 压缩输出
            messagebox.showinfo("成功", f"水印图像保存到 {output_path}")
        elif ext == 'pdf' and PDF_SUPPORT:
            add_watermark_to_pdf(file_path, output_path, text)
            messagebox.showinfo("成功", f"水印 PDF 保存到 {output_path}")
        else:
            messagebox.showerror("错误", "不支持的文件类型。只支持 PNG/JPG/JPEG/PDF。")
    except Exception as e:
        messagebox.showerror("错误", f"处理文件失败: {e}")

def main():
    load_font()  # 启动时加载字体（用 filedialog）
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口，只用对话框
    
    print("欢迎使用水印工具（最小 GUI 版）")
    file_path = filedialog.askopenfilename(title="选择输入文件 (图像/PDF)", filetypes=[("Images/PDF", "*.png *.jpg *.jpeg *.pdf")])
    if not file_path:
        root.destroy()
        return
    text = input("请输入水印文本: ").strip()  # CLI 输入文本
    if not text:
        messagebox.showwarning("警告", "水印文本为空，无法继续")
        root.destroy()
        return
    output_path = filedialog.asksaveasfilename(title="保存输出文件", defaultextension=".jpg", filetypes=[("JPEG/PDF", "*.jpg *.pdf")])
    if not output_path:
        root.destroy()
        return
    process_and_save(file_path, text, output_path)
    root.destroy()

if __name__ == "__main__":
    main()
