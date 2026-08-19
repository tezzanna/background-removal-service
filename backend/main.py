import io
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from rembg import remove, new_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bg-removal-api")

MODEL_NAME = os.environ.get("BG_REMOVAL_MODEL", "isnet-general-use")
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024

_session = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _session
    logger.info("Загружаю модель '%s'...", MODEL_NAME)
    _session = new_session(MODEL_NAME)
    logger.info("Модель загружена.")
    yield


app = FastAPI(
    title="Background Removal API",
    description="Сервис удаления фона с фотографий",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)) -> StreamingResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип файла: {file.content_type}. "
            f"Допустимые: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )

    raw_bytes = await file.read()

    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимум {MAX_FILE_SIZE_BYTES // (1024 * 1024)} МБ.",
        )

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Пустой файл.")

    try:
        result_bytes = remove(raw_bytes, session=_session)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Ошибка при обработке изображения")
        raise HTTPException(status_code=500, detail="Не удалось обработать изображение.") from exc

    return StreamingResponse(io.BytesIO(result_bytes), media_type="image/png")
