from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    """สินค้าในร้านหนึ่งชนิด"""

    code: str
    name: str
    price: Decimal
    stock: int


def main():
    products = [
        Product("P001", "น้ำดื่ม", Decimal("10.00"), 20),
        Product("P002", "ขนมปัง", Decimal("25.00"), 10),
        Product("P003", "นมกล่อง", Decimal("18.50"), 15),
    ]
    print("=== ข้อมูลสินค้าตัวอย่าง ===")
    for product in products:
        print(f"{product.code} | {product.name} | {product.price:.2f} บาท | คงเหลือ {product.stock}")


if __name__ == "__main__":
    main()
