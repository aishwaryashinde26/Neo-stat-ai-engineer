# NeoBook AI - Intelligent Booking Assistant

An AI-powered booking assistant built with Streamlit, LangChain, and advanced NLP capabilities.

## 🚀 Features

- **💬 Intelligent Chat Interface**: Natural language booking conversations
- **📅 Smart Calendar Management**: Automated booking scheduling
- **🕸️ Knowledge Graph**: Context-aware information retrieval
- **📊 Advanced Analytics**: Business insights and reporting
- **⚙️ Admin Dashboard**: Comprehensive booking management
- **📚 RAG Pipeline**: PDF knowledge base integration
- **💾 Persistent Memory**: Conversation history and context retention

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - LangChain for LLM orchestration
  - Groq LLM (llama-3.3-70b-versatile)
  - FAISS for vector storage
  - Sentence Transformers for embeddings
- **Backend**: 
  - SQLite database
  - SQLAlchemy ORM
  - NetworkX for knowledge graphs
- **Visualization**: 
  - Plotly for interactive charts
  - Matplotlib for network graphs
  - Pandas for data processing

## 📋 Prerequisites

- Python 3.8+
- Groq API Key

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/aishwaryashinde26/Neo-stat-ai-engineer.git
cd Neo-stat-ai-engineer
```

2. Install dependencies:
```bash
cd AI_UseCase
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file in AI_UseCase directory
GROQ_API_KEY=your_groq_api_key_here
```

4. Initialize the database:
```bash
python create_tables.py
```

5. Run the application:
```bash
streamlit run app/main.py
```

## 📖 Usage

### Chat Interface
- Natural language booking requests
- Quick action buttons for common tasks
- Conversation history with persistence
- Export chat functionality

### Calendar Management
- View all bookings with filtering options
- Status-based color coding
- Export to CSV functionality
- Search by customer details

### Knowledge Graph
- Visual representation of extracted knowledge
- Multiple layout options
- Interactive exploration
- Export capabilities

### Analytics Dashboard
- Booking status distribution
- Popular time slots analysis
- Timeline visualization
- Customer insights

### Admin Features
- Booking management (confirm/cancel)
- Customer database
- System statistics
- Bulk operations

## 🔧 Configuration

The application uses several configuration files:

- `config/config.py`: Main application settings
- `.env`: Environment variables (API keys, etc.)
- `requirements.txt`: Python dependencies

## 📁 Project Structure

```
AI_UseCase/
├── app/
│   ├── main.py              # Main Streamlit application
│   ├── booking_flow.py      # Booking logic and flow management
│   ├── rag_pipeline.py      # RAG implementation with knowledge graph
│   ├── memory_manager.py    # Conversation memory management
│   ├── tools.py            # Booking tools and utilities
│   └── admin_dashboard.py   # Admin interface
├── db/
│   ├── database.py         # Database connection and setup
│   └── models.py           # SQLAlchemy models
├── models/
│   ├── llm.py              # LLM configuration
│   └── embeddings.py       # Embedding models
├── config/
│   └── config.py           # Application configuration
├── data/                   # Database files (generated)
├── create_tables.py        # Database initialization
├── test_memory.py          # Memory system tests
└── requirements.txt        # Dependencies
```

## 🤖 AI Capabilities

### Natural Language Understanding
- Intent recognition for booking requests
- Entity extraction (dates, times, contact info)
- Context-aware responses
- Multi-turn conversation handling

### Knowledge Management
- PDF document processing and indexing
- Knowledge graph construction
- Semantic search capabilities
- Context retrieval for accurate responses

### Booking Intelligence
- Availability checking
- Slot recommendation
- Conflict resolution
- Automated confirmation workflows

## 📊 Analytics Features

- Real-time booking statistics
- Customer behavior analysis
- Time slot popularity metrics
- Status distribution visualizations
- Export capabilities for reporting

## 🔒 Security & Privacy

- Local database storage
- Conversation privacy
- Secure API key management
- Data export controls

## 🚀 Deployment

For production deployment:

1. Set up environment variables securely
2. Configure database backup procedures
3. Implement proper logging
4. Set up monitoring and alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

- **Aishwarya Shinde** - AI Engineer

## 📞 Support

For questions or support, please create an issue in this repository.

---

*Built with ❤️ using Streamlit, LangChain, and advanced AI technologies.*
