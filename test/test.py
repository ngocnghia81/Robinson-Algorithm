from flask import Flask, render_template, request, jsonify
from sympy import Or, And, Not, Implies, to_cnf
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import p, q, r
from itertools import combinations

app = Flask(__name__)

# Hàm xử lý nhập liệu
def process_expressions(hypotheses_str, conclusion_str):
    expressions = []
    steps = []

    # Tách các giả thuyết bởi dấu phẩy và xử lý từng giả thuyết
    hypotheses = hypotheses_str.split(',')
    for expr_str in hypotheses:
        try:
            # Thay thế các ký hiệu trong biểu thức
            expr_str = expr_str.replace('!', 'Not(').replace('V', 'Or').replace('^', 'And').replace('=>', 'Implies')
            parsed_expr = to_cnf(parse_expr(expr_str), simplify=True)
            expressions.append(parsed_expr)
            steps.append(f"Bước {len(steps) + 1}: Biểu thức '{expr_str}' đã được thêm vào danh sách và được chuẩn hóa thành CNF: {parsed_expr}.")
        except Exception as e:
            steps.append(f"Lỗi khi nhập biểu thức '{expr_str}': {e}. Vui lòng nhập lại.")

    # Xử lý kết luận
    try:
        conclusion_str = conclusion_str.replace('!', 'Not(').replace('V', 'Or').replace('^', 'And').replace('=>', 'Implies')
        parsed_conclusion = Not(to_cnf(parse_expr(conclusion_str), simplify=True))
        expressions.append(parsed_conclusion)
        steps.append(f"Bước {len(steps) + 1}: Kết luận '{conclusion_str}' đã được thêm vào danh sách dưới dạng phủ định: {parsed_conclusion}.")
    except Exception as e:
        steps.append(f"Lỗi khi nhập kết luận '{conclusion_str}': {e}.")

    # Kiểm tra chứng minh
    while True:
        if is_proved(expressions, steps):
            return steps, True
        if not create_new_expression(expressions, steps):
            return steps + ["Bước cuối: Kết luận bị bác bỏ."], False

def is_proved(expressions, steps):
    steps.append("Đang kiểm tra xem có cặp biểu thức đối ngẫu không...")
    for i in range(len(expressions)):
        for j in range(i + 1, len(expressions)):
            if expressions[i] == ~expressions[j]:
                steps.append(f"Bài toán được chứng minh bởi các mệnh đề: {expressions[i]} và {expressions[j]}.")
                return True
    steps.append("Không tìm thấy 2 mệnh đề nào đối ngẫu, thực hiện tạo biểu thức mới.")
    return False

def create_new_expression(expressions, steps):
    steps.append("Đang tạo biểu thức mới từ các cặp biểu thức...")
    pairs = combinations(expressions, 2)

    for pair in list(pairs):
        for i in pair[0].args:
            for j in pair[1].args:
                if i == ~j:
                    steps.append(f"{pair[0]} và {pair[1]} có biến đối ngẫu là: {i}.")
                    new_args = [arg for arg in (pair[0].args + pair[1].args) if arg != i and arg != ~i]
                    new_expression = Or(*new_args)
                    steps.append(f'Ta có biểu thức mới là: {new_expression}.')
                    expressions.append(new_expression)
                    steps.append('Mảng biểu thức cập nhật: ' + str(expressions))
                    return True
    steps.append('Không tạo được biểu thức mới.')
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    hypotheses = request.form['hypothesis']
    conclusion = request.form['conclusion']
    steps, proved = process_expressions(hypotheses, conclusion)
    return jsonify({'steps': steps, 'proved': proved})

if __name__ == '__main__':
    app.run(debug=True)
