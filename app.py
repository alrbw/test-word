import streamlit as st
from word_search_generator import WordSearch
from PIL import Image, ImageDraw, ImageFont
import io
import math
import os

# Cấu hình trang và ép giao diện Light Theme toàn diện
st.set_page_config(page_title="Word Name Generate", layout="centered")

st.markdown("""
    <style>
    /* 1. Nền tổng thể và thanh bên */
    .stApp {
        background-color: #FFFFFF;
        color: #222222;
    }
    [data-testid="stSidebar"] {
        background-color: #F8F9FB;
        border-right: 1px solid #E6E9EF;
    }

    /* 2. Ép màu nút bấm (Button) - Sửa lỗi nút màu đen */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #222222 !important;
        border: 1px solid #DCE0E5 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #FF69B4 !important;
        color: #FF69B4 !important;
        background-color: #FFF5F9 !important;
    }

    /* 3. Ép màu nút Download */
    div.stDownloadButton > button {
        background-color: #FF69B4 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #FF1493 !important;
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3) !important;
    }

    /* 4. Chỉnh ô nhập liệu (Text Area) và nhãn chữ */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #222222 !important;
        border: 1px solid #DCE0E5 !important;
    }
    label, p, h1, h2, h3 {
        color: #222222 !important;
    }

    /* 5. Ẩn menu và footer không cần thiết để giao diện sạch hơn */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def create_layered_design(puzzle_obj, main_color, base_text_color, size_px=3000):
    img = Image.new('RGBA', (size_px, size_px), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    grid = puzzle_obj.puzzle
    grid_size = len(grid)
    margin = size_px * 0.05 
    usable_size = size_px - (2 * margin)
    cell_size = usable_size / grid_size
    
    # Khớp chính xác với tên file bạn đã upload lên GitHub
    font_path = "ARLRDBD.TTF" 
    try:
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, int(cell_size * 0.65))
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    highlighted_cells = set()
    for word_obj in puzzle_obj.placed_words:
        r, c = word_obj.start_row, word_obj.start_column
        d_row, d_col = word_obj.direction.value
        for i in range(len(word_obj.text)):
            highlighted_cells.add((r + i * d_row, c + i * d_col))

    # LAYER 1: CHỮ RANDOM
    for r_idx, row in enumerate(grid):
        for c_idx, char in enumerate(row):
            if (r_idx, c_idx) not in highlighted_cells:
                x = margin + (c_idx * cell_size) + (cell_size / 2)
                y = margin + (r_idx * cell_size) + (cell_size / 2)
                draw.text((x, y), char, fill=base_text_color, font=font, anchor="mm")

    # LAYER 2: VIỀN CAPSULE
    for word_obj in puzzle_obj.placed_words:
        r1, c1 = word_obj.start_row, word_obj.start_column
        d_row, d_col = word_obj.direction.value
        r2 = r1 + d_row * (len(word_obj.text) - 1)
        c2 = c1 + d_col * (len(word_obj.text) - 1)
        
        x1 = margin + (c1 * cell_size) + (cell_size / 2)
        y1 = margin + (r1 * cell_size) + (cell_size / 2)
        x2 = margin + (c2 * cell_size) + (cell_size / 2)
        y2 = margin + (r2 * cell_size) + (cell_size / 2)
        
        rad = cell_size * 0.45
        thickness = max(10, int(cell_size * 0.1))
        angle = math.atan2(y2 - y1, x2 - x1)
        dx, dy = math.sin(angle) * rad, math.cos(angle) * rad
        
        draw.polygon([(x1+dx, y1-dy), (x1-dx, y1+dy), (x2-dx, y2+dy), (x2+dx, y2-dy)], fill=main_color)
        draw.ellipse([x1-rad, y1-rad, x1+rad, y1+rad], fill=main_color)
        draw.ellipse([x2-rad, y2-rad, x2+rad, y2+rad], fill=main_color)

        inner_rad = rad - thickness
        idx, idy = math.sin(angle) * inner_rad, math.cos(angle) * inner_rad
        draw.polygon([(x1+idx, y1-idy), (x1-idx, y1+idy), (x2-idx, y2+idy), (x2+idx, y2-idy)], fill=(255,255,255,0))
        draw.ellipse([x1-inner_rad, y1-inner_rad, x1+inner_rad, y1+inner_rad], fill=(255,255,255,0))
        draw.ellipse([x2-inner_rad, y2-inner_rad, x2+inner_rad, y2+inner_rad], fill=(255,255,255,0))

    # LAYER 3: CHỮ TRONG TÊN
    for r_idx, row in enumerate(grid):
        for c_idx, char in enumerate(row):
            if (r_idx, c_idx) in highlighted_cells:
                x = margin + (c_idx * cell_size) + (cell_size / 2)
                y = margin + (r_idx * cell_size) + (cell_size / 2)
                draw.text((x, y), char, fill=main_color, font=font, anchor="mm")
            
    buf = io.BytesIO()
    img.save(buf, format="PNG", dpi=(300, 300))
    return buf.getvalue()

# --- Giao diện chính ---
st.title("Word Name Generate")

# Tạo form để kiểm soát việc load lại trang
with st.sidebar:
    st.header("Cấu hình")
    with st.form("my_form"):
        c_h = st.color_picker("Highlight Color", "#FF69B4")
        c_b = st.color_picker("Base Text Color", "#222222")
        txt = st.text_area("Names (comma separated)", help="Nhập tên rồi ấn Generate để xem kết quả")
        submit_button = st.form_submit_button(label="Generate Design")

# Chỉ chạy logic khi người dùng ấn nút Generate
if submit_button and txt:
    names = [n.strip().upper() for n in txt.split(",") if n.strip()]
    if names:
        total_chars = sum(len(n) for n in names)
        density_size = math.ceil(math.sqrt(total_chars * 1.5))
        final_grid_size = max(density_size, max(len(n) for n in names))
        
        try:
            puzzle = WordSearch(",".join(names), size=final_grid_size)
            img_bytes = create_layered_design(puzzle, c_h, c_b)
            st.image(img_bytes, use_container_width=True)
            st.download_button("Download Image (300DPI)", img_bytes, "crossword_design.png", "image/png")
        except:
            # Tự động nới rộng grid nếu quá chật
            puzzle = WordSearch(",".join(names), size=final_grid_size + 2)
            img_bytes = create_layered_design(puzzle, c_h, c_b)
            st.image(img_bytes, use_container_width=True)
            st.download_button("Download Image (300DPI)", img_bytes, "crossword_design.png", "image/png")
elif not txt:
    st.info("Vui lòng nhập danh sách tên ở thanh bên trái và nhấn 'Generate Design'.")

