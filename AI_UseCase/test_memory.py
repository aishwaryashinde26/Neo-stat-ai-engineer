"""
Test script for the Memory Manager implementation.
This script tests the core functionality of the short-term memory system.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.memory_manager import memory_manager
from db.database import Base, engine
import uuid

# Initialize database
Base.metadata.create_all(bind=engine)

def test_basic_operations():
    """Test basic message storage and retrieval"""
    print("=" * 60)
    print("TEST 1: Basic Operations")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    
    # Add messages
    print("\n1. Adding 5 messages...")
    for i in range(5):
        memory_manager.add_message(session_id, "user" if i % 2 == 0 else "assistant", f"Message {i+1}")
    
    # Retrieve messages
    messages = memory_manager.get_recent_messages(session_id)
    print(f"   ✓ Added and retrieved {len(messages)} messages")
    
    # Verify content
    assert len(messages) == 5, "Should have 5 messages"
    print("   ✓ Message count verified")
    
    # Get count
    count = memory_manager.get_session_count(session_id)
    print(f"   ✓ Session count: {count}")
    
    print("\n✅ Test 1 PASSED\n")

def test_message_limit():
    """Test automatic cleanup to maintain 25 message limit"""
    print("=" * 60)
    print("TEST 2: Message Limit (25 messages)")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    
    # Add 30 messages
    print("\n1. Adding 30 messages...")
    for i in range(30):
        memory_manager.add_message(session_id, "user" if i % 2 == 0 else "assistant", f"Message {i+1}")
    
    # Check count
    count = memory_manager.get_session_count(session_id)
    print(f"   ✓ Final count: {count}")
    
    # Verify limit
    assert count <= 25, f"Should have at most 25 messages, but has {count}"
    print("   ✓ Message limit enforced correctly")
    
    # Verify we kept the most recent messages
    messages = memory_manager.get_recent_messages(session_id)
    last_message = messages[-1]['content']
    print(f"   ✓ Last message: '{last_message}'")
    assert "Message 30" in last_message, "Should keep most recent messages"
    
    print("\n✅ Test 2 PASSED\n")

def test_formatted_context():
    """Test context formatting for RAG and booking flow"""
    print("=" * 60)
    print("TEST 3: Formatted Context")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    
    # Add some messages
    print("\n1. Adding test messages...")
    memory_manager.add_message(session_id, "user", "Hello, I want to book an appointment")
    memory_manager.add_message(session_id, "assistant", "Sure! What's your name?")
    memory_manager.add_message(session_id, "user", "John Doe")
    
    # Test RAG format
    print("\n2. Testing RAG format...")
    rag_context = memory_manager.get_formatted_context(session_id, format_type='rag')
    print("   RAG Context:")
    print("   " + "\n   ".join(rag_context.split("\n")))
    assert "USER:" in rag_context, "Should have USER prefix"
    assert "ASSISTANT:" in rag_context, "Should have ASSISTANT prefix"
    print("   ✓ RAG format correct")
    
    # Test booking format
    print("\n3. Testing booking format...")
    booking_context = memory_manager.get_formatted_context(session_id, format_type='booking')
    print("   Booking Context:")
    print("   " + "\n   ".join(booking_context.split("\n")[:3]))  # Show first 3 lines
    assert "[" in booking_context, "Should have timestamp brackets"
    print("   ✓ Booking format correct")
    
    print("\n✅ Test 3 PASSED\n")

def test_session_isolation():
    """Test that sessions are isolated from each other"""
    print("=" * 60)
    print("TEST 4: Session Isolation")
    print("=" * 60)
    
    session1 = str(uuid.uuid4())
    session2 = str(uuid.uuid4())
    
    # Add messages to session 1
    print("\n1. Adding messages to Session 1...")
    memory_manager.add_message(session1, "user", "Session 1 message")
    
    # Add messages to session 2
    print("2. Adding messages to Session 2...")
    memory_manager.add_message(session2, "user", "Session 2 message")
    
    # Verify isolation
    messages1 = memory_manager.get_recent_messages(session1)
    messages2 = memory_manager.get_recent_messages(session2)
    
    print(f"   Session 1 count: {len(messages1)}")
    print(f"   Session 2 count: {len(messages2)}")
    
    assert len(messages1) == 1, "Session 1 should have 1 message"
    assert len(messages2) == 1, "Session 2 should have 1 message"
    assert "Session 1" in messages1[0]['content'], "Session 1 should have its own message"
    assert "Session 2" in messages2[0]['content'], "Session 2 should have its own message"
    
    print("   ✓ Sessions are properly isolated")
    
    print("\n✅ Test 4 PASSED\n")

def test_clear_session():
    """Test clearing a session"""
    print("=" * 60)
    print("TEST 5: Clear Session")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    
    # Add messages
    print("\n1. Adding 5 messages...")
    for i in range(5):
        memory_manager.add_message(session_id, "user", f"Message {i+1}")
    
    count_before = memory_manager.get_session_count(session_id)
    print(f"   Count before clear: {count_before}")
    
    # Clear session
    print("\n2. Clearing session...")
    deleted = memory_manager.clear_session(session_id)
    print(f"   Deleted {deleted} messages")
    
    # Verify cleared
    count_after = memory_manager.get_session_count(session_id)
    print(f"   Count after clear: {count_after}")
    
    assert count_after == 0, "Session should be empty after clear"
    print("   ✓ Session cleared successfully")
    
    print("\n✅ Test 5 PASSED\n")

def test_messages_as_list():
    """Test getting messages in Streamlit format"""
    print("=" * 60)
    print("TEST 6: Messages as List (Streamlit Format)")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    
    # Add messages
    print("\n1. Adding messages...")
    memory_manager.add_message(session_id, "user", "Hello")
    memory_manager.add_message(session_id, "assistant", "Hi there!")
    
    # Get as list
    messages = memory_manager.get_messages_as_list(session_id)
    print(f"   Retrieved {len(messages)} messages")
    print(f"   Format: {messages}")
    
    # Verify format
    assert isinstance(messages, list), "Should return a list"
    assert all('role' in msg and 'content' in msg for msg in messages), "Should have role and content"
    assert len(messages[0]) == 2, "Should only have role and content (no timestamp/metadata)"
    
    print("   ✓ Streamlit format correct")
    
    print("\n✅ Test 6 PASSED\n")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MEMORY MANAGER TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_basic_operations()
        test_message_limit()
        test_formatted_context()
        test_session_isolation()
        test_clear_session()
        test_messages_as_list()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe short-term memory system is working correctly.")
        print("You can now run the Streamlit app to test it in action.")
        print("\nRun: streamlit run app/main.py")
        print("=" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
