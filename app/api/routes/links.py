from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api.deps import get_db
from app.core.security import verify_api_key

router = APIRouter()


@router.post("/links", response_model=schemas.LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: schemas.LinkCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> schemas.LinkResponse:
    return await crud.create_link(db, str(payload.url))


@router.get("/links", response_model=list[schemas.LinkResponse])
async def list_links(db: AsyncSession = Depends(get_db)) -> list[schemas.LinkResponse]:
    return await crud.list_links(db)


@router.delete("/links/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    code: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
) -> None:
    if not await crud.delete_link(db, code):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")


@router.get("/{code}")
async def redirect(code: str, db: AsyncSession = Depends(get_db)) -> RedirectResponse:
    link = await crud.get_link(db, code)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return RedirectResponse(url=link.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
