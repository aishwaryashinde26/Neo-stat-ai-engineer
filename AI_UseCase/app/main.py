import streamlit as st
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import io
import uuid

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load env vars first
load_dotenv()

# Initialize database
from db.database import Base, engine, SessionLocal
from db.models import Booking, Customer, ConversationHistory

# Create tables
Base.metadata.create_all(bind=engine)

# Imports
from app.rag_pipeline import rag_pipeline
from app.booking_flow import BookingFlow
from app.tools import save_booking_tool, send_email_tool, check_availability, cancel_booking_tool
from app.admin_dashboard import admin_page
from app.memory_manager import memory_manager
from langchain_groq import ChatGroq
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Initialize LLM
try:
    llm = ChatGroq(model="llama-3.3-70b-versatile")
except Exception as e:
    st.error(f"Failed to initialize Groq LLM: {str(e)}. Please set GROQ_API_KEY in .env")
    llm = None

booking_flow = BookingFlow(llm)

def main():
    st.set_page_config(page_title="NeoBook AI", layout="wide", page_icon="🤖")
    
    # Sidebar
    with st.sidebar:
        st.title("🤖 NeoBook AI")
        st.markdown("---")
        
        # PDF Upload
        st.header("📚 Knowledge Base")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        if uploaded_file:
            with st.spinner("Processing PDF..."):
                msg = rag_pipeline.process_pdf(uploaded_file)
                st.success(msg)
        
        st.markdown("---")
        
        # Quick Stats
        st.header("📊 Quick Stats")
        db = SessionLocal()
        total_bookings = db.query(Booking).count()
        confirmed = db.query(Booking).filter(Booking.status == "confirmed").count()
        cancelled = db.query(Booking).filter(Booking.status == "cancelled").count()
        total_customers = db.query(Customer).count()
        db.close()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Bookings", total_bookings)
            st.metric("Confirmed", confirmed, delta=None)
        with col2:
            st.metric("Customers", total_customers)
            st.metric("Cancelled", cancelled, delta=None)

    # Main Title
    st.title("🤖 NeoBook AI - Intelligent Booking Assistant")
    st.markdown("*Your AI-powered booking companion with advanced features*")

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💬 Chat", 
        "📅 Calendar", 
        "🕸️ Knowledge Graph", 
        "📊 Insights",
        "⚙️ Admin",
        "🔧 Settings"
    ])

    with tab1:
        chat_interface()
    
    with tab2:
        calendar_interface()
        
    with tab3:
        kg_interface()
        
    with tab4:
        insights_interface()
        
    with tab5:
        admin_interface()
        
    with tab6:
        settings_interface()

