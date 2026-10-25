# =====================================================================
# ## 1. Module / Import (การนำเข้าโมดูล)
# ทำหน้าที่นำเข้าเครื่องมือสำเร็จรูปที่มีอยู่ใน Python มาช่วยทำงาน:
# - `json`, `os`: ใช้สำหรับจัดการไฟล์และการเซฟ/โหลดข้อมูล
# - `dataclass`: ช่วยสร้าง Class สำหรับเก็บข้อมูลได้สั้นและง่ายขึ้น
# - `Decimal`: ใช้คำนวณตัวเลขทางการเงินเพื่อป้องกันทศนิยมเพี้ยน
# - `typing`: ใช้ทำ Type Hinting ช่วยบอกชนิดตัวแปรให้โปรแกรมเมอร์อ่านง่ายขึ้น
# =====================================================================
import json
import os
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple

# =====================================================================
# ## 2. OOP (Object-Oriented Programming)
# การมองโค้ดเป็น "วัตถุ" (Object) แต่ละส่วนมีหน้าที่ของตัวเองชัดเจน
# `Product` ทำหน้าที่เป็นพิมพ์เขียวสำหรับสร้าง "สินค้า 1 ชิ้น"
# =====================================================================
@dataclass
class Product:
    code: str
    name: str
    price: Decimal
    stock: int

# `Inventory` ทำหน้าที่เป็น "โกดัง" จัดการเรื่องสต็อกและไฟล์
class Inventory:
    def __init__(self, default_products: Optional[List[Product]] = None, filename: str = "inventory.json"):
        self.filename = filename
        
        # =====================================================================
        # ## 3.1 Data Structures: Dictionary
        # ใช้ `{}` (Dictionary) ในการเก็บข้อมูลสินค้า โดยใช้ "รหัสสินค้า" เป็น Key
        # ทำให้เวลาค้นหาสินค้า (Search) ทำได้รวดเร็วมากโดยไม่ต้องวนลูปหาทีละตัว
        # =====================================================================
        self.products: Dict[str, Product] = {}
        self.load_data(default_products)

    # =====================================================================
    # ## 4. Function / Method
    # ฟังก์ชันที่ถูกเขียนอยู่ภายใน Class จะเรียกว่า "Method" 
    # มีหน้าที่รับผิดชอบงานเฉพาะเจาะจง เช่น โหลดข้อมูล, เซฟข้อมูล, ค้นหา
    # =====================================================================
    def load_data(self, default_products: Optional[List[Product]]) -> None:
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    p = Product(item["code"], item["name"], Decimal(item["price"]), item["stock"])
                    self.products[p.code] = p
        else:
            if default_products:
                for p in default_products:
                    self.products[p.code] = p
            self.save_data()

    def save_data(self) -> None:
        # =====================================================================
        # ## 3.2 Data Structures: Array / List
        # ใช้ `[]` (List) ในการเก็บข้อมูลสินค้าที่ถูกแปลงเป็นดิกชันนารีแล้วนำมาเรียงต่อกัน
        # เพื่อเตรียมนำไปเซฟลงไฟล์ JSON
        # =====================================================================
        data_to_save = []
        for p in self.products.values():
            data_to_save.append({
                "code": p.code,
                "name": p.name,
                "price": str(p.price), 
                "stock": p.stock
            })
            
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def get_all(self) -> List[Product]:
        return list(self.products.values())

    def find_product(self, code: str) -> Optional[Product]:
        return self.products.get(code.upper())

    def add_product(self, product: Product) -> None:
        product.code = product.code.upper()
        if product.code in self.products:
            # ใช้คำสั่ง raise ในการ 'โยน' ข้อผิดพลาดออกไปให้ระบบจัดการ
            raise ValueError(f"รหัสสินค้า '{product.code}' มีอยู่แล้ว")
        if not product.code or not product.name or not product.price.is_finite():
            raise ValueError("ข้อมูลสินค้าไม่ถูกต้อง (ชื่อหรือรหัสอาจว่างเปล่า)")
        if product.price <= 0 or product.stock < 0:
            raise ValueError("ราคาต้องมากกว่า 0 และสต็อกต้องไม่ติดลบ")
        
        self.products[product.code] = product
        self.save_data()


