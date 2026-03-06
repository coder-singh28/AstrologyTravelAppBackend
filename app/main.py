from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from app.logger import setup_logger
from app.routers import auth_router, user_router, astro_router, city_router,google_router
from starlette.middleware.sessions import SessionMiddleware

# ========================================
# FastAPI Application Configuration
# ========================================
app = FastAPI(
    title="Astrology Travel App",
    description="Backend API for travel astrology predictions",
    version="1.0.0"
)
app.add_middleware(
    SessionMiddleware,
    secret_key="1234567890abcdef"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Enable session support
app.add_middleware(
    SessionMiddleware,
    secret_key="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",  # TODO: Move to environment variable
    session_cookie="google_session",
    https_only=False  # Set to True in production
)

# Setup logger
logger = setup_logger()

# Include routers
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(astro_router.router)
app.include_router(city_router.router)
app.include_router(google_router.router)

# ========================================
# Lifecycle Events
# ========================================
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("[STARTUP] FastAPI application started")


# ----------------------------------------
# Home page
# ----------------------------------------
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve home page for authenticated users.
    Requires active session.
    """
    user = request.session.get("user")
    
    if not user:
        return RedirectResponse(url="/")
    
    logger.info(f"Serving home page for user: {user['email']}")
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": user,
            "email": user["email"],
            "name": user["name"],
        }
    )


# ========================================
# Routes
# ========================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve landing page"""
    logger.info("Landing page accessed")
    # return templates.TemplateResponse(request=request, name="index.html", context={})
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/logout")
async def logout(request: Request):
    """Clear user session and logout"""
    user = request.session.get("user")
    email = user.get("email") if user else "Unknown"
    logger.info(f"User logged out: {email}")
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)