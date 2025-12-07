import asyncio
import json
from typing import List, Dict, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document

from models.database import Chapter, ChatSession, ChatMessage, Embedding, User
from models.schemas import ChatRequest, ChatResponse
from services.modules_service import get_chapter_content


class RAGChatService:
    def __init__(self):
        # Initialize embeddings model
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        # Initialize LLM
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

        # Store vector stores (in production, use a persistent vector database)
        self.vector_stores = {}

        # Create a prompt template for the QA chain
        self.qa_prompt = PromptTemplate(
            template="""You are an expert assistant for the Physical AI & Humanoid Robotics textbook.
            Use the following context to answer the question. If the context doesn't contain enough information,
            say "I don't have enough information in the textbook to answer that question."

            Context: {context}

            Question: {question}

            Helpful Answer:""",
            input_variables=["context", "question"]
        )

    def create_embeddings_for_chapter(self, db: Session, chapter_id: int):
        """Create embeddings for a specific chapter"""
        chapter_content = get_chapter_content(db, chapter_id)
        if not chapter_content:
            return False

        # Split the content into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(chapter_content)

        # Create documents
        documents = [Document(page_content=chunk, metadata={"chapter_id": chapter_id}) for chunk in chunks]

        # Create vector store
        vector_store = FAISS.from_documents(documents, self.embeddings)

        # Store in memory (in production, save to a persistent vector database)
        self.vector_stores[chapter_id] = vector_store

        # Save embeddings to database (optional, for persistence)
        for i, chunk in enumerate(chunks):
            embedding_vector = self.embeddings.embed_query(chunk)
            embedding_record = Embedding(
                content_id=chapter_id,
                content_type="chapter",
                embedding_vector=json.dumps(embedding_vector),
                metadata_json=json.dumps({"chunk_index": i, "content_preview": chunk[:100]})
            )
            db.add(embedding_record)

        db.commit()
        return True

    def get_relevant_context(self, db: Session, query: str, module_id: Optional[int] = None, chapter_id: Optional[int] = None):
        """Get relevant context from textbook content"""
        # If specific chapter is requested, use only that chapter
        if chapter_id:
            if chapter_id not in self.vector_stores:
                self.create_embeddings_for_chapter(db, chapter_id)

            vector_store = self.vector_stores.get(chapter_id)
            if vector_store:
                docs = vector_store.similarity_search(query, k=4)
                return " ".join([doc.page_content for doc in docs])

        # If specific module is requested, combine all chapters in the module
        elif module_id:
            # Get all chapters in the module
            chapters = db.query(Chapter).filter(Chapter.module_id == module_id).all()
            context_parts = []

            for chapter in chapters:
                if chapter.id not in self.vector_stores:
                    self.create_embeddings_for_chapter(db, chapter.id)

                vector_store = self.vector_stores.get(chapter.id)
                if vector_store:
                    docs = vector_store.similarity_search(query, k=2)
                    context_parts.extend([doc.page_content for doc in docs])

            return " ".join(context_parts[:4])  # Limit to 4 chunks

        # If no specific module/chapter, search across all content
        else:
            all_context = []
            all_chapters = db.query(Chapter).all()

            for chapter in all_chapters:
                if chapter.id not in self.vector_stores:
                    self.create_embeddings_for_chapter(db, chapter.id)

                vector_store = self.vector_stores.get(chapter.id)
                if vector_store:
                    docs = vector_store.similarity_search(query, k=1)
                    all_context.extend([doc.page_content for doc in docs])

            # Return top relevant chunks
            return " ".join(all_context[:6])  # Limit to 6 chunks

    def generate_response(self, db: Session, query: str, module_id: Optional[int] = None, chapter_id: Optional[int] = None):
        """Generate a response using RAG"""
        # Get relevant context
        context = self.get_relevant_context(db, query, module_id, chapter_id)

        if not context.strip():
            return "I don't have enough information in the textbook to answer that question. Please refer to the relevant chapters in the Physical AI & Humanoid Robotics textbook."

        # Create a QA chain
        from langchain.chains import LLMChain
        qa_chain = LLMChain(llm=self.llm, prompt=self.qa_prompt)

        # Generate response
        response = qa_chain.run(question=query, context=context)
        return response

    def create_chat_session(self, db: Session, user_id: Optional[int] = None, title: str = "New Chat"):
        """Create a new chat session"""
        session = ChatSession(
            user_id=user_id,
            session_title=title
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def add_message_to_session(self, db: Session, session_id: int, sender_type: str, content: str):
        """Add a message to a chat session"""
        message = ChatMessage(
            session_id=session_id,
            sender_type=sender_type,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_session_history(self, db: Session, session_id: int):
        """Get chat history for a session"""
        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp).all()
        return messages

    def chat(self, db: Session, user_id: Optional[int], chat_request: ChatRequest):
        """Main chat method that handles the entire flow"""
        # Create or get session
        if chat_request.session_id:
            session_id = chat_request.session_id
        else:
            # Create new session
            session_title = f"Chat about {chat_request.message[:50]}..." if len(chat_request.message) > 50 else chat_request.message
            session = self.create_chat_session(db, user_id, session_title)
            session_id = session.id

        # Add user message to session
        user_message = self.add_message_to_session(
            db, session_id, "user", chat_request.message
        )

        # Generate AI response using RAG
        ai_response = self.generate_response(
            db,
            chat_request.message,
            chat_request.module_id,
            chat_request.chapter_id
        )

        # Add AI message to session
        ai_message = self.add_message_to_session(
            db, session_id, "assistant", ai_response
        )

        # Return response
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            message_id=ai_message.id
        )


# Global instance of the RAG chat service
rag_service = RAGChatService()