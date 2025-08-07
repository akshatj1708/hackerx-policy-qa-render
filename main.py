import os
import logging
import time
import re
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EXPECTED_BEARER_TOKEN = "612aeb3ebe9d63cfdb21e3f7d679fcebde54f7c1283c92b7937ea72c10c966af"
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "hackerx")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

app = FastAPI(
    title="Universal RAG System",
    description="Production-ready RAG system for all document types",
    version="6.0.0"
)

class HackRxRequest(BaseModel):
    documents: str = Field(..., description="URL to the PDF document")
    questions: List[str] = Field(..., description="List of questions to ask about the document")

class HackRxResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers corresponding to the questions")

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

# **GLOBAL MODELS - INITIALIZED ONCE**
embeddings_model = None
llm_model = None

def initialize_models():
    """Initialize models once at startup with memory optimizations"""
    global embeddings_model, llm_model
    if embeddings_model is None:
        # Use a smaller model and enable CPU offloading to reduce memory usage
        embeddings_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},  # Force CPU to save memory
            encode_kwargs={"normalize_embeddings": False}  # Disable normalization to save memory
        )
    if llm_model is None:
        llm_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.0,
            google_api_key=GOOGLE_API_KEY
        )
    return embeddings_model, llm_model

async def verify_token(auth_header: str = Security(api_key_header)):
    if auth_header is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing")
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer" or token != EXPECTED_BEARER_TOKEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication credentials")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header format")
    return token

def detect_document_type(documents: List) -> str:
    """Fast document type detection for adaptive processing"""
    sample_text = " ".join([doc.page_content[:300] for doc in documents[:3]]).lower()
    
    if any(term in sample_text for term in ["policy", "insurance", "premium", "coverage", "insured"]):
        return "insurance"
    elif any(term in sample_text for term in ["contract", "agreement", "clause", "whereas", "legal"]):
        return "legal"
    elif any(term in sample_text for term in ["system", "configuration", "technical", "specification"]):
        return "technical"
    elif any(term in sample_text for term in ["patient", "medical", "treatment", "diagnosis", "therapy"]):
        return "medical"
    else:
        return "general"

def optimized_document_processing(url: str) -> List:
    """Optimized document processing with targeted chunking"""
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        temp_file_path = "temp_policy.pdf"
        with open(temp_file_path, "wb") as temp_f:
            temp_f.write(response.content)

        loader = PyPDFLoader(temp_file_path)
        docs = loader.load()

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        # **OPTIMIZED CHUNKING PARAMETERS**
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=950,      # Sweet spot for context vs relevance
            chunk_overlap=175,   # Good boundary coverage
            separators=["\n\n", "\n", ". ", ".", " "],
            length_function=len,
        )
        
        split_docs = text_splitter.split_documents(docs)
        doc_type = detect_document_type(split_docs)
        
        logging.info(f"Document processed: {len(split_docs)} chunks, type: {doc_type}")
        return split_docs

    except Exception as e:
        if os.path.exists("temp_policy.pdf"):
            os.remove("temp_policy.pdf")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {e}")

def fast_vector_store(documents: List) -> PineconeVectorStore:
    """Optimized vector store creation"""
    logging.info("Creating vector store...")
    
    try:
        embeddings, _ = initialize_models()
        pc = Pinecone(api_key=PINECONE_API_KEY)

        existing_indexes = pc.list_indexes().names()
        
        # Smart index selection with fallback
        if PINECONE_INDEX_NAME not in existing_indexes:
            alternatives = ["hackerx", "bajajhackerx"]
            index_name = next((alt for alt in alternatives if alt in existing_indexes), existing_indexes[0] if existing_indexes else None)
            if not index_name:
                raise HTTPException(status_code=404, detail=f"No suitable index found. Available: {existing_indexes}")
            logging.info(f"Using alternative index: {index_name}")
        else:
            index_name = PINECONE_INDEX_NAME
        
        index = pc.Index(index_name)
        
        # **FAST VECTOR STORE CREATION** 
        vector_store = PineconeVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            index_name=index_name
        )

        logging.info("Vector store created successfully")
        return vector_store

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store error: {e}")

