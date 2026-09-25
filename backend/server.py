import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core import db, client, ORIGIN
from seed import seed_archive
from knowledge import router as knowledge_router
from editorial import router as editorial_router
from auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_archive()
    yield
    client.close()


app = FastAPI(title="VI Archive API", version="1.0.0", lifespan=lifespan,
              docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=[ORIGIN], allow_credentials=True,
                   allow_methods=["GET", "POST", "PUT", "DELETE"],
                   allow_headers=["Content-Type", "X-CSRF-Token", "If-None-Match"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("origin")
        if origin and origin != ORIGIN:
            return JSONResponse({"detail": "Origem não autorizada."}, status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store" if "/editorial" in request.url.path or "/auth" in request.url.path else "no-cache"
    return response


@app.get("/api/health")
async def health():
    await db.command("ping")
    return {"status": "ok", "service": "VI Archive", "version": "1"}


app.include_router(knowledge_router)
app.include_router(auth_router)
app.include_router(editorial_router)
logging.basicConfig(level=logging.INFO)