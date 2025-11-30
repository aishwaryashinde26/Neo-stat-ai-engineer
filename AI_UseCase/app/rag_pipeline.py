import os
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

import networkx as nx
import pickle





class RAGPipeline:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None
        self.kg = nx.Graph()
        self.documents = []
        
    def process_pdf(self, pdf_file):
        """Reads PDF, extracts text, chunks it, and builds Vector Store + KG"""
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
            
        # Chunking
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        self.documents.extend(chunks)
        
        # Build Vector Store
        if self.vector_store is None:
            self.vector_store = FAISS.from_texts(chunks, self.embeddings)
        else:
            self.vector_store.add_texts(chunks)
            
        # Build Knowledge Graph (Simplified)
        self._build_kg(chunks)
        
        return "PDF processed successfully."

    def _build_kg(self, chunks):
        """Simple entity extraction for KG (Mock implementation for speed)"""
        # In a real scenario, use an LLM or NER model to extract entities
        # Here we just link chunks to a central node or keywords
        for i, chunk in enumerate(chunks):
            node_id = f"chunk_{i}"
            self.kg.add_node(node_id, content=chunk[:50] + "...")
            # Extract capitalized words as naive entities
            words = [w for w in chunk.split() if w[0].isupper() and len(w) > 3]
            for word in set(words):
                self.kg.add_node(word, type="entity")
                self.kg.add_edge(node_id, word)

    def query(self, query, llm, conversation_context=""):
        """Hybrid Query: KG -> RAG -> LLM with conversation context"""
        
        # 1. Try KG (Naive search for entities in query)
        kg_context = []
        query_words = query.split()
        for word in query_words:
            if self.kg.has_node(word):
                neighbors = list(self.kg.neighbors(word))
                for n in neighbors:
                    if n.startswith("chunk_"):
                        # In a real app, retrieve full content. 
                        # Here we rely on Vector Store for full content.
                        pass
        
        # 2. RAG Retrieval
        if self.vector_store:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(query)
            context = "\n\n".join([d.page_content for d in docs])
        else:
            context = "No documents uploaded."
            
        # 3. Generate Answer with conversation context
        prompt_template = """
        You are an AI Booking Assistant. Use the following context and conversation history to answer the user's question.
        If the answer is not in the context, say you don't know, but try to be helpful.
        
        Conversation History:
        {conversation_history}
        
        Knowledge Base Context:
        {context}
        
        Current Question: {question}
        
        Answer:
        """
        prompt = PromptTemplate(
            template=prompt_template, 
            input_variables=["conversation_history", "context", "question"]
        )
        chain = prompt | llm
        
        response = chain.invoke({
            "conversation_history": conversation_context if conversation_context else "No previous conversation.",
            "context": context, 
            "question": query
        })
        return response.content

# Singleton instance
rag_pipeline = RAGPipeline()