# `Sale` ทำหน้าที่เป็น "ตะกร้าสินค้า" รับผิดชอบการคำนวณบิลปัจจุบัน
class Sale:
    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self.items: Dict[str, int] = {}  

    def add_item(self, code: str, quantity: int) -> None:
        product = self.inventory.find_product(code)
        if not product:
            raise ValueError("ไม่พบรหัสสินค้านี้")
        if quantity <= 0:
            raise ValueError("จำนวนสินค้าต้องมากกว่า 0")
        
        current_qty = self.items.get(product.code, 0)
        if current_qty + quantity > product.stock:
            raise ValueError(f"สต็อกไม่พอ! (มี {product.stock} ชิ้น, คุณต้องการ {current_qty + quantity})")
        
        self.items[product.code] = current_qty + quantity

    def get_items(self) -> List[Tuple[Product, int]]:
        return [(self.inventory.find_product(code), qty) for code, qty in self.items.items()]

    def total(self) -> Decimal:
        return sum(
            (item.price * qty for item, qty in self.get_items()),
            Decimal("0.00")
        )

    def checkout(self, received: Decimal) -> Tuple[Decimal, Decimal, Decimal, List[Tuple[Product, int]]]:
        if not self.items:
            raise ValueError("ยังไม่มีสินค้าในรายการขาย")
        if not received.is_finite() or received < self.total():
            raise ValueError("เงินที่รับมาไม่เพียงพอหรือไม่ถูกต้อง")

        total = self.total()
        change = received - total
        sold_items = self.get_items()

        for product, qty in sold_items:
            product.stock -= qty
            
        self.inventory.save_data() 
        self.cancel()
        
        return total, received, change, sold_items

    def cancel(self) -> None:
        self.items.clear()


