"""
Модуль для работы с данными в базе данных.
Содержит функции для добавления материалов, регистрации прихода/списания,
получения остатков и другой бизнес-логики.
"""

from db import get_connection
from datetime import datetime
from typing import List, Dict, Optional, Tuple


def add_material(name: str, unit: str, category: str = 'other',
                 min_stock: float = 0.0, max_stock: Optional[float] = None) -> Optional[int]:
    """
    Добавляет новый материал в базу данных.
    
    Args:
        name: Название материала
        unit: Единица измерения (м, кг, шт и т.д.)
        category: Категория материала ('fabric', 'accessory', 'thread', 'other')
    
    Returns:
        ID созданного материала или None при ошибке
    """
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    
    try:
        # created_at устанавливается автоматически через DEFAULT CURRENT_TIMESTAMP
        cursor.execute(
            "INSERT INTO materials (name, unit, category, created_at, min_stock, max_stock, minstock, maxstock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (name, unit, category, datetime.now(), min_stock, max_stock, min_stock, max_stock)
        )
        connection.commit()
        material_id = cursor.lastrowid
        print(f"Материал '{name}' успешно добавлен с ID={material_id}")
        return material_id
    except Exception as e:
        print(f"Ошибка при добавлении материала: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def get_all_materials() -> List[Dict]:
    """
    Получает список всех материалов из базы данных.
    
    Returns:
        Список словарей с данными материалов: [{'id': 1, 'name': 'Ткань', 'unit': 'м', 'category': 'fabric', 'created_at': ...}, ...]
    """
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, name, unit, category, created_at, min_stock, max_stock, minstock, maxstock FROM materials ORDER BY name")
        materials = cursor.fetchall()
        return materials
    except Exception as e:
        print(f"Ошибка при получении материалов: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_material_by_name(name: str) -> Optional[Dict]:
    """Возвращает материал по точному имени."""
    connection = get_connection()
    if not connection:
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM materials WHERE name = %s LIMIT 1", (name,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении материала по имени: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def update_material(material_id: int, name: str, unit: str, category: str,
                    min_stock: float = 0.0, max_stock: Optional[float] = None) -> bool:
    """
    Обновляет данные материала в базе данных.
    
    Args:
        material_id: ID материала для обновления
        name: Новое название материала
        unit: Новая единица измерения
        category: Категория материала ('fabric', 'accessory', 'thread', 'other')
    
    Returns:
        True если обновление успешно, False при ошибке
    """
    connection = get_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "UPDATE materials SET name = %s, unit = %s, category = %s, min_stock=%s, max_stock=%s, minstock=%s, maxstock=%s WHERE id = %s",
            (name, unit, category, min_stock, max_stock, min_stock, max_stock, material_id)
        )
        connection.commit()
        print(f"Материал ID={material_id} успешно обновлен")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении материала: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def delete_material(material_id: int) -> bool:
    """
    Удаляет материал из базы данных.
    Внимание: из-за CASCADE также удалятся связанные партии и операции.
    
    Args:
        material_id: ID материала для удаления
    
    Returns:
        True если удаление успешно, False при ошибке
    """
    connection = get_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("DELETE FROM materials WHERE id = %s", (material_id,))
        connection.commit()
        print(f"Материал ID={material_id} успешно удален")
        return True
    except Exception as e:
        print(f"Ошибка при удалении материала: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def register_receipt(material_id: int, quantity: float, price: float, 
                     location_id: Optional[int] = None, supplier_id: Optional[int] = None,
                     contract_id: Optional[int] = None, serial_number: Optional[str] = None,
                     user_id: Optional[int] = None) -> Optional[int]:
    """
    Регистрирует приход материала: создает партию и запись в movements.
    Поддерживает адресное хранение, поставщиков и контроль качества.
    
    Args:
        material_id: ID материала
        quantity: Количество
        price: Цена за единицу
        location_id: ID адреса хранения (опционально)
        supplier_id: ID поставщика (опционально)
        contract_id: ID договора (опционально)
        serial_number: Серийный номер партии (опционально)
        user_id: ID пользователя для аудита
    
    Returns:
        ID созданной партии или None при ошибке
    """
    if quantity <= 0:
        print("Ошибка: количество должно быть больше нуля!")
        return None
    
    if price < 0:
        print("Ошибка: цена не может быть отрицательной!")
        return None
    
    connection = get_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    
    try:
        # Проверяем, существует ли материал
        cursor.execute("SELECT id FROM materials WHERE id = %s", (material_id,))
        if not cursor.fetchone():
            print(f"Ошибка: материал с ID={material_id} не найден!")
            return None
        
        # Создаем партию с адресом, поставщиком и качеством
        received_at = datetime.now()
        cursor.execute(
            """INSERT INTO batches (material_id, quantity, price, received_at, 
               location_id, supplier_id, contract_id, quality_status, serial_number) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'OK', %s)""",
            (material_id, quantity, price, received_at, location_id, supplier_id, contract_id, serial_number)
        )
        batch_id = cursor.lastrowid
        
        # Создаем запись о приходе в movements
        cursor.execute(
            """INSERT INTO movements (material_id, movement_type, batch_id, quantity, created_at) 
               VALUES (%s, 'IN', %s, %s, %s)""",
            (material_id, batch_id, quantity, received_at)
        )
        
        connection.commit()
        
        # Логируем операцию
        from models_extended import log_audit
        log_audit(user_id, f"Приход материала ID={material_id}", f"qty={quantity}, batch={batch_id}")
        
        print(f"Приход зарегистрирован: партия ID={batch_id}, количество={quantity}")
        return batch_id
        
    except Exception as e:
        print(f"Ошибка при регистрации прихода: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def get_batches_for_material(material_id: int, method: str = 'FIFO') -> List[Dict]:
    """
    Получает список партий для материала с учетом остатков, отсортированных по методу FIFO/LIFO.
    
    Логика сортировки:
    - FIFO (First In, First Out): сортировка по дате прихода партии (received_at) по возрастанию,
      затем по ID партии по возрастанию (для стабильности при одинаковых датах)
    - LIFO (Last In, First Out): сортировка по дате прихода партии (received_at) по убыванию,
      затем по ID партии по убыванию (для стабильности при одинаковых датах)
    
    Основной критерий - дата партии (received_at), которая устанавливается при регистрации прихода.
    
    Args:
        material_id: ID материала
        method: Метод сортировки - 'FIFO' (старые первые) или 'LIFO' (новые первые)
    
    Returns:
        Список партий с остатками: [{'id': 1, 'quantity': 10.5, 'price': 100.0, ...}, ...]
    """
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Улучшенная сортировка для FIFO/LIFO
        # Основной критерий - дата прихода партии (received_at)
        # Дополнительный критерий - ID партии для стабильности при одинаковых датах
        if method.upper() == 'FIFO':
            # FIFO: старые партии первыми (по дате прихода, затем по ID)
            order_by = "ORDER BY b.received_at ASC, b.id ASC"
        else:  # LIFO
            # LIFO: новые партии первыми (по дате прихода, затем по ID)
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
            WHERE b.material_id = %s
            GROUP BY b.id, b.material_id, b.quantity, b.price, b.received_at, b.location_id, b.quality_status, b.serial_number
            HAVING remaining > 0
            {order_by}
        """
        
        cursor.execute(query, (material_id,))
        batches = cursor.fetchall()
        return batches
        
    except Exception as e:
        print(f"Ошибка при получении партий: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def register_issue(material_id: int, quantity: float, method: str = 'FIFO', order_id: Optional[int] = None, user_id: Optional[int] = None) -> bool:
    """
    Регистрирует списание материала по методу FIFO или LIFO.
    Автоматически выбирает партии и уменьшает их остатки.
    Учитывает качество партий (не использует BLOCKED) и резервирование.
    
    Args:
        material_id: ID материала
        quantity: Количество для списания
        method: Метод списания - 'FIFO' или 'LIFO'
        order_id: ID заказа производства (опционально)
        user_id: ID пользователя для аудита
    
    Returns:
        True если списание успешно, False при ошибке
    """
    if quantity <= 0:
        print("Ошибка: количество должно быть больше нуля!")
        return False
    
    # Импортируем функции для работы с качеством и резервированием
    from models_extended import get_batches_for_material_with_quality, get_available_balance, check_and_create_replenishment_request, log_audit
    
    # Получаем доступные партии (только с качеством OK)
    batches = get_batches_for_material_with_quality(material_id, method)
    
    if not batches:
        print(f"Ошибка: нет доступных партий для материала ID={material_id}")
        return False
    
    # Проверяем доступный остаток (с учетом резервирования)
    available_balance = get_available_balance(material_id)
    if available_balance < quantity:
        total_remaining = sum(float(b['remaining']) for b in batches)
        print(f"Ошибка: недостаточно материала! Доступно: {available_balance}, требуется: {quantity}")
        if total_remaining >= quantity:
            print("Внимание: часть материала зарезервирована под заказы!")
        return False
    
    connection = get_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    created_at = datetime.now()
    remaining_to_issue = quantity
    
    try:
        # Списываем из партий по порядку
        for batch in batches:
            if remaining_to_issue <= 0:
                break
            
            batch_id = batch['id']
            available = float(batch['remaining'])
            to_issue = min(available, remaining_to_issue)
            
            # Создаем запись о списании
            cursor.execute(
                """INSERT INTO movements (material_id, movement_type, batch_id, quantity, created_at, order_id) 
                   VALUES (%s, 'OUT', %s, %s, %s, %s)""",
                (material_id, batch_id, to_issue, created_at, order_id)
            )
            
            remaining_to_issue -= to_issue
            print(f"Списано {to_issue} из партии ID={batch_id}")
        
        connection.commit()
        print(f"Списание успешно зарегистрировано: {quantity}")
        
        # Логируем операцию
        log_audit(user_id, f"Списание материала ID={material_id}", f"qty={quantity}, method={method}")
        
        # Проверяем и создаем заявку на пополнение, если нужно
        check_and_create_replenishment_request(material_id, user_id)
        
        return True
        
    except Exception as e:
        print(f"Ошибка при регистрации списания: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_stock_balance() -> List[Dict]:
    """
    Получает текущие остатки по всем материалам.
    Считает остаток как сумму всех партий минус все списания.
    
    Returns:
        Список словарей: [{'material_id': 1, 'name': 'Ткань', 'unit': 'м', 'balance': 15.5}, ...]
    """
    connection = get_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
            SELECT 
                m.id as material_id,
                m.name,
                m.unit,
                COALESCE(SUM(
                    b.quantity - COALESCE((
                        SELECT SUM(mv.quantity) 
                        FROM movements mv 
                        WHERE mv.batch_id = b.id AND mv.movement_type = 'OUT'
                    ), 0)
                ), 0) as balance
            FROM materials m
            LEFT JOIN batches b ON b.material_id = m.id
            GROUP BY m.id, m.name, m.unit
            HAVING balance > 0 OR balance IS NULL
            ORDER BY m.name
        """
        
        cursor.execute(query)
        balances = cursor.fetchall()
        
        # Заменяем NULL на 0
        for balance in balances:
            if balance['balance'] is None:
                balance['balance'] = 0.0
            else:
                balance['balance'] = float(balance['balance'])
        
        return balances
        
    except Exception as e:
        print(f"Ошибка при получении остатков: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_material_balance(material_id: int) -> float:
    """
    Получает текущий остаток конкретного материала.
    
    Args:
        material_id: ID материала
    
    Returns:
        Остаток материала (0.0 если материала нет или остаток нулевой)
    """
    connection = get_connection()
    if not connection:
        return 0.0
    
    cursor = connection.cursor()
    
    try:
        query = """
            SELECT COALESCE(SUM(
                b.quantity - COALESCE((
                    SELECT SUM(mv.quantity) 
                    FROM movements mv 
                    WHERE mv.batch_id = b.id AND mv.movement_type = 'OUT'
                ), 0)
            ), 0) as balance
            FROM batches b
            WHERE b.material_id = %s
        """
        
        cursor.execute(query, (material_id,))
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            return float(result[0])
        return 0.0
        
    except Exception as e:
        print(f"Ошибка при получении остатка: {e}")
        return 0.0
    finally:
        cursor.close()
        connection.close()

