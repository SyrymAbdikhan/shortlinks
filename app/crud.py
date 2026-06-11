import random
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Link


def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


async def create_link(db: AsyncSession, url: str) -> Link:
    for _ in range(10):
        code = _generate_code()
        result = await db.execute(select(Link).where(Link.code == code))
        if not result.scalar_one_or_none():
            break
    link = Link(code=code, url=url)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def get_link(db: AsyncSession, code: str) -> Link | None:
    result = await db.execute(select(Link).where(Link.code == code))
    return result.scalar_one_or_none()


async def list_links(db: AsyncSession) -> list[Link]:
    result = await db.execute(select(Link).order_by(Link.created_at.desc()))
    return list(result.scalars().all())


async def delete_link(db: AsyncSession, code: str) -> bool:
    result = await db.execute(select(Link).where(Link.code == code))
    link = result.scalar_one_or_none()
    if not link:
        return False
    await db.delete(link)
    await db.commit()
    return True