def universal_query_enhancement(question: str) -> str:
    """Universal query enhancement that works across all document types"""
    
    # **PATTERN-BASED ENHANCEMENT** (domain-agnostic)
    enhancement_patterns = {
        # Time-related queries
        r"(grace|due|deadline|period|duration|time|when)": "period duration time deadline timeframe due date",
        
        # Waiting/eligibility queries
        r"(waiting|wait|eligibility|eligible|qualify)": "waiting period duration eligibility eligible qualified requirements",
        
        # Coverage/inclusion queries  
        r"(coverage|cover|include|benefit)": "covered included benefits coverage eligible excluded",
        
        # Numerical/limit queries
        r"(limit|maximum|minimum|amount|percentage|rate|cost|fee)": "limit maximum minimum amount percentage rate cost fee charges",
        
        # Definition queries
        r"(what is|define|definition|meaning|means)": "definition means defined refers includes explanation",
        
        # Process/procedure queries
        r"(how to|process|procedure|steps|method)": "process procedure method steps requirements instructions",
        
        # Comparison queries
        r"(difference|compare|versus|vs|better)": "difference comparison versus compared contrast between",
        
        # Medical/treatment queries (adaptive)
        r"(treatment|therapy|medical|diagnosis)": "treatment therapy medical diagnosis care procedure",
        
        # Legal/contractual queries (adaptive)
        r"(contract|agreement|clause|legal|liability)": "contract agreement clause legal liability terms conditions",
        
        # Technical/system queries (adaptive)  
        r"(system|configuration|setup|technical)": "system configuration setup technical specification parameters"
    }
    
    enhanced_question = question
    for pattern, enhancement in enhancement_patterns.items():
        if re.search(pattern, question, re.IGNORECASE):
            enhanced_question = f"{question} {enhancement}"
            logging.info(f"Applied universal enhancement for pattern: {pattern}")
            break
    
    return enhanced_question

def improved_retrieval(question: str, vector_store: PineconeVectorStore) -> List:
    """Enhanced retrieval with universal query enhancement"""
    
    enhanced_q = universal_query_enhancement(question)
    
    # **OPTIMIZED RETRIEVAL PARAMETERS**
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}  # Balanced coverage vs speed
    )
    
    return retriever.invoke(enhanced_q)

def create_universal_chain(vector_store: PineconeVectorStore):
    """Universal RAG chain that works across document types"""
    
    _, llm = initialize_models()
    
    # **UNIVERSAL PROMPT TEMPLATE**
    prompt_template = """You are an expert document analyst. Extract precise information from the provided context across any document type.

UNIVERSAL INTERPRETATION RULES:
- Pay attention to conditional phrases like "other than", "except", "excluding", "unless"
- "Not covered other than X, Y" means X and Y ARE covered
- Look for exact numbers, percentages, time periods, amounts, and specific values
- Cross-reference information across multiple context sections
- Distinguish between what IS and ISN'T included/covered/applicable

SEARCH PRIORITIES (Universal):
- For time-related queries: Look for specific durations, deadlines, periods
- For numerical queries: Find exact amounts, percentages, limits, ranges
- For definitional queries: Check terms, conditions, definitions sections
- For procedural queries: Find step-by-step processes, requirements, methods
- For coverage/eligibility: Identify inclusions, exclusions, conditions

RESPONSE GUIDELINES:
- Provide specific details and exact values when found
- Reference document sections, clauses, or page numbers when available
- If information is incomplete, specify what partial information was found
- Be precise about conditions, limitations, and exceptions
- State confidence level based on evidence strength

CONTEXT:
{context}

QUESTION: {input}

DETAILED ANALYSIS:"""

    prompt = PromptTemplate.from_template(prompt_template)
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(vector_store.as_retriever(), document_chain)

    return retrieval_chain

