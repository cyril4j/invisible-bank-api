"""
Admin dashboard endpoints.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.admin_service import AdminService
from app.core.admin_auth import verify_admin_credentials
from app.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])

# Set up templates
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials)
):
    """
    Admin dashboard showing recent accounts and transactions.

    Requires HTTP Basic Authentication:
    - Username: admin
    - Password: admin
    """
    # Get dashboard data
    stats = AdminService.get_dashboard_stats(db)
    accounts = AdminService.get_recent_accounts(db, limit=10)
    transactions = AdminService.get_recent_transactions(db, limit=10)

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "stats": stats,
            "accounts": accounts,
            "transactions": transactions,
            "version": settings.app_version
        }
    )


@router.get("/logout")
async def admin_logout():
    """
    Logout from admin panel.

    Note: HTTP Basic Auth doesn't have a standard logout mechanism.
    This endpoint returns 401 to force browser to clear credentials.
    """
    return HTMLResponse(
        content="""
        <html>
            <head>
                <title>Logged Out</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .message {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        text-align: center;
                    }
                    h1 {
                        color: #333;
                        margin-bottom: 20px;
                    }
                    p {
                        color: #666;
                        margin-bottom: 20px;
                    }
                    a {
                        color: #667eea;
                        text-decoration: none;
                        font-weight: 600;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="message">
                    <h1>Logged Out</h1>
                    <p>You have been logged out from the admin panel.</p>
                    <p>To log in again, <a href="/admin">click here</a>.</p>
                    <p><small>Note: You may need to close your browser to fully clear credentials.</small></p>
                </div>
            </body>
        </html>
        """,
        status_code=401,
        headers={"WWW-Authenticate": "Basic"}
    )
