# views.py

from flask import Blueprint, jsonify, request
from .models import db, Book
from PIL import Image
import pytesseract
import easyocr
import tempfile

main = Blueprint('main', __name__)

# 设置Tesseract OCR的路径
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

# 获取所有图书
@main.route('/books', methods=['GET'])
def get_all_books():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    books = Book.query.order_by(Book.create_date.desc()).paginate(page=page, per_page=page_size, error_out=False)
    
    book_list = [book.to_dict() for book in books.items]
    
    return jsonify({
        'books': book_list,
        'count': books.total,
        'page': page,
        'page_size': page_size
    })

# 获取单个图书
@main.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    book_data = {
        'id': book.id,
        'name': book.name,
        'author': book.author,
        'create_date': book.create_date.strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify({'book': book_data})

# 创建新图书
@main.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    new_book = Book(name=data['name'], author=data['author'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book created successfully'}), 201

# 更新图书信息
@main.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    data = request.get_json()
    book.name = data['name']
    book.author = data['author']
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

# 删除图书
@main.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

# OCR识别图片
@main.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file:
        # 将图像加载到Pillow中
        image= Image.open(file)
        # 使用Tesseract OCR进行文本识别
        text = pytesseract.image_to_string(image, lang='chi_sim')
        return jsonify({'text': text})
    
@main.route('/ocr', methods=['POST'])
def ocr():
    # 检查请求中是否包含文件
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded!'}), 400
    
    # 从请求中获取图片文件
    image = request.files['image']
    
    # 将文件保存到临时文件中
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        image.save(temp_file)
        temp_file_path = temp_file.name
    
    # 初始化 EasyOCR 读取器，并指定中文和英文作为识别语言
    reader = easyocr.Reader(['ch_sim', 'en'])  # 指定中文和英文
    
    # 使用 EasyOCR 进行文本识别
    result = reader.readtext(temp_file_path)

    print(result)
    
    # 提取文本内容
    text_content = [item[1] for item in result]
    
    # 将文本内容组织成 JSON 格式并返回
    return jsonify({'text_content': text_content}), 200