import streamlit as st
import pandas as pd
from db.database import SessionLocal
from db.models import Booking, Customer
from app.tools import cancel_booking_tool

def admin_page():
    st.title("Admin Dashboard")
    
    db = SessionLocal()
    bookings = db.query(Booking).all()
    
    data = []
    for b in bookings:
        data.append({
            "ID": b.id,
            "Customer": b.customer.name,
            "Email": b.customer.email,
            "Type": b.booking_type,
            "Date": b.date,
            "Time": b.time,
            "Status": b.status,
            "Created At": b.created_at
        })
    
    df = pd.DataFrame(data)
    
    st.subheader("All Bookings")
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No bookings found.")
        
    db.close()
    
    st.markdown("---")
    st.subheader("🗑️ Manage Bookings")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        booking_id = st.text_input("Enter Booking ID to Cancel")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Cancel Booking", type="primary", use_container_width=True):
            if booking_id:
                res = cancel_booking_tool(booking_id)
                st.success(res)
                st.rerun()
            else:
                st.warning("Please enter a Booking ID")