# `CashierApp` ทำหน้าที่เป็น "หน้าจอ (UI)" จัดการการแสดงผลและการกดเมนู
class CashierApp:
    def __init__(self):
        default_items = [
            Product("P001", "น้ำดื่ม", Decimal("10.00"), 20),
            Product("P002", "ขนมปัง", Decimal("25.00"), 10),
            Product("P003", "นมกล่อง", Decimal("18.50"), 15),
        ]
        self.inventory = Inventory(default_products=default_items)
        self.sale = Sale(self.inventory)

    def run(self) -> None:
        menu = (
            "\n=== ระบบแคชเชียร์ ===\n"
            "[1] ดูสินค้าทั้งหมด     [2] ค้นหาสินค้า    [3] เพิ่มสินค้าใหม่\n"
            "[4] เพิ่มสินค้าลงตะกร้า   [5] ดูตะกร้าสินค้า  [6] ชำระเงิน\n"
            "[7] ยกเลิกบิลปัจจุบัน     [0] ออกจากระบบ\n"
            "เลือกเมนู: "
        )
        
        while True:
            # =====================================================================
            # ## 5. Exception Handling (การดักจับข้อผิดพลาด)
            # โครงสร้าง try...except ใช้คลุมจุดที่อาจเกิด Error จากการกรอกข้อมูลของผู้ใช้
            # ถ้าโปรแกรมพัง มันจะวิ่งมาที่ `except` แทนที่จะปิดตัวโปรแกรมทิ้ง
            # =====================================================================
            try:
                choice = input(menu).strip()
                if choice == "1": self._show_inventory()
                elif choice == "2": self._search_product()
                elif choice == "3": self._add_product()
                elif choice == "4": self._add_sale_item()
                elif choice == "5": self._show_cart()
                elif choice == "6": self._checkout()
                elif choice == "7":
                    self.sale.cancel()
                    print("\n[ ยกเลิกบิลเรียบร้อยแล้ว ]")
                elif choice == "0":
                    print("\n[ ปิดโปรแกรม ขอบคุณที่ใช้บริการ ]")
                    break
                else:
                    print("\n[!] กรุณาเลือกเมนู 0-7")
            except (EOFError, KeyboardInterrupt):
                print("\n\n[ ปิดโปรแกรมฉุกเฉิน ]")
                break
            except Exception as e:
                print(f"\n[!] เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")

    # ฟังก์ชันต่างๆ ด้านล่างนี้คือ Method ของหน้าจอ UI 
    # ทำหน้าที่พิมพ์ข้อความและรับ Input จากผู้ใช้
    def _show_inventory(self) -> None:
        print("\n" + "="*50)
        print(f"{'รหัส':<6} | {'ชื่อสินค้า':<15} | {'ราคา (บาท)':>10} | {'คงเหลือ':>8}")
        print("-" * 50)
        for p in self.inventory.get_all():
            print(f"{p.code:<6} | {p.name:<15} | {p.price:>10.2f} | {p.stock:>8}")
        print("="*50)

    def _search_product(self) -> None:
        code = input("ใส่รหัสสินค้า: ").strip()
        p = self.inventory.find_product(code)
        if p:
            print(f"\nพบสินค้า: {p.name} | ราคา {p.price:.2f} บาท | สต็อก {p.stock} ชิ้น")
        else:
            print("\n[!] ไม่พบสินค้านี้ในระบบ")

    def _add_product(self) -> None:
        print("\n--- เพิ่มสินค้าใหม่ ---")
        try:
            code = input("รหัสสินค้า: ").strip()
            name = input("ชื่อสินค้า: ").strip()
            price = Decimal(input("ราคา (บาท): ").strip())
            stock = int(input("จำนวนคงเหลือ: ").strip())
            self.inventory.add_product(Product(code, name, price, stock))
            print(f"\n[ เพิ่มสินค้า '{name}' สำเร็จ ]")
        except (ValueError, InvalidOperation) as e:
            print(f"\n[!] ข้อผิดพลาด: {e}")

    def _add_sale_item(self) -> None:
        print("\n--- เพิ่มสินค้าลงตะกร้า ---")
        try:
            code = input("รหัสสินค้า: ").strip()
            quantity = int(input("จำนวน: ").strip())
            self.sale.add_item(code, quantity)
            print("\n[ เพิ่มลงตะกร้าสำเร็จ ]")
        except ValueError as e:
            print(f"\n[!] ข้อผิดพลาด: {e}")

    def _show_cart(self) -> None:
        items = self.sale.get_items()
        if not items:
            print("\n[ ยังไม่มีสินค้าในตะกร้า ]")
            return
            
        print("\n" + "="*50)
        print(f"{'ชื่อสินค้า':<15} | {'จำนวน':>6} | {'ราคา/ชิ้น':>10} | {'รวม':>10}")
        print("-" * 50)
        for p, qty in items:
            print(f"{p.name:<15} | {qty:>6} | {p.price:>10.2f} | {p.price * qty:>10.2f}")
        print("-" * 50)
        print(f"{'ยอดรวมทั้งสิ้น:':<37} {self.sale.total():>10.2f} บาท")
        print("="*50)

    def _checkout(self) -> None:
        if not self.sale.items:
            print("\n[!] ยังไม่มีสินค้าในตะกร้า")
            return
            
        self._show_cart()
        try:
            received = Decimal(input("\nรับเงินมา (บาท): ").strip())
            total, received, change, sold_items = self.sale.checkout(received)
            self._print_receipt(sold_items, total, received, change)
        except (ValueError, InvalidOperation) as e:
            print(f"\n[!] ข้อผิดพลาด: {e}")

    def _print_receipt(self, sold_items: List[Tuple[Product, int]], total: Decimal, received: Decimal, change: Decimal) -> None:
        print("\n" + "="*40)
        print(f"{'ใบเสร็จรับเงิน':^40}")
        print("="*40)
        print(f"{'รายการ':<15} | {'จำนวน':>6} | {'รวม':>12}")
        print("-" * 40)
        for p, qty in sold_items:
            print(f"{p.name:<15} | {qty:>6} | {p.price * qty:>12.2f}")
        print("-" * 40)
        print(f"{'ยอดรวม:':<25} {total:>12.2f} บาท")
        print(f"{'รับเงิน:':<25} {received:>12.2f} บาท")
        print(f"{'เงินทอน:':<25} {change:>12.2f} บาท")
        print("="*40 + "\n")

if __name__ == "__main__":
    app = CashierApp()
    app.run()