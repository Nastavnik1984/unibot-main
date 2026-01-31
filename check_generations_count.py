"""Скрипт для проверки количества генераций в БД.

Сравнивает фактическое количество в БД с тем, что показывает админка.
"""

import asyncio

from sqlalchemy import func, select

from src.db.base import DatabaseSession
from src.db.models.generation import Generation


async def main() -> None:
    """Проверить количество генераций в БД."""
    async with DatabaseSession() as session:
        # Подсчитываем все генерации
        stmt = select(func.count(Generation.id))
        result = await session.execute(stmt)
        total_count = result.scalar_one()

        print(f"Всего генераций в БД: {total_count}")

        # Проверяем генерации по статусам
        for status in ["pending", "completed", "failed"]:
            stmt = select(func.count(Generation.id)).where(Generation.status == status)
            result = await session.execute(stmt)
            count = result.scalar_one()
            print(f"  - {status}: {count}")

        # Проверяем, есть ли генерации с несуществующими пользователями
        # (это не должно быть из-за CASCADE, но проверим)
        from sqlalchemy import exists
        from src.db.models.user import User

        stmt = select(func.count(Generation.id)).where(
            ~exists().where(User.id == Generation.user_id)
        )
        result = await session.execute(stmt)
        orphaned_count = result.scalar_one()

        if orphaned_count > 0:
            print(f"\n⚠️  ВНИМАНИЕ: Найдено {orphaned_count} генераций с несуществующими пользователями!")
            print("   Это может влиять на подсчет в админке, если SQLAdmin делает INNER JOIN.")
        else:
            print("\n✅ Все генерации имеют существующих пользователей")


if __name__ == "__main__":
    asyncio.run(main())