async def process_questions_universally(questions: List[str], vector_store: PineconeVectorStore, rag_chain) -> List[str]:
    """Universal question processing for any document type"""
    
    answers = []
    
    for i, question in enumerate(questions, 1):
        start_time = time.time()
        
        try:
            # Enhanced retrieval with universal patterns
            relevant_docs = improved_retrieval(question, vector_store)
            
            # Generate answer
            response = rag_chain.invoke({"input": question})
            answer = response.get("answer", "Information not available in the provided context.")
            
            answers.append(answer)
            
            elapsed = time.time() - start_time
            logging.info(f"Question {i} processed in {elapsed:.2f}s")
            
        except Exception as e:
            logging.error(f"Error processing question {i}: {e}")
            answers.append("Error processing question.")
    
    return answers

@app.post("/hackrx/run", response_model=HackRxResponse, dependencies=[Depends(verify_token)])
async def run_submission(request: HackRxRequest):
    """Universal processing endpoint for any document type"""
    
    total_start = time.time()
    logging.info("Starting universal document processing...")
    
    try:
        # **PHASE 1: DOCUMENT SETUP**
        setup_start = time.time()
        documents = optimized_document_processing(request.documents)
        vector_store = fast_vector_store(documents)
        rag_chain = create_universal_chain(vector_store)
        setup_time = time.time() - setup_start
        
        # **PHASE 2: UNIVERSAL QUESTION PROCESSING**
        processing_start = time.time()
        answers = await process_questions_universally(request.questions, vector_store, rag_chain)
        processing_time = time.time() - processing_start
        
        total_time = time.time() - total_start
        
        logging.info(f"UNIVERSAL PROCESSING METRICS - Setup: {setup_time:.2f}s, Processing: {processing_time:.2f}s, Total: {total_time:.2f}s")
        logging.info(f"Throughput: {len(request.questions)/total_time:.2f} questions/second")
        
        return HackRxResponse(answers=answers)

    except Exception as e:
        total_time = time.time() - total_start
        logging.error(f"Processing failed after {total_time:.2f}s: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Universal RAG API - Works with any document type", 
        "version": "6.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Universal RAG System",
        "version": "6.0.0",
        "features": [
            "Works with any document type",
            "Pattern-based query enhancement", 
            "Optimized chunking (950/175)",
            "Smart retrieval (k=10)",
            "Universal prompting"
        ],
        "supported_documents": ["Insurance", "Legal", "Technical", "Medical", "General"],
        "target_performance": "70-75% accuracy with <50s latency"
    }

@app.post("/debug/document-analysis")
async def analyze_document(url: str):
    """Debug endpoint to analyze document characteristics"""
    try:
        documents = optimized_document_processing(url)
        doc_type = detect_document_type(documents)
        
        return {
            "document_type": doc_type,
            "total_chunks": len(documents),
            "chunk_size": 950,
            "chunk_overlap": 175,
            "sample_content": documents[0].page_content[:200] + "..." if documents else "No content",
            "processing_optimizations": "Universal pattern-based enhancement"
        }
    except Exception as e:
        return {"error": str(e)}

# **STARTUP INITIALIZATION**
@app.on_event("startup")
async def startup_event():
    """Initialize models at startup for fast processing"""
    logging.info("Initializing universal models at startup...")
    initialize_models()
    logging.info("Universal RAG system ready for any document type")

if __name__ == "__main__":
    print("🚀 Starting Universal RAG Server...")
    print("📊 Features: Works with ANY document type")
    print("🎯 Target: 70-75% accuracy, <50s latency")
    print("✨ Optimizations: Universal patterns + Smart chunking + Enhanced retrieval")
    print("📚 API documentation: http://localhost:8000/docs")
    print("💚 Health check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)