def chat_interface():
    st.header("💬 Chat with Booking Assistant")
    
    # Session State
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        # Load conversation history from database
        st.session_state.messages = memory_manager.get_messages_as_list(
            st.session_state.session_id,
            limit=25
        )
    
    if "booking_slots" not in st.session_state:
        st.session_state.booking_slots = {}
    
    # Quick Actions
    with st.expander("⚡ Quick Actions", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📅 Book Appointment", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "I want to book an appointment"
                })
                st.rerun()
        with col2:
            if st.button("❓ Ask About Services", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What services do you offer?"
                })
                st.rerun()
        with col3:
            if st.button("🔍 Check Availability", use_container_width=True):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What time slots are available?"
                })
                st.rerun()
    
    # Chat Controls
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Messages:** {len(st.session_state.messages)}")
    with col2:
        if st.button("🗑️ Clear Chat"):
            # Clear from database
            memory_manager.clear_session(st.session_state.session_id)
            st.session_state.messages = []
            st.session_state.booking_slots = {}
            st.rerun()
    
    # Chat History
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
    
    # Suggested Prompts (show only when chat is empty)
    if len(st.session_state.messages) == 0:
        st.info("💡 **Try asking:**")
        suggestions = [
            "I want to book a consultation for tomorrow at 3 PM",
            "What are your available time slots?",
            "Tell me about your services"
        ]
        for suggestion in suggestions:
            st.markdown(f"- *{suggestion}*")
    
    # Chat Input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to session state and database
        st.session_state.messages.append({"role": "user", "content": prompt})
        memory_manager.add_message(st.session_state.session_id, "user", prompt)
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = process_message(prompt, st.session_state.session_id)
                st.markdown(response)
                
                # Add assistant response to session state and database
                st.session_state.messages.append({"role": "assistant", "content": response})
                memory_manager.add_message(st.session_state.session_id, "assistant", response)
    
    # Export Chat
    if len(st.session_state.messages) > 0:
        st.markdown("---")
        chat_text = "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])
        st.download_button(
            label="📥 Export Chat",
            data=chat_text,
            file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

def calendar_interface():
    st.header("📅 Booking Calendar")
    
    db = SessionLocal()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "confirmed", "cancelled"])
    with col2:
        booking_type_filter = st.text_input("Booking Type (contains)")
    with col3:
        search_name = st.text_input("Search by Name/Email")
    
    # Query bookings
    query = db.query(Booking)
    if status_filter != "All":
        query = query.filter(Booking.status == status_filter)
    
    bookings = query.all()
    
    # Extract data BEFORE closing session to avoid DetachedInstanceError
    booking_data = []
    for b in bookings:
        booking_data.append({
            "id": b.id,
            "customer_name": b.customer.name,
            "customer_email": b.customer.email,
            "customer_phone": b.customer.phone,
            "booking_type": b.booking_type,
            "date": b.date,
            "time": b.time,
            "status": b.status,
            "created_at": b.created_at
        })
    
    db.close()
    
    # Apply filters on extracted data
    if booking_type_filter:
        booking_data = [b for b in booking_data if booking_type_filter.lower() in b["booking_type"].lower()]
    if search_name:
        booking_data = [b for b in booking_data if search_name.lower() in b["customer_name"].lower() or search_name.lower() in b["customer_email"].lower()]
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Total Bookings", len(booking_data))
    with col2:
        confirmed_count = len([b for b in booking_data if b["status"] == "confirmed"])
        st.metric("✅ Confirmed", confirmed_count)
    with col3:
        cancelled_count = len([b for b in booking_data if b["status"] == "cancelled"])
        st.metric("❌ Cancelled", cancelled_count)
    with col4:
        unique_customers = len(set([b["customer_email"] for b in booking_data]))
        st.metric("👥 Unique Customers", unique_customers)
    
    st.markdown("---")
    
    # Display bookings
    if booking_data:
        data = []
        for b in booking_data:
            data.append({
                "ID": b["id"],
                "Customer": b["customer_name"],
                "Email": b["customer_email"],
                "Phone": b["customer_phone"],
                "Type": b["booking_type"],
                "Date": b["date"],
                "Time": b["time"],
                "Status": b["status"],
                "Created": b["created_at"].strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(data)
        
        # Color-code status
        def highlight_status(row):
            if row['Status'] == 'confirmed':
                return ['background-color: #d4edda'] * len(row)
            elif row['Status'] == 'cancelled':
                return ['background-color: #f8d7da'] * len(row)
            return [''] * len(row)
        
        st.dataframe(df.style.apply(highlight_status, axis=1), use_container_width=True)
        
        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"bookings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No bookings found matching your filters.")

def kg_interface():
    st.header("🕸️ Knowledge Graph Visualization")
    
    if rag_pipeline.kg.number_of_nodes() > 0:
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔵 Nodes", rag_pipeline.kg.number_of_nodes())
        with col2:
            st.metric("🔗 Edges", rag_pipeline.kg.number_of_edges())
        with col3:
            density = nx.density(rag_pipeline.kg)
            st.metric("📊 Density", f"{density:.3f}")
        
        st.markdown("---")
        
        # Layout options
        layout_option = st.selectbox("Graph Layout", ["Spring", "Circular", "Random"])
        
        # Visualization
        fig, ax = plt.subplots(figsize=(12, 10))
        
        if layout_option == "Spring":
            pos = nx.spring_layout(rag_pipeline.kg, k=0.5, iterations=50)
        elif layout_option == "Circular":
            pos = nx.circular_layout(rag_pipeline.kg)
        else:
            pos = nx.random_layout(rag_pipeline.kg)
        
        # Draw
        nx.draw_networkx_nodes(rag_pipeline.kg, pos, node_color='skyblue', node_size=1000, alpha=0.9, ax=ax)
        nx.draw_networkx_edges(rag_pipeline.kg, pos, edge_color='gray', alpha=0.5, ax=ax)
        nx.draw_networkx_labels(rag_pipeline.kg, pos, font_size=8, font_weight='bold', ax=ax)
        
        ax.set_title("Knowledge Graph", fontsize=16, fontweight='bold')
        ax.axis('off')
        
        st.pyplot(fig)
        
        # Save graph
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        st.download_button(
            label="📥 Download Graph Image",
            data=buf,
            file_name=f"knowledge_graph_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png"
        )
    else:
        st.info("📚 Knowledge Graph is empty. Upload a PDF to populate it.")

def insights_interface():
    st.header("📊 Booking Insights & Analytics")
    
    db = SessionLocal()
    bookings = db.query(Booking).all()
    db.close()
    
    if not bookings:
        st.info("No booking data available yet.")
        return
    
    # Prepare data
    df = pd.DataFrame([{
        "date": b.date,
        "time": b.time,
        "type": b.booking_type,
        "status": b.status,
        "created_at": b.created_at
    } for b in bookings])
    
    # Booking Status Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Booking Status Distribution")
        status_counts = df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                     title="Bookings by Status", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Booking Types")
        type_counts = df['type'].value_counts()
        fig = px.bar(x=type_counts.index, y=type_counts.values,
                     labels={'x': 'Booking Type', 'y': 'Count'},
                     title="Bookings by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.subheader("📅 Booking Timeline")
    df['created_date'] = pd.to_datetime(df['created_at']).dt.date
    timeline = df.groupby('created_date').size().reset_index(name='count')
    fig = px.line(timeline, x='created_date', y='count',
                  labels={'created_date': 'Date', 'count': 'Number of Bookings'},
                  title="Bookings Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    # Popular Time Slots
    st.subheader("⏰ Popular Time Slots")
    time_counts = df['time'].value_counts().head(10)
    fig = px.bar(x=time_counts.index, y=time_counts.values,
                 labels={'x': 'Time Slot', 'y': 'Bookings'},
                 title="Top 10 Most Booked Time Slots")
    st.plotly_chart(fig, use_container_width=True)

def admin_interface():
    admin_page()

def settings_interface():
    st.header("🔧 Settings & Configuration")
    
    # Theme (placeholder - Streamlit doesn't support runtime theme changes easily)
    st.subheader("🎨 Appearance")
    st.info("💡 Use the Streamlit menu (☰ → Settings → Theme) to change the app theme.")
    
    st.markdown("---")
    
    # System Info
    st.subheader("ℹ️ System Information")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**App Name:** NeoBook AI")
        st.markdown("**Version:** 2.0.0")
        st.markdown("**LLM Model:** llama-3.3-70b-versatile")
    with col2:
        st.markdown("**Database:** SQLite")
        st.markdown("**Vector Store:** FAISS")
        st.markdown("**Embeddings:** all-MiniLM-L6-v2")
    
    st.markdown("---")
    
    # About
    st.subheader("📖 About")
    st.markdown("""
    **NeoBook AI** is an intelligent booking assistant powered by:
    - 🤖 **Groq LLM** for natural language understanding
    - 📚 **RAG Pipeline** with Knowledge Graph for context-aware responses
    - 💾 **SQLite Database** for reliable data storage
    - 📊 **Advanced Analytics** for business insights
    
    Built with ❤️ using Streamlit, LangChain, and NetworkX.
    """)
    
    st.markdown("---")
    
    # Danger Zone
    with st.expander("⚠️ Danger Zone", expanded=False):
        st.warning("**Warning:** These actions cannot be undone!")
        if st.button("🗑️ Clear All Chat History", type="secondary"):
            if "messages" in st.session_state:
                st.session_state.messages = []
                st.success("Chat history cleared!")
        
        if st.button("🔄 Reset Knowledge Graph", type="secondary"):
            rag_pipeline.kg.clear()
            rag_pipeline.documents = []
            rag_pipeline.vector_store = None
            st.success("Knowledge Graph reset!")

def process_message(user_input, session_id):
    # Get conversation context
    conversation_context = memory_manager.get_formatted_context(session_id, format_type='rag')
    
    # Check Booking Intent
    is_booking = False
    if "book" in user_input.lower() or st.session_state.booking_slots:
        is_booking = True
        
    if is_booking:
        # Extract slots
        extracted = booking_flow.extract_intent_and_slots(st.session_state.messages, user_input)
        
        # Update session slots
        for k, v in extracted.items():
            if v:
                st.session_state.booking_slots[k] = v
                
        # Decide next step
        next_step = booking_flow.get_next_step(st.session_state.booking_slots)
        
        if next_step == "READY_TO_BOOK":
            slots = st.session_state.booking_slots
            
            # Check Availability
            if not check_availability(slots['date'], slots['time']):
                return f"❌ Sorry, the slot on **{slots['date']}** at **{slots['time']}** is already booked. Please choose another time."
            
            # Execute Booking
            res = save_booking_tool(slots['name'], slots['email'], slots['phone'], slots['booking_type'], slots['date'], slots['time'])
            
            if isinstance(res, dict) and res.get("success"):
                booking_id = res["id"]
                message = res["message"]
                
                # Format Email
                email_body = f"""Booking is confirmed!

Booking ID: {booking_id}

- *Name:* {slots['name']}
- *Email:* {slots['email']}
- *Phone:* {slots['phone']}
- *Room Type:* {slots['booking_type']}
- *Date:* {slots['date']}
- *Time:* {slots['time']}"""

                # Send Email
                send_email_tool(slots['email'], "Booking Confirmation", email_body)
                
                # Reset slots
                st.session_state.booking_slots = {}
                return f"✅ **Booking Confirmed!**\n\nBooking ID: `{booking_id}`\n\n📧 A confirmation email has been sent to **{slots['email']}**."
            else:
                return f"❌ Failed to save booking: {res.get('message') if isinstance(res, dict) else res}"
        else:
            return next_step

    # RAG / General Chat
    return rag_pipeline.query(user_input, llm, conversation_context)

if __name__ == "__main__":
    main()