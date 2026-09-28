from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass
class Product:
    """สินค้าในร้านหนึ่งชนิด"""

    code: str
    name: str
    price: Decimal
    stock: int


class Inventory:
    """เก็บและจัดการสินค้าตามรหัส"""

    def __init__(self, products):
        self.products = {product.code: product for product in products}

    def show_products(self):
        print("รหัส | ชื่อ | ราคา (บาท) | คงเหลือ")
        for product in self.products.values():
            print(f"{product.code} | {product.name} | {product.price:.2f} | {product.stock}")

    def find_product(self, code):
        return self.products.get(code.upper())

    def add_product(self, product):
        if product.code in self.products:
            raise ValueError("รหัสสินค้านี้มีอยู่แล้ว")
        if not product.code or not product.name or not product.price.is_finite():
            raise ValueError("ข้อมูลสินค้าไม่ถูกต้อง")
        if product.price <= 0 or product.price.as_tuple().exponent < -2 or product.stock < 0:
            raise ValueError("ราคา/จำนวนคงเหลือไม่ถูกต้อง")
        self.products[product.code] = product


def add_product_from_input(inventory):
    try:
        code = input("รหัสสินค้า: ").strip().upper()
        name = input("ชื่อสินค้า: ").strip()
        price = Decimal(input("ราคา (บาท): ").strip())
        stock = int(input("จำนวนคงเหลือ: ").strip())
        inventory.add_product(Product(code, name, price, stock))
        print("เพิ่มสินค้าเรียบร้อย")
    except (ValueError, InvalidOperation) as error:
        print(f"ข้อผิดพลาด: {error}")


def main():

    inventory = Inventory([
        Product("P001", "น้ำดื่ม", Decimal("10.00"), 20),
        Product("P002", "ขนมปัง", Decimal("25.00"), 10),
        Product("P003", "นมกล่อง", Decimal("18.50"), 15),
    ])
    while True:
        print("\n=== จัดการสินค้า ===")
        choice = input("1 แสดงสินค้า | 2 ค้นหา | 3 เพิ่มสินค้า | 0 ออก: ").strip()
        if choice == "1":
            inventory.show_products()
        elif choice == "2":
            product = inventory.find_product(input("รหัสสินค้า: ").strip())
            print(f"พบ: {product.name} ราคา {product.price:.2f} บาท" if product else "ไม่พบสินค้า")
        elif choice == "3":
            add_product_from_input(inventory)
        elif choice == "0":
            break
        else:
            print("กรุณาเลือกเมนูที่ถูกต้อง")


if __name__ == "__main__":
    main()
