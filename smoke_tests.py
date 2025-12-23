"""
Простые smoke‑проверки основных сценариев.
Запуск: python smoke_tests.py
"""

from datetime import datetime
from db import init_db
from models import add_material, register_receipt, register_issue, get_material_by_name
from models_extended import (
    get_all_locations,
    get_all_suppliers,
    add_production_order,
    add_reservation,
    get_available_balance,
    check_and_create_replenishment_request,
)


def run():
    print("Инициализация БД...")
    init_db()

    print("Создаем материал с min/max stock...")
    material_name = "SMOKE-Тест"
    existing = get_material_by_name(material_name)
    if existing:
        material_id = existing["id"]
        print(f"Материал '{material_name}' уже существует, используем ID={material_id}")
    else:
        material_id = add_material(material_name, "шт", "other", min_stock=2, max_stock=10)
        print(f"Материал '{material_name}' успешно добавлен с ID={material_id}")
    assert material_id, "Материал не создан"

    print("Приход партии с локацией и поставщиком...")
    locations = get_all_locations()
    suppliers = get_all_suppliers()
    loc_id = locations[0]["id"] if locations else None
    supplier_id = suppliers[0]["id"] if suppliers else None
    batch_id = register_receipt(material_id, 5, 10.0, loc_id, supplier_id, None, "SN-SMOKE", None)
    assert batch_id, "Приход не создан"

    print("Создаем заказ и резервируем материал...")
    order_id = add_production_order(f"SMK-{datetime.now().timestamp():.0f}", datetime.now().date())
    assert order_id, "Заказ не создан"
    res_id = add_reservation(order_id, material_id, 1.0)
    assert res_id, "Резерв не создан"

    print("Проверяем списание с учетом FIFO/LIFO и резерва...")
    available_before = get_available_balance(material_id)
    assert available_before >= 4.0, "Доступный остаток меньше ожидаемого"
    ok = register_issue(material_id, 2.0, "FIFO", order_id)
    assert ok, "Списание не прошло"

    print("Проверяем авто-заявку на пополнение при падении ниже минимума...")
    check_and_create_replenishment_request(material_id)

    print("Smoke tests OK")


if __name__ == "__main__":
    run()

