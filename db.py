"""
Модуль для подключения к базе данных MySQL и создания таблиц.
Содержит функции для инициализации структуры БД.
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Параметры подключения к базе данных
# ВАЖНО: Перед запуском создайте базу данных 'textile_warehouse' в MySQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'textile_warehouse',
    'user': 'root',
    'password': 'root'  
}


def get_connection():
    """
    Создает и возвращает подключение к базе данных MySQL.
    
    Returns:
        mysql.connector.connection.MySQLConnection: Объект подключения или None при ошибке
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None


def migrate_tables():
    """
    Мигрирует существующие таблицы, добавляя новые поля если их нет.
    Используется для обновления структуры БД без потери данных.
    """
    # Подстраховка: создаем недостающие таблицы, если база была старой
    try:
        create_tables()
    except Exception:
        pass

    connection = get_connection()
    if not connection:
        print("Не удалось подключиться к базе данных для миграции!")
        return False
    
    cursor = connection.cursor()
    
    try:
        # Проверяем, существует ли таблица materials
        # Если таблиц нет, значит они будут созданы через create_tables()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'materials'
        """)
        if cursor.fetchone()[0] == 0:
            print("Таблица materials не существует. Пропускаем миграцию - таблицы будут созданы через create_tables()")
            connection.commit()
            return True  # Не ошибка, просто таблиц еще нет
        
        # Проверяем и добавляем поле category, если его нет
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'materials' 
            AND COLUMN_NAME = 'category'
        """)
        if cursor.fetchone()[0] == 0:
            print("Добавление поля category...")
            cursor.execute("ALTER TABLE materials ADD COLUMN category VARCHAR(20) DEFAULT 'other'")
            # Проверяем, существует ли индекс перед созданием
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.STATISTICS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'materials' 
                AND INDEX_NAME = 'idx_category'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE materials ADD INDEX idx_category (category)")
            # Устанавливаем значение по умолчанию для существующих записей
            cursor.execute("UPDATE materials SET category = 'other' WHERE category IS NULL")
            print("✓ Поле category успешно добавлено в таблицу materials")
        
        # Проверяем и добавляем поле created_at, если его нет
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'materials' 
            AND COLUMN_NAME = 'created_at'
        """)
        if cursor.fetchone()[0] == 0:
            print("Добавление поля created_at...")
            cursor.execute("ALTER TABLE materials ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            cursor.execute("ALTER TABLE materials ADD INDEX idx_created (created_at)")
            cursor.execute("UPDATE materials SET created_at = NOW() WHERE created_at IS NULL")
            print("✓ Поле created_at успешно добавлено в таблицу materials")
        
        # Добавляем поля min_stock и max_stock (старое имя) и дублирующие minstock/maxstock (требование ТЗ)
        for field in ['min_stock', 'max_stock', 'minstock', 'maxstock']:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'materials' 
                AND COLUMN_NAME = '{field}'
            """)
            if cursor.fetchone()[0] == 0:
                default_clause = "DEFAULT 0" if field in ('min_stock', 'minstock') else "NULL"
                cursor.execute(f"ALTER TABLE materials ADD COLUMN {field} DECIMAL(10,3) {default_clause}")
                print(f"✓ Поле {field} успешно добавлено в таблицу materials")
        
        # Добавляем новые поля в batches
        batch_fields = [
            ('location_id', 'INT NULL', 'FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL'),
            ('supplier_id', 'INT NULL', 'FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL'),
            ('contract_id', 'INT NULL', 'FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE SET NULL'),
            ('quality_status', "ENUM('OK', 'BLOCKED') DEFAULT 'OK'", None),
            ('serial_number', 'VARCHAR(50) NULL', None)
        ]
        
        for field, field_type, fk_constraint in batch_fields:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'batches' 
                AND COLUMN_NAME = '{field}'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE batches ADD COLUMN {field} {field_type}")
                if fk_constraint:
                    try:
                        cursor.execute(f"ALTER TABLE batches ADD {fk_constraint}")
                    except:
                        pass  # FK может не добавиться если таблицы еще нет
                print(f"✓ Поле {field} успешно добавлено в таблицу batches")
        
        # Добавляем поле order_id в movements
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'movements' 
            AND COLUMN_NAME = 'order_id'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE movements MODIFY movement_type ENUM('IN', 'OUT', 'TRANSFER') NOT NULL")
            cursor.execute("ALTER TABLE movements ADD COLUMN order_id INT NULL")
            try:
                cursor.execute("ALTER TABLE movements ADD FOREIGN KEY (order_id) REFERENCES production_orders(id) ON DELETE SET NULL")
            except:
                pass
            print("✓ Поле order_id успешно добавлено в таблицу movements")

        # Добавляем недостающие поля по новым требованиям
        # locations: name
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'locations' AND COLUMN_NAME = 'name'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE locations ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT 'Склад'")
            print("✓ Добавлено поле name в locations")

        # suppliers: contact
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'suppliers' AND COLUMN_NAME = 'contact'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE suppliers ADD COLUMN contact VARCHAR(255) NULL")
            print("✓ Добавлено поле contact в suppliers")

        # contracts: contract_date, description (оставляем старый signed_at)
        for field_name, field_def in [
            ('contract_date', 'DATE NULL'),
            ('description', 'VARCHAR(255) NULL')
        ]:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'contracts' AND COLUMN_NAME = %s
            """, (field_name,))
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE contracts ADD COLUMN {field_name} {field_def}")
                print(f"✓ Добавлено поле {field_name} в contracts")

        # production_orders: number, order_date, status
        prod_fields = [
            ('number', "VARCHAR(50) NOT NULL", "UNIQUE"),
            ('order_date', "DATE NULL", None),
            ('status', "ENUM('NEW','IN_PROGRESS','DONE','CANCELLED') DEFAULT 'NEW'", None)
        ]
        for field_name, field_def, extra in prod_fields:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'production_orders' AND COLUMN_NAME = %s
            """, (field_name,))
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE production_orders ADD COLUMN {field_name} {field_def}")
                if extra == "UNIQUE":
                    cursor.execute(f"ALTER TABLE production_orders ADD UNIQUE INDEX idx_{field_name} ({field_name})")
                print(f"✓ Добавлено поле {field_name} в production_orders")

        # reservations: status, quantity
        for field_name, field_def in [
            ('status', "ENUM('ACTIVE','RELEASED','CANCELLED') DEFAULT 'ACTIVE'"),
            ('quantity', "DECIMAL(10,3) NULL")
        ]:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'reservations' AND COLUMN_NAME = %s
            """, (field_name,))
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE reservations ADD COLUMN {field_name} {field_def}")
                print(f"✓ Добавлено поле {field_name} в reservations")

        # audit_log: details
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'audit_log' AND COLUMN_NAME = 'details'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE audit_log ADD COLUMN details TEXT NULL")
            print("✓ Добавлено поле details в audit_log")
        
        connection.commit()
        print("Миграция базы данных завершена успешно!")
        return True
    except Error as e:
        print(f"Ошибка при миграции таблиц: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def create_tables():
    """
    Создает все необходимые таблицы в базе данных, если они не существуют.
    Выполняет SQL-скрипты для создания структуры БД.
    """
    connection = get_connection()
    if not connection:
        print("Не удалось подключиться к базе данных!")
        return False
    
    cursor = connection.cursor()
    
    try:
        # ВАЖНО: Создаем таблицы в правильном порядке для FK-ограничений
        # Сначала независимые таблицы, затем зависимые
        
        # Создание таблицы materials (материалы)
        # Добавлены поля: category, created_at, min_stock, max_stock (минимальный/максимальный уровень запаса)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                unit VARCHAR(20) NOT NULL,
                category VARCHAR(20) DEFAULT 'other',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                min_stock DECIMAL(10,3) DEFAULT 0,
                max_stock DECIMAL(10,3) NULL,
                minstock DECIMAL(10,3) DEFAULT 0,
                maxstock DECIMAL(10,3) NULL,
                UNIQUE KEY unique_name (name),
                INDEX idx_category (category),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Создание таблицы users (пользователи системы)
        # Роли: storekeeper (кладовщик), supply (снабженец), accountant (бухгалтер), admin (администратор)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                role ENUM('storekeeper', 'supply', 'accountant', 'admin') NOT NULL DEFAULT 'storekeeper',
                INDEX idx_username (username),
                INDEX idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Создание таблицы locations (адреса хранения)
        # Адресное хранение: код вида "A-01-03" (ряд-стеллаж-ячейка)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(255) NULL,
                INDEX idx_code (code),
                INDEX idx_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Создание таблицы suppliers (поставщики)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                inn VARCHAR(20) NULL,
                contact VARCHAR(255) NULL,
                INDEX idx_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Создание таблицы contracts (договоры с поставщиками)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                supplier_id INT NOT NULL,
                number VARCHAR(50) NOT NULL,
                contract_date DATE NULL,
                description VARCHAR(255) NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE,
                INDEX idx_supplier (supplier_id),
                INDEX idx_number (number)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Создание таблицы batches (партии материалов)
        # Добавлены поля: location_id (адрес хранения), supplier_id, contract_id (поставщик и договор),
        # quality_status (статус качества), serial_number (серийный номер)
        # ВАЖНО: Создаем таблицу сначала без FK, затем добавляем FK отдельно для избежания ошибок
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batches (
                id INT AUTO_INCREMENT PRIMARY KEY,
                material_id INT NOT NULL,
                quantity DECIMAL(10,3) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                received_at DATETIME NOT NULL,
                location_id INT NULL,
                supplier_id INT NULL,
                contract_id INT NULL,
                quality_status ENUM('OK', 'BLOCKED') DEFAULT 'OK',
                serial_number VARCHAR(50) NULL,
                INDEX idx_material (material_id),
                INDEX idx_received (received_at),
                INDEX idx_location (location_id),
                INDEX idx_quality (quality_status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Добавляем FK-ограничения отдельно (если их еще нет)
        # Это позволяет избежать ошибок при создании таблиц в неправильном порядке
        try:
            # Проверяем существование FK перед добавлением
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'batches' 
                AND CONSTRAINT_NAME = 'batches_ibfk_1'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE batches ADD CONSTRAINT batches_ibfk_1 FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE")
        except:
            pass  # FK уже существует или не может быть создан
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'batches' 
                AND CONSTRAINT_NAME = 'batches_ibfk_2'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE batches ADD CONSTRAINT batches_ibfk_2 FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL")
        except:
            pass
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'batches' 
                AND CONSTRAINT_NAME = 'batches_ibfk_3'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE batches ADD CONSTRAINT batches_ibfk_3 FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL")
        except:
            pass
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'batches' 
                AND CONSTRAINT_NAME = 'batches_ibfk_4'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE batches ADD CONSTRAINT batches_ibfk_4 FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE SET NULL")
        except:
            pass
        
        # Создание таблицы production_orders (заказы производства)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                number VARCHAR(50) NOT NULL UNIQUE,
                order_date DATE NULL,
                status ENUM('NEW','IN_PROGRESS','DONE','CANCELLED') DEFAULT 'NEW',
                description VARCHAR(255) NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_number (number),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Создание таблицы reservations (резервирование материалов под заказы)
        # Создаем без FK сначала
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                material_id INT NOT NULL,
                reserved_qty DECIMAL(10,3) NOT NULL,
                quantity DECIMAL(10,3) NULL,
                status ENUM('ACTIVE','RELEASED','CANCELLED') DEFAULT 'ACTIVE',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_order (order_id),
                INDEX idx_material (material_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Добавляем FK для reservations отдельно
        for fk_name, fk_def in [
            ('reservations_ibfk_1', 'FOREIGN KEY (order_id) REFERENCES production_orders(id) ON DELETE CASCADE'),
            ('reservations_ibfk_2', 'FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE')
        ]:
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'reservations' 
                    AND CONSTRAINT_NAME = '{fk_name}'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"ALTER TABLE reservations ADD CONSTRAINT {fk_name} {fk_def}")
            except:
                pass
        
        # Создание таблицы replenishment_requests (заявки на пополнение)
        # Автоматические заявки при минимальном уровне запаса
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS replenishment_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                material_id INT NOT NULL,
                requested_qty DECIMAL(10,3) NOT NULL,
                status ENUM('NEW', 'SENT', 'APPROVED', 'REJECTED') DEFAULT 'NEW',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_material (material_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Добавляем FK для replenishment_requests отдельно
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'replenishment_requests' 
                AND CONSTRAINT_NAME = 'replenishment_requests_ibfk_1'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE replenishment_requests ADD CONSTRAINT replenishment_requests_ibfk_1 FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE")
        except:
            pass
        
        # Создание таблицы movements (операции прихода/списания)
        # Добавлено поле order_id для связи со списанием под заказ производства
        # Создаем без FK сначала, затем добавляем FK отдельно
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                material_id INT NOT NULL,
                movement_type ENUM('IN', 'OUT', 'TRANSFER') NOT NULL,
                batch_id INT NULL,
                quantity DECIMAL(10,3) NOT NULL,
                created_at DATETIME NOT NULL,
                order_id INT NULL,
                INDEX idx_material (material_id),
                INDEX idx_type (movement_type),
                INDEX idx_created (created_at),
                INDEX idx_order (order_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Добавляем FK для movements отдельно
        for fk_name, fk_def in [
            ('movements_ibfk_1', 'FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE'),
            ('movements_ibfk_2', 'FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL'),
            ('movements_ibfk_3', 'FOREIGN KEY (order_id) REFERENCES production_orders(id) ON DELETE SET NULL')
        ]:
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'movements' 
                    AND CONSTRAINT_NAME = '{fk_name}'
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"ALTER TABLE movements ADD CONSTRAINT {fk_name} {fk_def}")
            except:
                pass
        
        # Создание таблицы audit_log (журнал операций)
        # Журнал операций для аудита всех действий пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                action VARCHAR(255) NOT NULL,
                details TEXT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user_id),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Добавляем FK для audit_log отдельно
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'audit_log' 
                AND CONSTRAINT_NAME = 'audit_log_ibfk_1'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE audit_log ADD CONSTRAINT audit_log_ibfk_1 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL")
        except:
            pass
        
        connection.commit()
        print("✓ Все таблицы успешно созданы!")
        
        # Проверяем, что все таблицы созданы
        required_tables = [
            'materials', 'users', 'locations', 'suppliers', 'contracts',
            'batches', 'production_orders', 'reservations', 
            'replenishment_requests', 'movements', 'audit_log'
        ]
        
        for table in required_tables:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = '{table}'
            """)
            if cursor.fetchone()[0] == 0:
                print(f"⚠ Предупреждение: таблица {table} не создана!")
            else:
                print(f"✓ Таблица {table} существует")
        
        return True
        
    except Error as e:
        print(f"Ошибка при создании таблиц: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()


def seed_data():
    """
    Заполняет базу данных тестовыми данными.
    Создает материалы, партии и операции для демонстрации работы системы.
    """
    connection = get_connection()
    if not connection:
        print("Не удалось подключиться к базе данных!")
        return False
    
    cursor = connection.cursor()
    
    try:
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM materials")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("База данных уже содержит данные. Пропускаем заполнение тестовыми данными.")
            return True
        
        print("Заполнение базы данных тестовыми данными...")
        
        # Добавляем материалы с категориями, датами создания и минимальными остатками
        from datetime import datetime, timedelta
        
        materials_data = [
            ('Хлопок', 'кг', 'fabric', datetime.now() - timedelta(days=60), 50.0, 200.0),
            ('Лен', 'м', 'fabric', datetime.now() - timedelta(days=55), 100.0, 500.0),
            ('Фурнитура', 'шт', 'accessory', datetime.now() - timedelta(days=50), 200.0, 1000.0),
            ('Подкладка', 'м', 'fabric', datetime.now() - timedelta(days=45), 50.0, 300.0),
        ]
        
        material_ids = {}
        for name, unit, category, created_at, min_stock, max_stock in materials_data:
            cursor.execute(
                "INSERT INTO materials (name, unit, category, created_at, min_stock, max_stock, minstock, maxstock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (name, unit, category, created_at, min_stock, max_stock, min_stock, max_stock)
            )
            material_ids[name] = cursor.lastrowid
        
        # Добавляем пользователей (пользователи, роли и журнал операций)
        users_data = [
            ('admin', 'admin'),
            ('storekeeper', 'storekeeper'),
            ('supply', 'supply'),
            ('accountant', 'accountant'),
        ]
        for username, role in users_data:
            try:
                cursor.execute("INSERT INTO users (username, role) VALUES (%s, %s)", (username, role))
            except:
                pass  # Пользователь уже существует
        
        # Добавляем адреса хранения (адресное хранение)
        locations_data = [
            ('A-01-01', 'Ячейка A-01-01', 'Ряд A, стеллаж 01, ячейка 01'),
            ('A-01-02', 'Ячейка A-01-02', 'Ряд A, стеллаж 01, ячейка 02'),
            ('B-02-01', 'Ячейка B-02-01', 'Ряд B, стеллаж 02, ячейка 01'),
            ('B-02-02', 'Ячейка B-02-02', 'Ряд B, стеллаж 02, ячейка 02'),
        ]
        location_ids = {}
        for code, name, description in locations_data:
            try:
                cursor.execute("INSERT INTO locations (code, name, description) VALUES (%s, %s, %s)", (code, name, description))
                location_ids[code] = cursor.lastrowid
            except:
                pass
        
        # Добавляем поставщиков (управление поставщиками и договорами)
        suppliers_data = [
            ('ООО "Текстиль-Снаб"', '1234567890', 'supply@example.com'),
            ('ИП Иванов', '0987654321', 'ivanov@example.com'),
        ]
        supplier_ids = {}
        for name, inn, contact in suppliers_data:
            try:
                cursor.execute("INSERT INTO suppliers (name, inn, contact) VALUES (%s, %s, %s)", (name, inn, contact))
                supplier_ids[name] = cursor.lastrowid
            except:
                pass
        
        # Добавляем договоры
        if supplier_ids:
            first_supplier_id = list(supplier_ids.values())[0]
            try:
                cursor.execute(
                    "INSERT INTO contracts (supplier_id, number, contract_date, description) VALUES (%s, %s, %s, %s)",
                    (first_supplier_id, 'ДГ-2024-001', (datetime.now() - timedelta(days=90)).date(), 'Базовый договор поставки')
                )
            except:
                pass
        
        # Добавляем партии материалов с разными датами для тестирования FIFO/LIFO
        # Важно: дата партии (received_at) используется для сортировки в FIFO/LIFO
        batches_data = [
            # Хлопок - несколько партий с разными датами
            ('Хлопок', 100.0, 150.0, datetime.now() - timedelta(days=30)),
            ('Хлопок', 50.0, 160.0, datetime.now() - timedelta(days=15)),
            ('Хлопок', 75.0, 155.0, datetime.now() - timedelta(days=5)),
            
            # Лен - несколько партий
            ('Лен', 200.0, 80.0, datetime.now() - timedelta(days=25)),
            ('Лен', 150.0, 85.0, datetime.now() - timedelta(days=10)),
            
            # Фурнитура
            ('Фурнитура', 500.0, 5.0, datetime.now() - timedelta(days=20)),
            ('Фурнитура', 300.0, 5.5, datetime.now() - timedelta(days=7)),
            
            # Подкладка
            ('Подкладка', 100.0, 120.0, datetime.now() - timedelta(days=18)),
        ]
        
        batch_ids = []
        # Используем первый адрес и поставщика для тестовых партий
        first_location_id = list(location_ids.values())[0] if location_ids else None
        first_supplier_id = list(supplier_ids.values())[0] if supplier_ids else None
        first_contract_id = None
        if first_supplier_id:
            cursor.execute("SELECT id FROM contracts WHERE supplier_id = %s LIMIT 1", (first_supplier_id,))
            contract = cursor.fetchone()
            if contract:
                first_contract_id = contract[0]
        
        for i, (material_name, quantity, price, received_at) in enumerate(batches_data):
            material_id = material_ids[material_name]
            # Чередуем адреса для демонстрации
            location_id = list(location_ids.values())[i % len(location_ids)] if location_ids else None
            
            cursor.execute(
                """INSERT INTO batches (material_id, quantity, price, received_at, location_id, supplier_id, contract_id, quality_status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 'OK')""",
                (material_id, quantity, price, received_at, location_id, first_supplier_id, first_contract_id)
            )
            batch_id = cursor.lastrowid
            batch_ids.append((batch_id, material_id, quantity, received_at))
            
            # Создаем запись о приходе
            cursor.execute(
                """INSERT INTO movements (material_id, movement_type, batch_id, quantity, created_at) 
                   VALUES (%s, 'IN', %s, %s, %s)""",
                (material_id, batch_id, quantity, received_at)
            )
        
        # Добавляем несколько операций списания для демонстрации
        # Списание хлопка (частично из первой партии)
        if len(batch_ids) > 0:
            batch_id, material_id, quantity, received_at = batch_ids[0]
            issue_quantity = 30.0
            issue_date = datetime.now() - timedelta(days=10)
            cursor.execute(
                """INSERT INTO movements (material_id, movement_type, batch_id, quantity, created_at) 
                   VALUES (%s, 'OUT', %s, %s, %s)""",
                (material_id, batch_id, issue_quantity, issue_date)
            )
        
        connection.commit()
        print("Тестовые данные успешно добавлены!")
        return True
        
    except Error as e:
        print(f"Ошибка при заполнении тестовыми данными: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()


def init_db():
    """
    Инициализирует базу данных: создает таблицы, мигрирует существующие и заполняет тестовыми данными.
    """
    if not create_tables():
        return False
    
    # Мигрируем существующие таблицы (добавляем новые поля если нужно)
    migrate_tables()
    
    seed_data()
    print("База данных успешно инициализирована!")
    return True


if __name__ == "__main__":
    # Тестирование подключения и инициализации БД
    print("Инициализация базы данных...")
    print("=" * 50)
    init_db()
    print("=" * 50)
    print("\nДля обновления существующей БД запустите:")
    print("  python -c 'from db import migrate_tables; migrate_tables()'")

