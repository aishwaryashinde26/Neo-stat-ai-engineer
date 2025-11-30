from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional

class BookingState(BaseModel):
    name: Optional[str] = Field(description="Customer name")
    email: Optional[str] = Field(description="Customer email")
    phone: Optional[str] = Field(description="Customer phone number")
    booking_type: Optional[str] = Field(description="Type of service/booking")
    date: Optional[str] = Field(description="Date of booking")
    time: Optional[str] = Field(description="Time of booking")
    confirmation: Optional[bool] = Field(description="User confirmed booking")

class BookingFlow:
    def __init__(self, llm):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=BookingState)
        
    def extract_intent_and_slots(self, history, current_input):
        """Extracts booking details from conversation."""
        prompt = PromptTemplate(
            template="""
            You are an AI Booking Assistant. Analyze the conversation and extract booking details for the CURRENT booking request.
            
            RULES:
            1. If the conversation history contains a previous successful booking (indicated by "Booking Confirmed"), IGNORE the details and confirmation from that previous booking.
            2. Treat the "Current Input" as the start of a new booking or a continuation of the current incomplete booking.
            3. Do NOT set "confirmation" to true unless the user has explicitly confirmed the CURRENT booking summary in the most recent turns.
            4. If the user says "same as before", you MAY use previous details, otherwise start fresh.
            
            Return a JSON object with the following fields: name, email, phone, booking_type, date, time, confirmation.
            If a field is missing, set it to null.
            
            Conversation History:
            {history}
            
            Current Input: {input}
            
            {format_instructions}
            """,
            input_variables=["history", "input"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | self.parser
        try:
            return chain.invoke({"history": history, "input": current_input})
        except Exception:
            return {}

    def get_next_step(self, current_slots):
        """Determines the next question to ask based on missing slots."""
        required_slots = ["name", "email", "phone", "booking_type", "date", "time"]
        missing = [slot for slot in required_slots if not current_slots.get(slot)]
        
        if missing:
            return f"Please provide your {missing[0]}."
        
        if not current_slots.get("confirmation"):
            summary = f"Booking Summary:\nName: {current_slots['name']}\nEmail: {current_slots['email']}\nService: {current_slots['booking_type']}\nDate: {current_slots['date']}\nTime: {current_slots['time']}"
            return f"{summary}\n\nDo you confirm this booking? (Yes/No)"
            
        return "READY_TO_BOOK"
