import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# =========================================================
# CONFIGURATION
# =========================================================
#EMAIL_SENDER = os.getenv("EMAIL_SENDER")
#EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
#EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", EMAIL_SENDER)

EMAIL_SENDER = "csense353@gmail.com"
EMAIL_PASSWORD = "ehpn raxq hcrz tffq"
EMAIL_RECEIVER="csense353@gmail.com"
# Your actual OneOrigin / OneCloud website
ALLOWED_ORIGINS = [
    "https://www.oneorigin-tech.com/onecloud.html",
    "https://www.oneorigin-tech.com/oneops.html",
    "https://www.oneorigin-tech.com/onecampus.html",
]

# =========================================================
# FASTAPI APP
# =========================================================
app = FastAPI(
    title="OneCloud API",
    description="OneCloud waitlist registration API",
    version="1.0.0"
)

# =========================================================
# CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

# =========================================================
# REQUEST MODEL
# =========================================================
class WaitlistRequest(BaseModel):
    email: EmailStr
    plan: str

# =========================================================
# ALLOWED PLANS
# =========================================================
ALLOWED_PLANS = {
    "starter": "Starter — ₹1,499 / month",
    "pro": "Pro — ₹4,999 / month",
    "max": "Max — ₹9,999 / month",
    "dedicated": "Dedicated — ₹19,999 / month",
    "dedicated-plus": "Dedicated+ — ₹59,999 / month",
    "threadripper-turbo": "Threadripper Turbo — ₹99 / hour",
    "institutional": "Institutional / Enterprise",
}

# =========================================================
# SEND EMAIL
# =========================================================
def send_waitlist_email(email: str, plan: str):
    if not EMAIL_SENDER:
        return False, "EMAIL_SENDER is not configured."
    if not EMAIL_PASSWORD:
        return False, "EMAIL_PASSWORD is not configured."
    if not EMAIL_RECEIVER:
        return False, "EMAIL_RECEIVER is not configured."
    try:

        registration_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        plan_name = ALLOWED_PLANS.get(
            plan,
            plan
        )
        # -------------------------------------------------
        # EMAIL MESSAGE
        # -------------------------------------------------
        msg = MIMEMultipart("alternative")
        msg["Subject"] = (
            "New OneCloud Waitlist Registration - "
            f"{registration_time}"
        )
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        body = f"""
            New OneCloud Waitlist Registration
            ===================================

            Email:
            {email}

            Interested Plan:
            {plan_name}

            Registration Time:
            {registration_time}

            Source:
            OneCloud Website
            """
        msg.attach(
            MIMEText(body, "plain")
        )
        # -------------------------------------------------
        # GMAIL SMTP
        # -------------------------------------------------
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=20
        ) as server:

            server.login(
                EMAIL_SENDER,
                EMAIL_PASSWORD
            )

            server.sendmail(
                EMAIL_SENDER,
                EMAIL_RECEIVER,
                msg.as_string()
            )

        return True, None
    
    except Exception as e:
        print(
            "Email sending error:",
            str(e)
        )
        return False, str(e)
    
# =========================================================
# HEALTH CHECK
# =========================================================
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "OneCloud API"
    }

# =========================================================
# WAITLIST ENDPOINT
# =========================================================
@app.post("/waitlist")
def register_waitlist(
    request: WaitlistRequest
):
    # -----------------------------------------------------
    # Validate plan
    # -----------------------------------------------------
    if request.plan not in ALLOWED_PLANS:

        raise HTTPException(
            status_code=400,
            detail="Invalid plan selected."
        )

    # -----------------------------------------------------
    # Send notification
    # -----------------------------------------------------
    success, error = send_waitlist_email(
        email=str(request.email),
        plan=request.plan
    )

    if not success:
        print(
            "Waitlist registration failed:",
            error
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to register your interest right now."
        )

    # -----------------------------------------------------
    # Success
    # -----------------------------------------------------
    return {
        "success": True,
        "message": "Waitlist registration received."
    }

# =========================================================
# LOCAL DEVELOPMENT
# =========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(
            os.getenv("PORT", 8000)
        )
    )