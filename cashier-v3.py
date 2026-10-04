from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass
class Product:

    code: str
    name: str
    price: Decimal
    stock: int


class Inventory:

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


class Sale:

    def __init__(self, inventory):
        self.inventory = inventory
        self.items = {}  # รหัสสินค้า -> จำนวนที่เลือก

    def add_item(self, code, quantity):
        product = self.inventory.find_product(code)
        if product is None:
            raise ValueError("ไม่พบรหัสสินค้า")
        if quantity <= 0:
            raise ValueError("จำนวนสินค้าต้องมากกว่า 0")
        if self.items.get(product.code, 0) + quantity > product.stock:
            raise ValueError("สินค้าในสต็อกไม่เพียงพอ")
        self.items[product.code] = self.items.get(product.code, 0) + quantity

    def show_items(self):
        if not self.items:
            print("ยังไม่มีสินค้าในรายการขาย")
            return
        print("รายการขาย:")
        for code, quantity in self.items.items():
            product = self.inventory.find_product(code)
            print(f"{product.name} x {quantity} @ {product.price:.2f} บาท")

    def total(self):
        """คำนวณยอดรวมจากราคาและจำนวนสินค้า"""
        return sum(
            (self.inventory.find_product(code).price * quantity
             for code, quantity in self.items.items()),
            Decimal("0.00"),
        )

    def checkout(self, received):
        """รับเงิน ตัดสต็อก และคืนข้อมูลการขายเมื่อชำระสำเร็จ"""
        if not self.items:
            raise ValueError("ยังไม่มีสินค้าในรายการขาย")
        if not received.is_finite() or received.as_tuple().exponent < -2:
            raise ValueError("จำนวนเงินต้องเป็นตัวเลขที่มีทศนิยมไม่เกิน 2 ตำแหน่ง")
        total = self.total()
        if received < total:
            raise ValueError("เงินที่รับมาไม่เพียงพอ")
        sold_items = [(self.inventory.find_product(code), quantity)
                      for code, quantity in self.items.items()]
        for product, quantity in sold_items:
            product.stock -= quantity
        self.items.clear()
        return total, received, received - total, sold_items


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


def add_sale_item_from_input(sale):
    try:
        code = input("รหัสสินค้าที่ต้องการขาย: ").strip()
        quantity = int(input("จำนวน: ").strip())
        sale.add_item(code, quantity)
        print("เพิ่มลงรายการขายเรียบร้อย")
    except ValueError as error:
        print(f"ข้อผิดพลาด: {error}")


def checkout_from_input(sale):
    try:
        print(f"ยอดรวม: {sale.total():.2f} บาท")
        received = Decimal(input("รับเงิน (บาท): ").strip())
        total, received, change, _ = sale.checkout(received)
        print(f"ชำระสำเร็จ | ยอดรวม {total:.2f} | รับ {received:.2f} | ทอน {change:.2f} บาท")
    except (ValueError, InvalidOperation) as error:
        print(f"ข้อผิดพลาด: {error}")


def main():
    inventory = Inventory([
        Product("P001", "น้ำดื่ม", Decimal("10.00"), 20),
        Product("P002", "ขนมปัง", Decimal("25.00"), 10),
        Product("P003", "นมกล่อง", Decimal("18.50"), 15),
    ])
    sale = Sale(inventory)
    while True:
        print("\n=== ระบบแคชเชียร์: เลือกสินค้า ===")
        choice = input("1 แสดงสินค้า | 2 ค้นหา | 3 เพิ่มสินค้า | 4 เลือกขาย | 5 รายการขาย | 6 ชำระเงิน | 0 ออก: ").strip()
        if choice == "1":
            inventory.show_products()
        elif choice == "2":
            product = inventory.find_product(input("รหัสสินค้า: ").strip())
            print(f"พบ: {product.name} ราคา {product.price:.2f} บาท" if product else "ไม่พบสินค้า")
        elif choice == "3":
            add_product_from_input(inventory)
        elif choice == "4":
            add_sale_item_from_input(sale)
        elif choice == "5":
            sale.show_items()
        elif choice == "6":
            checkout_from_input(sale)
        elif choice == "0":
            break
        else:
            print("กรุณาเลือกเมนูที่ถูกต้อง")


if __name__ == "__main__":
    main()
