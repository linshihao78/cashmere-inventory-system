import tkinter as tk
import os
import sys
import sqlite3

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

db_file = os.path.join(base_dir, "inventory.db")

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def get_product_info():
    name = entry.get()
    color = color_entry.get()
    size = size_entry.get()
    return name, color, size

def clear_input():
    entry.delete(0, "end")
    color_entry.delete(0, "end")
    size_entry.delete(0, "end")
    price_entry.delete(0, "end")
    stock_entry.delete(0, "end")
    warning_entry.delete(0, "end")
    result_text.delete("1.0", "end")

def show_result(text):
    result_text.delete("1.0", "end")
    result_text.insert("1.0", text)

def search_product():
    name, color, size = get_product_info()

    cursor.execute("""
    SELECT name, color, size, price, stock
    FROM products
    WHERE name = ? AND color = ? AND size = ?
    """, (name, color, size))

    product = cursor.fetchone()

    return product

def show_search_result():
    product = search_product()

    if product:
        show_result(
            f'商品：{product[0]}\n'
            f'颜色：{product[1]}\n'
            f'尺码：{product[2]}\n'
            f'价格：{product[3]}元\n'
            f'库存：{product[4]}件'
        )
    else:
        show_result("没有找到该商品")

def update_product():
    name, color, size = get_product_info()

    try:
        price = float(price_entry.get())
        stock = int(stock_entry.get())
    except ValueError:
        return "价格必须是数字，库存必须是整数"

    if price < 0:
        return "价格不能小于0"

    if stock < 0:
        return "库存不能小于0"

    cursor.execute("""
    SELECT id
    FROM products
    WHERE name = ? AND color = ? AND size = ?
    """, (name, color, size))

    product = cursor.fetchone()

    if product:
        cursor.execute("""
        UPDATE products
        SET price = ?, stock = ?
        WHERE id = ?
        """, (price, stock, product[0]))

        conn.commit()

        return "修改成功"

    return "没有找到该商品"

def show_all_products():
    cursor.execute("SELECT name, color, size, price, stock FROM products")

    products = cursor.fetchall()

    text = ""

    for product in products:
        text += (
            f'商品：{product[0]} '
            f'颜色：{product[1]} '
            f'尺码：{product[2]} '
            f'价格：{product[3]}元 '
            f'库存：{product[4]}件\n'
        )

    show_result(text)
def show_update_result():
    result = update_product()
    show_result(result)

def add_product():
    name, color, size = get_product_info()

    if name == "":
        show_result("请输入商品名称")
        return

    cursor.execute("""
    SELECT id
    FROM products
    WHERE name = ? AND color = ? AND size = ?
    """, (name, color, size))

    if cursor.fetchone():
        show_result("该商品已经存在")
        return

    try:
        price = float(price_entry.get())
        stock = int(stock_entry.get())

        if price < 0:
            show_result("价格不能小于0")
            return

        if stock < 0:
            show_result("库存不能小于0")
            return

    except ValueError:
        show_result("价格必须是数字，库存必须是整数")
        return

    cursor.execute("""
    INSERT INTO products (name, color, size, price, stock)
    VALUES (?, ?, ?, ?, ?)
    """, (name, color, size, price, stock))

    conn.commit()

    show_result("添加成功")

def subtract_product():
    name, color, size = get_product_info()

    if name == "":
        show_result("请输入商品名称")
        return

    cursor.execute("""
    SELECT id
    FROM products
    WHERE name = ? AND color = ? AND size = ?
    """, (name, color, size))

    product = cursor.fetchone()

    if product:
        cursor.execute("""
        DELETE FROM products
        WHERE id = ?
        """, (product[0],))

        conn.commit()

        show_result("删除成功")
        return

    show_result("没有找到该商品")

def stock_in():
    name, color, size = get_product_info()

    try:
        stock = int(stock_entry.get())
    except ValueError:
        show_result("入库数量必须是整数")
        return

    if name == "":
        show_result("请输入商品名称")
        return

    if stock < 0:
        show_result("入库数量不能小于0")
        return

    cursor.execute("""
    SELECT id, stock
    FROM products
    WHERE name = ? AND color = ? AND size = ?
    """, (name, color, size))

    product = cursor.fetchone()

    if product:
        new_stock = product[1] + stock

        cursor.execute("""
        UPDATE products
        SET stock = ?
        WHERE id = ?
        """, (new_stock, product[0]))

        conn.commit()

        show_result("入库成功")
        return

    show_result("没有找到该商品")

