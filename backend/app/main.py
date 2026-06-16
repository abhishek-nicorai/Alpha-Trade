from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager 

# Modular Imports
from app.api.v1.router import api_router
from app.db.models import Base
from app.db.session import engine
from app.main_bot import orchestrator

# 1. Define the Lifespan (The most important logic for automation)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    print("🚦 AlphaTrade API is starting up...")
    
    # CRITICAL: This line launches the Trading Engine in the background
    # It allows the API to serve the UI while the Bot trades concurrently
    asyncio.create_task(orchestrator.run_forever())
    
    yield # The app stays in this state while running

    # --- SHUTDOWN LOGIC ---
    print("🚦 API shutting down... stopping bot.")
    # This calls the stop() method we wrote to kill the WebSocket thread
    orchestrator.stop()

# 2. INITIALIZE APP with Lifespan
app = FastAPI(
    title="AlphaTrade India Modular", 
    lifespan=lifespan 
)

# 3. Enable CORS (Ensures React can talk to this server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Initialize Database Tables automatically on start
try:
    Base.metadata.create_all(bind=engine)
    print("💾 Database tables synced successfully.")
except Exception as e:
    print(f"⚠️ DB Initialization Error: {e}")

# 5. Include Modular API Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "AlphaTrade Modular API is running",
        "bot_status": "Operational" if orchestrator.is_running else "Standby"
    }