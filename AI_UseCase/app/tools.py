from sqlalchemy.orm import Session
from db.models import Booking, Customer
from db.database import SessionLocal
import smtplib
from email.mime.text import MIMEText

import uuid

def save_booking_tool(name, email, phone, booking_type, date, time, extra_info=""):
    """Saves a booking to the database."""
    db: Session = SessionLocal()
    try:
        # Check if customer exists
        customer = db.query(Customer).filter(Customer.email == email).first()
        if not customer:
            customer = Customer(name=name, email=email, phone=phone)
            db.add(customer)
            db.commit()
            db.refresh(customer)
        
        # Create booking
        booking_id = str(uuid.uuid4())
        booking = Booking(
            id=booking_id,
            customer_id=customer.customer_id,
            booking_type=booking_type,
            date=date,
            time=time,
            extra_info=extra_info,
            status="confirmed"
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return {"success": True, "id": booking.id, "message": f"Booking saved successfully! Booking ID: {booking.id}"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error saving booking: {str(e)}"}
    finally:
        db.close()

def check_availability(date, time):
    """Checks if a slot is already booked."""
    db: Session = SessionLocal()
    try:
        existing = db.query(Booking).filter(
            Booking.date == date,
            Booking.time == time,
            Booking.status == "confirmed"
        ).first()
        return existing is None
    finally:
        db.close()

def cancel_booking_tool(booking_id):
    """Cancels a booking by ID."""
    db: Session = SessionLocal()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return "Booking not found."
        
        booking.status = "cancelled"
        db.commit()
        return f"Booking {booking_id} cancelled successfully."
    except Exception as e:
        db.rollback()
        return f"Error cancelling booking: {str(e)}"
    finally:
        db.close()

def send_email_tool(to_email, subject, body):
    """Sends an email using SMTP if credentials are provided, otherwise mocks it."""
    import os
    
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not sender_email or not sender_password:
        print(f"--- EMAIL MOCKED (Missing Credentials) ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print(f"------------------------------------------")
        return "Email sent successfully (Mocked - Set EMAIL_SENDER/PASSWORD to send real emails)."

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return "Email sent successfully."
    except Exception as e:
        print(f"Error sending email: {e}")
        return f"Failed to send email: {str(e)}"
