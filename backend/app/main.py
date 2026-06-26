import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Modular Imports
from app.api.v1.router import api_router
from app.db.models import Base
from app.db.session import engine
from app.main_bot import orchestrator

# 1. Setup Logging (Helps you see exactly what the bot is doing)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AlphaTrade-API")

# 2. Define the Lifespan (Management of Bot & API lifecycle)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    logger.info("🚦 Starting AlphaTrade API & Background Bot...")
    
    # Initialize Database Tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("💾 Database tables synced successfully.")
    except Exception as e:
        logger.error(f"❌ DB Initialization Error: {e}")

    # Launch Trading Engine as a Background Task
    bot_task = asyncio.create_task(orchestrator.run_forever())
    
    yield  # API is now running and reachable
    
    # --- SHUTDOWN ---
    logger.info("🚦 API shutting down... stopping background processes.")
    orchestrator.stop()
    bot_task.cancel() # Ensure the background task is killed
    logger.info("🛑 Bot stopped. Goodbye.")

# 3. INITIALIZE APP
app = FastAPI(
    title="AlphaTrade India Modular",
    description="Professional Algorithmic Trading System v1.0",
    lifespan=lifespan
)

# 4. ENABLE CORS (Allows React frontend to communicate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. INCLUDE MODULAR ROUTES
# This links all your endpoints (/dashboard, /market, /watchlist, etc.)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "status": "online",
        "bot_engine": "Operational" if orchestrator.is_running else "Standby",
        "version": "1.0.0"
    }