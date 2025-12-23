"""
Модуль для реализации логики выбора партий по методам FIFO и LIFO.
FIFO (First In, First Out) - первым пришел, первым ушел (старые партии списываются первыми)
LIFO (Last In, First Out) - последним пришел, первым ушел (новые партии списываются первыми)
"""

from models import get_batches_for_material
from typing import List, Dict, Tuple


def select_batches_for_issue(material_id: int, quantity: float, method: str = 'FIFO') -> List[Dict]:
    """
    Выбирает партии для списания по методу FIFO или LIFO.
    
    Args:
        material_id: ID материала
        quantity: Требуемое количество для списания
        method: Метод выбора - 'FIFO' или 'LIFO'
    
    Returns:
        Список партий с указанием, сколько из каждой нужно списать:
        [{'batch_id': 1, 'quantity_to_issue': 10.5, 'batch': {...}}, ...]
    """
    # Получаем партии, отсортированные по методу
    batches = get_batches_for_material(material_id, method)
    
    if not batches:
        return []
    
    selected = []
    remaining_quantity = quantity
    
    # Проходим по партиям в порядке сортировки и выбираем нужное количество
    for batch in batches:
        if remaining_quantity <= 0:
            break
        
        available = float(batch['remaining'])
        if available > 0:
            quantity_to_take = min(available, remaining_quantity)
            selected.append({
                'batch_id': batch['id'],
                'quantity_to_issue': quantity_to_take,
                'batch': batch
            })
            remaining_quantity -= quantity_to_take
    
    return selected


def calculate_total_available(material_id: int) -> float:
    """
    Рассчитывает общее доступное количество материала во всех партиях.
    
    Args:
        material_id: ID материала
    
    Returns:
        Общее доступное количество
    """
    batches = get_batches_for_material(material_id, 'FIFO')  # Метод не важен для подсчета
    total = sum(float(b['remaining']) for b in batches)
    return total


def can_issue(material_id: int, quantity: float) -> Tuple[bool, float]:
    """
    Проверяет, можно ли списать указанное количество материала.
    
    Args:
        material_id: ID материала
        quantity: Требуемое количество
    
    Returns:
        Кортеж (можно_ли_списать, доступное_количество)
    """
    available = calculate_total_available(material_id)
    can_issue_flag = available >= quantity
    return can_issue_flag, available