def stock_out():
    name, color, size = get_product_info()

    try:
        stock = int(stock_entry.get())
    except ValueError:
        show_result("出库数量必须是整数")
        return

    if name == "":
        show_result("请输入商品名称")
        return

    if stock < 0:
        show_result("出库数量不能小于0")
        return

    cursor.execute("""
    SELECT id, stock
    FROM products
    WHERE name = ? AND color = ? AND size = ?
    """, (name, color, size))

    product = cursor.fetchone()

    if product:
        current_stock = product[1]

        if stock > current_stock:
            show_result("出库数量不能大于当前库存")
            return

        new_stock = current_stock - stock

        cursor.execute("""
        UPDATE products
        SET stock = ?
        WHERE id = ?
        """, (new_stock, product[0]))

        conn.commit()

        show_result("出库成功")
        return

    show_result("没有找到该商品")
def stock_warning():
    try:
        warning = int(warning_entry.get())
    except ValueError:
        show_result("输入错误")
        return

    if warning < 0:
        show_result("预警线不能小于0")
        return

    cursor.execute("""
    SELECT name, color, size, stock
    FROM products
    WHERE stock <= ?
    """, (warning,))

    products = cursor.fetchall()

    text = ""

    for product in products:
        text += (
            f'商品：{product[0]} '
            f'颜色：{product[1]} '
            f'尺码：{product[2]} '
            f'库存：{product[3]}件\n'
        )

    if text == "":
        show_result("没有库存不足的商品")
    else:
        show_result(text)

window = tk.Tk()

window.title("商品库存管理")
window.geometry("500x300")

input_frame = tk.Frame(window)
input_frame.pack(pady=10)

name_label = tk.Label(input_frame, text="商品名称：")
name_label.grid(row=0,column=0,padx=5,pady=5)

entry = tk.Entry(input_frame,width=20)
entry.grid(row=0,column=1,padx=5,pady=5)

color_label = tk.Label(input_frame, text="颜色：")
color_label.grid(row=1, column=0, padx=5, pady=5)

color_entry = tk.Entry(input_frame, width=20)
color_entry.grid(row=1, column=1, padx=5, pady=5)

size_label = tk.Label(input_frame, text="尺码：")
size_label.grid(row=2, column=0, padx=5, pady=5)

size_entry = tk.Entry(input_frame, width=20)
size_entry.grid(row=2, column=1, padx=5, pady=5)

price_label = tk.Label(input_frame, text="价格：")
price_label.grid(row=3, column=0, padx=5, pady=5)

price_entry = tk.Entry(input_frame, width=20)
price_entry.grid(row=3, column=1, padx=5, pady=5)

stock_label = tk.Label(input_frame, text="库存：")
stock_label.grid(row=4, column=0, padx=5, pady=5)

stock_entry = tk.Entry(input_frame, width=20)
stock_entry.grid(row=4, column=1, padx=5, pady=5)

warning_label = tk.Label(input_frame, text="库存预警线：")
warning_label.grid(row=5, column=0, padx=5, pady=5)

warning_entry = tk.Entry(input_frame, width=20)
warning_entry.grid(row=5, column=1, padx=5, pady=5)

button_frame = tk.Frame(window)
button_frame.pack(pady=10)
button = tk.Button(
        button_frame,
        text="查询商品",
        command=show_search_result,
        width=10
    )
button.grid(row=0,column=0,padx=5)

clear_button = tk.Button(
    button_frame,
    text="清空",
    command=clear_input,
    width=10
)

clear_button.grid(row=0,column=1,padx=5)

show_button = tk.Button(
    button_frame,
    text="显示全部商品",
    command=show_all_products,
    width=10
)

show_button.grid(row=0, column=2, padx=5)

update_button = tk.Button(
        button_frame,
        text="修改商品",
        command=show_update_result,
        width=10
    )
update_button.grid(row=1,column=0,padx=5)

add_button = tk.Button(
    button_frame,
    text="新增商品",
    command=add_product,
    width=10
    )
add_button.grid(row=1,column=1,padx=5)

subtract_button = tk.Button(
        button_frame,
        text="删除商品",
        command=subtract_product,
        width=10
    )

subtract_button.grid(row=1, column=2, padx=5)

stock_in_button= tk.Button(
    button_frame,
    text="入库"
    ,command=stock_in
    ,width=10
)
stock_in_button.grid(row=2,column=0,padx=5)

stock_out_button= tk.Button(
    button_frame,
    text="出库"
    ,command=stock_out
    ,width=10
)
stock_out_button.grid(row=2,column=1,padx=5)

stock_warning_button= tk.Button(
    button_frame,
    text="库存预警"
    ,command=stock_warning
    ,width=10
)
stock_warning_button.grid(row=2,column=2,padx=5)

result_frame = tk.Frame(window)
result_frame.pack(pady=10)

result_text = tk.Text(result_frame,width=40,height=8)
result_text.pack()

window.mainloop()
