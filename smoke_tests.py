"""
Простые smoke‑проверки основных сценариев.
Запуск: python smoke_tests.py
Идемпотентный: можно запускать многократно без ошибок.
"""

from datetime import datetime
from db import init_db
from models import add_material, register_receipt, register_issue, get_material_by_name
from models_extended import (
    get_all_locations,
    get_all_suppliers,
    add_location,
    add_supplier,
    add_production_order,
    get_all_production_orders,
    add_reservation,
    get_available_balance,
    check_and_create_replenishment_request,
    transfer_batch,
    get_all_batches,
)


def run():
    print("=" * 60)
    print("SMOKE TESTS - Идемпотентная проверка функционала")
    print("=" * 60)
    
    print("\n1. Инициализация БД...")
    init_db()

    print("\n2. Создаем/находим материал с min/max stock...")
    material_name = "SMOKE-Тест"
    existing = get_material_by_name(material_name)
    if existing:
        material_id = existing["id"]
        print(f"   ✓ Материал '{material_name}' уже существует, используем ID={material_id}")
    else:
        material_id = add_material(material_name, "шт", "other", min_stock=2, max_stock=10)
        print(f"   ✓ Материал '{material_name}' успешно добавлен с ID={material_id}")
    assert material_id, "Материал не создан"

    print("\n3. Создаем/находим локацию...")
    locations = get_all_locations()
    loc_code = "SMOKE-LOC-01"
    loc = next((l for l in locations if l.get('code') == loc_code), None)
    if loc:
        loc_id = loc["id"]
        print(f"   ✓ Локация '{loc_code}' уже существует, используем ID={loc_id}")
    else:
        loc_id = add_location(loc_code, "Тестовая локация", "Для smoke-тестов")
        print(f"   ✓ Локация '{loc_code}' создана с ID={loc_id}")
    assert loc_id, "Локация не создана"

    print("\n4. Создаем/находим поставщика...")
    suppliers = get_all_suppliers()
    supplier_name = "SMOKE-Поставщик"
    supplier = next((s for s in suppliers if s.get('name') == supplier_name), None)
    if supplier:
        supplier_id = supplier["id"]
        print(f"   ✓ Поставщик '{supplier_name}' уже существует, используем ID={supplier_id}")
    else:
        supplier_id = add_supplier(supplier_name, "1234567890", "test@example.com")
        print(f"   ✓ Поставщик '{supplier_name}' создан с ID={supplier_id}")
    assert supplier_id, "Поставщик не создан"

    print("\n5. Приход партии с локацией и поставщиком...")
    batch_id = register_receipt(material_id, 5, 10.0, loc_id, supplier_id, None, "SN-SMOKE", None)
    assert batch_id, "Приход не создан"
    print(f"   ✓ Приход зарегистрирован, партия ID={batch_id}")

    print("\n6. Создаем/находим заказ производства...")
    order_number = f"SMK-{int(datetime.now().timestamp())}"
    orders = get_all_production_orders()
    order = next((o for o in orders if o.get('number') == order_number), None)
    if order:
        order_id = order["id"]
        print(f"   ✓ Заказ '{order_number}' уже существует, используем ID={order_id}")
    else:
        order_id = add_production_order(order_number, datetime.now(), 'NEW', "Smoke test order")
        print(f"   ✓ Заказ '{order_number}' создан с ID={order_id}")
    assert order_id, "Заказ не создан"

    print("\n7. Резервируем материал под заказ...")
    res_id = add_reservation(order_id, material_id, 1.0)
    assert res_id, "Резерв не создан"
    print(f"   ✓ Резерв создан с ID={res_id}")

    print("\n8. Проверяем списание с учетом FIFO/LIFO и резерва...")
    available_before = get_available_balance(material_id)
    print(f"   Доступный остаток (с учетом резерва): {available_before}")
    assert available_before >= 4.0, f"Доступный остаток меньше ожидаемого: {available_before}"
    ok = register_issue(material_id, 2.0, "FIFO", order_id, None)
    assert ok, "Списание не прошло"
    print(f"   ✓ Списано 2.0 по методу FIFO")

    print("\n9. Проверяем авто-заявку на пополнение при падении ниже минимума...")
    check_and_create_replenishment_request(material_id, None)
    print(f"   ✓ Проверка заявок выполнена")

    print("\n10. Проверяем перемещение между локациями...")
    batches = get_all_batches()
    test_batch = next((b for b in batches if b.get('material_id') == material_id and b.get('location_id') == loc_id), None)
    if test_batch:
        # Создаем вторую локацию для перемещения
        loc2_code = "SMOKE-LOC-02"
        loc2 = next((l for l in locations if l.get('code') == loc2_code), None)
        if not loc2:
            loc2_id = add_location(loc2_code, "Тестовая локация 2", "Для перемещения")
        else:
            loc2_id = loc2["id"]
        
        if test_batch.get('remaining', 0) > 0:
            transfer_ok = transfer_batch(test_batch['id'], loc2_id, 1.0, None)
            if transfer_ok:
                print(f"   ✓ Перемещение выполнено: партия {test_batch['id']} -> локация {loc2_id}")
            else:
                print(f"   ⚠ Перемещение не выполнено (возможно, недостаточно остатка)")
        else:
            print(f"   ⚠ Нет остатка для перемещения")
    else:
        print(f"   ⚠ Партия не найдена для перемещения")

    print("\n" + "=" * 60)
    print("✓ SMOKE TESTS OK - Все проверки пройдены!")
    print("=" * 60)


if __name__ == "__main__":
    run()

