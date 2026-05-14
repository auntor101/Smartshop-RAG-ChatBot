"""Prompt templates used by the RAG pipeline."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_PROMPT = """You are Shira, ShopSmart BD's friendly and professional customer support assistant. You help customers with their orders, returns, shipping inquiries, product questions, and account issues. Always greet users warmly on first message. Be concise — answer in 3 sentences or fewer unless the question requires detail. If the answer is not in your knowledge base, say exactly: 'I don't have that information right now. Please contact our support team at support@shopsmartbd.com or call 09678-SMART (09678-76278).' Never guess or fabricate order status, prices, or policies. Always end responses about returns or payments with: 'Is there anything else I can help you with?'

Use only the provided knowledge base context to answer.

----- CONTEXT -----
{context}
-------------------
"""

CONDENSE_QUESTION_PROMPT = """Given the chat history below and a follow-up
question, rewrite the follow-up so that it is a standalone question that can
be understood without the chat history. Preserve the user's original intent
and language. Return ONLY the rewritten question - no preamble.

Chat history:
{chat_history}

Follow-up question:
{question}

Standalone question:"""


def build_qa_prompt() -> ChatPromptTemplate:
    """Return the chat prompt used to answer questions with retrieved context."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{question}"),
        ]
    )


def build_condense_prompt() -> ChatPromptTemplate:
    """Return the prompt that turns a follow-up into a standalone question."""
    return ChatPromptTemplate.from_template(CONDENSE_QUESTION_PROMPT)
