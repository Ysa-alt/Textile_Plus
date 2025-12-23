"""
Расширенный модуль для работы с данными.
Содержит функции для работы с заявками на пополнение, адресами хранения,
резервированием, поставщиками, качеством, пользователями и аудитом.
"""

from db import get_connection
from datetime import datetime
from typing import List, Dict, Optional


# ==================== ПОЛЬЗОВАТЕЛИ И АУДИТ ====================

def get_user_by_username(username: str) -> Optional[Dict]:
    """Получает пользователя по имени."""
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def log_audit(user_id: Optional[int], action: str, details: Optional[str] = None):
    """Записывает действие в журнал аудита (единая точка)."""
    connection = get_connection()
    if not connection:
        return
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO audit_log (user_id, action, details, created_at) VALUES (%s, %s, %s, %s)",
            (user_id, action, details, datetime.now())
        )
        connection.commit()
    except Exception as e:
        print(f"Ошибка при записи в журнал аудита: {e}")
    finally:
        cursor.close()
        connection.close()


# Алиас под wording ТЗ
def logaudit(user_id: Optional[int], action: str, details: Optional[str] = None):
    return log_audit(user_id, action, details)


# ==================== АДРЕСА ХРАНЕНИЯ ====================

def add_location(code: str, name: str, description: str = None, user_id: Optional[int] = None) -> Optional[int]:
    """Добавляет адрес хранения."""
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO locations (code, name, description) VALUES (%s, %s, %s)",
            (code, name, description)
        )
        connection.commit()
        log_audit(user_id, f"Создан адрес хранения {code}", description)
        return cursor.lastrowid
    except Exception as e:
        print(f"Ошибка при добавлении адреса: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def update_location(location_id: int, code: str, name: str, description: str = None, user_id: Optional[int] = None) -> bool:
    """Обновляет адрес хранения."""
    connection = get_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE locations SET code=%s, name=%s, description=%s WHERE id=%s",
            (code, name, description, location_id)
        )
        connection.commit()
        log_audit(user_id, f"Изменен адрес хранения ID={location_id}", f"{code} / {name}")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении адреса: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def delete_location(location_id: int, user_id: Optional[int] = None) -> bool:
    """Удаляет адрес хранения."""
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM locations WHERE id=%s", (location_id,))
        connection.commit()
        log_audit(user_id, f"Удален адрес хранения ID={location_id}")
        return True
    except Exception as e:
        print(f"Ошибка при удалении адреса: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_all_locations() -> List[Dict]:
    """Получает все адреса хранения."""
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM locations ORDER BY code")
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении адресов: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


# ==================== ПОСТАВЩИКИ И ДОГОВОРЫ ====================

def add_supplier(name: str, inn: str = None, contact: str = None, user_id: Optional[int] = None) -> Optional[int]:
    """Добавляет поставщика."""
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO suppliers (name, inn, contact) VALUES (%s, %s, %s)",
            (name, inn, contact)
        )
        connection.commit()
        log_audit(user_id, f"Создан поставщик {name}", contact)
        return cursor.lastrowid
    except Exception as e:
        print(f"Ошибка при добавлении поставщика: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def update_supplier(supplier_id: int, name: str, inn: str = None, contact: str = None, user_id: Optional[int] = None) -> bool:
    """Обновляет поставщика."""
    connection = get_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE suppliers SET name=%s, inn=%s, contact=%s WHERE id=%s",
            (name, inn, contact, supplier_id)
        )
        connection.commit()
        log_audit(user_id, f"Изменен поставщик ID={supplier_id}", name)
        return True
    except Exception as e:
        print(f"Ошибка при обновлении поставщика: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def delete_supplier(supplier_id: int, user_id: Optional[int] = None) -> bool:
    """Удаляет поставщика."""
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM suppliers WHERE id=%s", (supplier_id,))
        connection.commit()
        log_audit(user_id, f"Удален поставщик ID={supplier_id}")
        return True
    except Exception as e:
        print(f"Ошибка при удалении поставщика: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_all_suppliers() -> List[Dict]:
    """Получает всех поставщиков."""
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM suppliers ORDER BY name")
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении поставщиков: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def add_contract(supplier_id: int, number: str, contract_date: datetime, description: str = None, user_id: Optional[int] = None) -> Optional[int]:
    """Добавляет договор с поставщиком."""
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO contracts (supplier_id, number, contract_date, description) VALUES (%s, %s, %s, %s)",
            (supplier_id, number, contract_date, description)
        )
        connection.commit()
        log_audit(user_id, f"Создан договор {number}", f"Поставщик {supplier_id}")
        return cursor.lastrowid
    except Exception as e:
        print(f"Ошибка при добавлении договора: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def update_contract(contract_id: int, supplier_id: int, number: str, contract_date: datetime, description: str = None, user_id: Optional[int] = None) -> bool:
    """Обновляет договор."""
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE contracts SET supplier_id=%s, number=%s, contract_date=%s, description=%s WHERE id=%s",
            (supplier_id, number, contract_date, description, contract_id)
        )
        connection.commit()
        log_audit(user_id, f"Изменен договор ID={contract_id}", number)
        return True
    except Exception as e:
        print(f"Ошибка при обновлении договора: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def delete_contract(contract_id: int, user_id: Optional[int] = None) -> bool:
    """Удаляет договор."""
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM contracts WHERE id=%s", (contract_id,))
        connection.commit()
        log_audit(user_id, f"Удален договор ID={contract_id}")
        return True
    except Exception as e:
        print(f"Ошибка при удалении договора: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_contracts_by_supplier(supplier_id: int) -> List[Dict]:
    """Получает договоры поставщика."""
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM contracts WHERE supplier_id = %s ORDER BY signed_at DESC",
            (supplier_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении договоров: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


# ==================== ЗАКАЗЫ ПРОИЗВОДСТВА ====================

def add_production_order(number: str, order_date: datetime, status: str = 'NEW', description: str = None, user_id: Optional[int] = None) -> Optional[int]:
    """Создает заказ производства."""
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO production_orders (number, order_date, status, description, created_at) VALUES (%s, %s, %s, %s, %s)",
            (number, order_date, status, description, datetime.now())
        )
        connection.commit()
        log_audit(user_id, f"Создан заказ {number}", status)
        return cursor.lastrowid
    except Exception as e:
        print(f"Ошибка при создании заказа: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def update_production_order_status(order_id: int, status: str, user_id: Optional[int] = None) -> bool:
    """Обновляет статус заказа."""
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE production_orders SET status=%s WHERE id=%s", (status, order_id))
        connection.commit()
        log_audit(user_id, f"Статус заказа ID={order_id} изменен на {status}")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении статуса заказа: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def delete_production_order(order_id: int, user_id: Optional[int] = None) -> bool:
    """Удаляет заказ производства."""
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM production_orders WHERE id=%s", (order_id,))
        connection.commit()
        log_audit(user_id, f"Удален заказ производства ID={order_id}")
        return True
    except Exception as e:
        print(f"Ошибка при удалении заказа: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_all_production_orders() -> List[Dict]:
    """Получает все заказы производства."""
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM production_orders ORDER BY created_at DESC")
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении заказов: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


# ==================== РЕЗЕРВИРОВАНИЕ ====================

def add_reservation(order_id: int, material_id: int, reserved_qty: float, user_id: Optional[int] = None) -> Optional[int]:
    """Создает резервирование материала под заказ (ACTIVE)."""
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO reservations (order_id, material_id, reserved_qty, quantity, status, created_at) VALUES (%s, %s, %s, %s, 'ACTIVE', %s)",
            (order_id, material_id, reserved_qty, reserved_qty, datetime.now())
        )
        connection.commit()
        log_audit(user_id, f"Резервирование материала ID={material_id}", f"order={order_id}, qty={reserved_qty}")
        return cursor.lastrowid
    except Exception as e:
        print(f"Ошибка при создании резервирования: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def release_reservation(reservation_id: int, status: str = 'RELEASED', user_id: Optional[int] = None) -> bool:
    """Снимает/изменяет резерв."""
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE reservations SET status=%s WHERE id=%s", (status, reservation_id))
        connection.commit()
        log_audit(user_id, f"Обновлен резерв ID={reservation_id}", status)
        return True
    except Exception as e:
        print(f"Ошибка при обновлении резерва: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_reservations_by_material(material_id: int) -> List[Dict]:
    """Получает резервирования по материалу."""
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM reservations WHERE material_id = %s",
            (material_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении резервирований: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_all_reservations() -> List[Dict]:
    """Возвращает все резервы."""
    connection = get_connection()
    if not connection:
        return []
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.*, po.number as order_number, m.name as material_name
            FROM reservations r
            LEFT JOIN production_orders po ON po.id = r.order_id
            LEFT JOIN materials m ON m.id = r.material_id
            ORDER BY r.created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении резервов: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_available_balance(material_id: int) -> float:
    """
    Получает доступный остаток (физический минус резервы).
    Резервирование под заказы: учитывает зарезервированные количества.
    """
    from models import get_material_balance
    physical = get_material_balance(material_id)
    
    connection = get_connection()
    if not connection:
        return physical
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT COALESCE(SUM(reserved_qty), 0) FROM reservations WHERE material_id = %s AND status='ACTIVE'",
            (material_id,)
        )
        reserved = float(cursor.fetchone()[0] or 0)
        return max(0, physical - reserved)
    except Exception as e:
        print(f"Ошибка при расчете доступного остатка: {e}")
        return physical
    finally:
        cursor.close()
        connection.close()


# ==================== ЗАЯВКИ НА ПОПОЛНЕНИЕ ====================

def check_and_create_replenishment_request(material_id: int, user_id: Optional[int] = None):
    """
    Проверяет остаток материала и создает заявку на пополнение, если нужно.
    Автоматические заявки при минимальном уровне запаса.
    """
    connection = get_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Получаем материал с min_stock/minstock
        cursor.execute("SELECT min_stock, minstock FROM materials WHERE id = %s", (material_id,))
        material = cursor.fetchone()
        if not material:
            return
        
        min_value = material.get('minstock') or material.get('min_stock')
        if min_value is None:
            return
        min_stock = float(min_value)
        from models import get_material_balance
        balance = get_material_balance(material_id)
        
        # Проверяем, нужна ли заявка
        if balance <= min_stock:
            # Проверяем, нет ли уже открытой заявки
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM replenishment_requests 
                WHERE material_id = %s AND status IN ('NEW', 'SENT')
            """, (material_id,))
            existing = cursor.fetchone()
            
            if existing['count'] == 0:
                # Создаем заявку
                requested_qty = min_stock * 2  # Запрашиваем двойной минимум
                cursor.execute("""
                    INSERT INTO replenishment_requests (material_id, requested_qty, status, created_at)
                    VALUES (%s, %s, 'NEW', %s)
                """, (material_id, requested_qty, datetime.now()))
                connection.commit()
                log_audit(user_id, f"Автоматически создана заявка на пополнение материала ID={material_id}")
                print(f"Создана заявка на пополнение для материала ID={material_id}")
    except Exception as e:
        print(f"Ошибка при проверке заявок: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def get_all_replenishment_requests() -> List[Dict]:
    """Получает все заявки на пополнение."""
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.*, m.name as material_name, m.unit
            FROM replenishment_requests r
            JOIN materials m ON m.id = r.material_id
            ORDER BY r.created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении заявок: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def update_replenishment_request_status(request_id: int, status: str, user_id: Optional[int] = None) -> bool:
    """Обновляет статус заявки на пополнение."""
    connection = get_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE replenishment_requests SET status = %s WHERE id = %s",
            (status, request_id)
        )
        connection.commit()
        log_audit(user_id, f"Изменен статус заявки ID={request_id} на {status}")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении статуса: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


# ==================== КОНТРОЛЬ КАЧЕСТВА ====================

def update_batch_quality(batch_id: int, quality_status: str, user_id: Optional[int] = None) -> bool:
    """Обновляет статус качества партии."""
    connection = get_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE batches SET quality_status = %s WHERE id = %s",
            (quality_status, batch_id)
        )
        connection.commit()
        log_audit(user_id, f"Изменен статус качества партии ID={batch_id} на {quality_status}")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении качества: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_batches_for_material_with_quality(material_id: int, method: str = 'FIFO') -> List[Dict]:
    """
    Получает партии материала с учетом качества.
    Исключает заблокированные партии (BLOCKED).
    Контроль качества материалов: не использует партии со статусом BLOCKED.
    """
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        if method.upper() == 'FIFO':
            order_by = "ORDER BY b.received_at ASC, b.id ASC"
        else:
            order_by = "ORDER BY b.received_at DESC, b.id DESC"
        
        query = f"""
            SELECT 
                b.id,
                b.material_id,
                b.quantity as batch_quantity,
                b.price,
                b.received_at,
                b.location_id,
                b.quality_status,
                b.serial_number,
                COALESCE(SUM(CASE WHEN m.movement_type = 'OUT' THEN m.quantity ELSE 0 END), 0) as used_quantity,
                (b.quantity - COALESCE(SUM(CASE WHEN m.movement_type = 'OUT' THEN m.quantity ELSE 0 END), 0)) as remaining
            FROM batches b
            LEFT JOIN movements m ON m.batch_id = b.id AND m.movement_type = 'OUT'
            WHERE b.material_id = %s AND (b.quality_status = 'OK' OR b.quality_status IS NULL)
            GROUP BY b.id, b.material_id, b.quantity, b.price, b.received_at, b.location_id, b.quality_status, b.serial_number
            HAVING remaining > 0
            {order_by}
        """
        
        cursor.execute(query, (material_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении партий с учетом качества: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_all_batches_with_material() -> List[Dict]:
    """Возвращает все партии с названием материала и адресом."""
    connection = get_connection()
    if not connection:
        return []
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT b.*, m.name as material_name, l.code as location_code
            FROM batches b
            LEFT JOIN materials m ON m.id = b.material_id
            LEFT JOIN locations l ON l.id = b.location_id
            ORDER BY b.received_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении партий: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


# ==================== ПЕРЕМЕЩЕНИЕ МЕЖДУ ЛОКАЦИЯМИ ====================

def transfer_batch(batch_id: int, to_location_id: int, quantity: float, user_id: Optional[int] = None) -> bool:
    """
    Перемещает партию на другую локацию с записью движения TRANSFER.
    Обновляет location_id у партии.
    """
    if quantity <= 0:
        print("Количество для перемещения должно быть больше 0")
        return False

    connection = get_connection()
    if not connection:
        return False

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT material_id, location_id, quantity FROM batches WHERE id=%s", (batch_id,))
        batch = cursor.fetchone()
        if not batch:
            print("Партия не найдена")
            return False

        created_at = datetime.now()
        cursor.execute(
            "INSERT INTO movements (material_id, movement_type, batch_id, quantity, created_at) VALUES (%s,'TRANSFER',%s,%s,%s)",
            (batch['material_id'], batch_id, quantity, created_at)
        )
        cursor.execute("UPDATE batches SET location_id=%s WHERE id=%s", (to_location_id, batch_id))
        connection.commit()
        log_audit(user_id, f"Перемещение партии ID={batch_id}", f"to_location={to_location_id}, qty={quantity}")
        return True
    except Exception as e:
        print(f"Ошибка при перемещении: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

