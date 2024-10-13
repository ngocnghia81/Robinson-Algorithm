from flask import Flask, render_template, request, jsonify
from sympy import Or, And, Not, Implies, to_cnf
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import p, q, r  # Định nghĩa các biến logic
from itertools import combinations

app = Flask(__name__)


# Hàm chuyển đổi từ Implies thành dạng hiển thị 'p => q'
def display_expression(expr):
    if isinstance(expr, Implies):
        return f"{expr.args[0]} => {expr.args[1]}"
    elif isinstance(expr, Not):
        return f"~({display_expression(expr.args[0])})"
    elif isinstance(expr, Or):
        return " | ".join([display_expression(arg) for arg in expr.args])
    elif isinstance(expr, And):
        return " & ".join([display_expression(arg) for arg in expr.args])
    else:
        return str(expr)


def process_expressions(hypotheses_str, conclusion):
    expressions = []
    steps = []

    # Tách các giả thuyết ngăn cách bởi dấu phẩy
    hypotheses = [hyp.strip() for hyp in hypotheses_str.split(',')]

    # Hàm để chuyển đổi ký hiệu người dùng nhập thành biểu thức logic hợp lệ
    def convert_to_logic(expr_str):
        expr_str = expr_str.replace('!', 'Not(')  # Xử lý phủ định
        expr_str = expr_str.replace('=>', ',')  # Thay thế '=>' bằng dấu phẩy để đặt trong Implies()
        expr_str = expr_str.replace('V', 'Or(')  # Xử lý phép OR
        expr_str = expr_str.replace('^', 'And(')  # Xử lý phép AND

        # Đóng dấu ngoặc cho các hàm logic
        if 'Or(' in expr_str or 'And(' in expr_str:
            expr_str += ')' * expr_str.count('(')

        return expr_str

    # Nhập các giả thuyết vào danh sách
    cnf_steps = []  # Danh sách lưu trữ các bước chuẩn hóa

    for expr_str in hypotheses:
        try:
            expr_str = convert_to_logic(expr_str)
            parsed_expr = parse_expr(f"Implies({expr_str})")
            cnf_expr = to_cnf(parsed_expr, simplify=True)
            expressions.append(cnf_expr)
            step_number = len(steps) + 1  # Tính số thứ tự
            cnf_steps.append(
                f"Bước {step_number}: Giả thuyết '{display_expression(parsed_expr)}' đã được chuẩn hóa thành CNF: {cnf_expr}.")
        except Exception as e:
            step_number = len(steps) + 1  # Tính số thứ tự
            steps.append(f"Bước {step_number}: Lỗi khi nhập biểu thức '{expr_str}': {e}. Vui lòng nhập lại.")

    # Xử lý kết luận
    try:
        conclusion_str = convert_to_logic(conclusion)
        parsed_conclusion = Not(to_cnf(parse_expr(f"Implies({conclusion_str})"), simplify=True))
        expressions.append(parsed_conclusion)
        step_number = len(steps) + 1  # Tính số thứ tự
        cnf_steps.append(
            f"Bước {step_number}: Kết luận '{display_expression(parse_expr(f'Implies({conclusion_str})'))}' đã được thêm vào danh sách dưới dạng phủ định: {parsed_conclusion}.")
    except Exception as e:
        step_number = len(steps) + 1  # Tính số thứ tự
        steps.append(f"Bước {step_number}: Lỗi khi nhập kết luận '{conclusion}': {e}.")

    # Gộp các bước lại thành một bước
    step_number = len(steps) + 1  # Tính số thứ tự
    steps.append(f"Bước {step_number}: Các giả thuyết và kết luận: {', '.join(cnf_steps)}")

    # Hiển thị mảng biểu thức
    step_number = len(steps) + 1  # Tính số thứ tự
    steps.append(f"Bước {step_number}: Mảng biểu thức: {[display_expression(expr) for expr in expressions]}")

    # Kiểm tra chứng minh
    while True:
        if is_proved(expressions, steps):
            return steps, True
        if not create_new_expression(expressions, steps):
            return steps + [f"Bước cuối: Kết luận bị bác bỏ."], False


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
                    steps.append(
                        f"{display_expression(pair[0])} và {display_expression(pair[1])} có biến đối ngẫu là: {i}.")
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
    hypotheses = request.form['hypotheses']
    conclusion = request.form['conclusion']
    steps, proved = process_expressions(hypotheses, conclusion)
    return jsonify({'steps': steps, 'proved': proved})


if __name__ == '__main__':
    app.run(debug=True)
