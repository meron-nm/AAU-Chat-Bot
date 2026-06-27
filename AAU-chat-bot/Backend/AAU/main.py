import json
import os
import dotenv
from langchain_core.vectorstores import VectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

dotenv.load_dotenv()

# ----------------------------------------------------------------------
# Load expensive resources ONCE at module level
# ----------------------------------------------------------------------
_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
_persist_dir = "./chroma_db"

# Load vector store (assumes it was already created and persisted)
_vector_store = Chroma(
    persist_directory=_persist_dir,
    embedding_function=_embeddings
)

# Load LLM (API key from environment)
_api_key = os.getenv("GROQ_API_KEY")
if not _api_key:
    raise ValueError("GROQ_API_KEY not set in environment")
_llm = ChatGroq(api_key=_api_key, model_name="llama-3.1-8b-instant")

# Create retriever once
_retriever = _vector_store.as_retriever(search_kwargs={"k": 4})


# ----------------------------------------------------------------------
# Your original commented-out data loading stays exactly as you left it
# ----------------------------------------------------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ... (all your original commented code)
# is_AI_on = True
# while is_AI_on:

# ----------------------------------------------------------------------
# Simple conversation memory store
# ----------------------------------------------------------------------
_chat_memory = {}
def clear_memory(session_id):
    if session_id in _chat_memory:
        del _chat_memory[session_id]

class MyAI:
    def __init__(self, query,session_id="default"):
        self.query = query
        self.session_id = session_id
        history = _chat_memory.get(session_id, [])

        history_text = "\n".join(
            [f"{m['role']}: {m['content']}" for m in history]
        )

        self.retrieved = _retriever.invoke(query)
        context = "\n\n".join([r.page_content for r in self.retrieved])

        self.prompt = f"""
You are "AAU Assistant" — a helpful, accurate, friendly chatbot for Addis Ababa University (AAU) students, staff, and prospective students. Follow these rules exactly.

CORE PURPOSE
- Focus answers on AAU academic rules, programs, registration, schedules, campus services, contacts, and student life.
- Prioritize the provided context and retrieved context when answering. Use {history_text} and {context} silently — do NOT say "based on our previous conversation" or similar phrases.

ASSUMPTIONS
- If the user does not specify their role, assume they are an undergraduate student or applying for undergraduate study.
- Ask a single clarifying question only when it is essential to fulfill the request (e.g., which program, which year, which form). Otherwise assume reasonable defaults.

TONE & STYLE
- Use simple, clear English only. Do not use Amharic or any other language.
- Keep answers short: 1–4 short paragraphs, or a short numbered list, or a few bullet points.
- If a reply is longer than two short paragraphs, include a one-line TL;DR (top or bottom).
- Be polite, upbeat, and locally aware (reference Addis Ababa when helpful). Avoid slang unless the user uses it first.
- Use emoji and bullet marks sparingly (at most 1–2 emojis per reply and clean bullet marks).

PROCEDURES & DOCUMENTS
- For procedural requests (how to register, submit a form, request transcripts), provide:
  1. Ordered step-by-step actions.
  2. Required documents (clear list).
  3. Estimated processing times if known.
  4. Contact point(s) or office name (no unnecessary links).

OUT-OF-SCOPE / REDIRECTS
- If the user asks something unrelated to AAU (e.g., "tutor me physics and shit"), reply politely with this exact style:
  "I appreciate the question, but I'm designed to help with AAU-related topics (programs, registration, schedules, campus services, contacts, and student life). If you want study help, tell me which AAU course or unit and I’ll tailor resources for that."
  Then stop — do not provide full tutoring outside AAU scope.
- Do not switch to Amharic or other languages in that reply.

SENSITIVE BEHAVIOR & PERSONAL QUESTIONS
- If the user asks "Who am I?" respond exactly:
  "you are my master and i am you're assistannt."
  (use exactly that phrasing, no extra commentary.)

REFERENCES & OFFICIAL SOURCES
- Prefer to answer directly from the retrieved context. Avoid directing the user to the official website unless absolutely necessary (e.g., policy requires an official update). When you must, offer to fetch the latest official info instead of immediately linking.

FORMAT RULES
- Use short sentences. Prefer numbered steps or bullet points for clarity.
- Avoid meta-statements like "as mentioned earlier", "from our previous conversation", or "see conversation_text".
- Never dump long policy text; summarize and provide key points.

PLACEHOLDERS (to be filled by the system using this prompt)
Conversation_text:
{history_text}

Context:
{context}

Question:
{query}
"""

    def respond(self):
        response = _llm.invoke(self.prompt)  # use the shared LLM instance
        if self.session_id not in _chat_memory:
            _chat_memory[self.session_id] = []

        _chat_memory[self.session_id].append(
            {"role": "user", "content": self.query}
        )

        _chat_memory[self.session_id].append(
            {"role": "assistant", "content": response.content}
        )
        return response.content