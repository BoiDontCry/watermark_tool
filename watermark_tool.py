import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import io
import os  # 新加，用于路径
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color

# 全局字体路径（默认您的，运行时检查/选择）
DEFAULT_FONT_PATH = 'C:/Users/lzzwf/OneDrive/Desktop/mydemocode/LXGWWenKai-Regular.ttf'
FONT_PATH = DEFAULT_FONT_PATH
FONT_NAME = 'ChineseFont'

def load_font():
    global FONT_PATH
    if not os.path.exists(FONT_PATH):
        messagebox.showwarning("字体缺失", "默认字体不存在，请选择中文字体文件（.ttf）")
        FONT_PATH = filedialog.askopenfilename(filetypes=[("TTF Fonts", "*.ttf")])
        if not FONT_PATH:
            messagebox.showerror("错误", "未选择字体，无法继续")
            exit()
    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))  # 注册到reportlab
    except Exception as e:
        messagebox.showerror("错误", f"加载字体失败: {e}")
        exit()

def add_watermark(image, text):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, 40)  # 用动态路径
    width, height = image.size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    draw.text((width - text_width - 10, height - text_height - 10), text, font=font, fill=(255, 0, 0, 128))
    return image

def add_watermark_to_pdf(input_pdf_path, output_pdf_path, text):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        media_box = page.mediabox
        width = float(media_box.width)
        height = float(media_box.height)
        
        # 创建临时水印页
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        c.setFont(FONT_NAME, 40)
        c.setFillColor(Color(1, 0, 0, alpha=0.5))
        c.drawString(width - 200, height - 80, text)
        c.save()
        
        # 合并
        packet.seek(0)
        watermark_reader = PdfReader(packet)
        page.merge_page(watermark_reader.pages[0])
        writer.add_page(page)
    
    with open(output_pdf_path, "wb") as output_stream:
        writer.write(output_stream)

def process_file(file_path, text):
    images = []
    ext = file_path.lower().split('.')[-1]
    
    try:
        if ext in ['png', 'jpg', 'jpeg']:
            img = Image.open(file_path).convert('RGB')
            images.append(add_watermark(img, text))
            return images, False
        elif ext == 'pdf':
            return [file_path], True
        else:
            raise ValueError("不支持的文件类型")
    except Exception as e:
        messagebox.showerror("错误", f"处理文件失败: {e}")
        return None, False

def generate_pdf(data, output_path, is_pdf=False):
    if not data:
        return
    if is_pdf:
        add_watermark_to_pdf(data[0], output_path, text)
    else:
        c = canvas.Canvas(output_path, pagesize=letter)
        c.setFont(FONT_NAME, 12)
        for img in data:
            img_data = io.BytesIO()
            img.save(img_data, format='JPEG')
            img_data.seek(0)
            width, height = img.size
            c.setPageSize((width, height))
            img_data.seek(0)
            image_reader = ImageReader(img_data)
            c.drawImage(image_reader, 0, 0, width=width, height=height)
            c.showPage()
        c.save()

def main():
    load_font()  # 启动时加载字体
    root = tk.Tk()
    root.title("水印工具")
    root.geometry("300x150")
    
    text_var = tk.StringVar()
    tk.Label(root, text="水印文本:").pack()
    tk.Entry(root, textvariable=text_var).pack()
    
    def upload():
        file_path = filedialog.askopenfilename(filetypes=[("Images/PDF", "*.png *.jpg *.jpeg *.pdf")])
        if not file_path:
            return
        global text
        text = text_var.get().strip()
        if not text:
            messagebox.showwarning("警告", "请输入水印文本")
            return
        result, is_pdf = process_file(file_path, text)
        if result:
            output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if output_path:
                generate_pdf(result, output_path, is_pdf)
                messagebox.showinfo("成功", "PDF已导出")
    
    tk.Button(root, text="上传并处理", command=upload).pack()
    root.mainloop()

if __name__ == "__main__":
    main()
