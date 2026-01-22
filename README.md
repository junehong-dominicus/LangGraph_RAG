# LangChain, RAG, and LangGraph

## 1. LangChain
**The Framework for LLM Applications**

LangChain is an open-source framework designed to simplify the development of applications powered by Large Language Models (LLMs) like GPT-4, Claude, or Llama. It provides the "glue" code necessary to connect LLMs to other data sources and computational tools.

## The repository has been moved. You can now find it at:  
## https://github.com/junehong-dominicus/automated_blog_content_pipeline

- **Core Philosophy**: LLMs are powerful but isolated. They don't know about your private data, they can't take actions (like sending emails), and they don't have memory of past conversations by default. LangChain solves this.
- **Key Components**:
  - **Chains**: Sequences of calls (e.g., Prompt → LLM → Output Parser).
  - **Prompts**: Templates to manage and optimize inputs to the model.
  - **Tools**: Interfaces that allow LLMs to interact with the outside world (Google Search, Calculators, APIs).
  - **Memory**: Components to persist state between calls of a chain/agent.

## 2. RAG (Retrieval-Augmented Generation)
**The Architecture for Knowledge**

RAG is not a library, but a technique or architectural pattern used to improve the accuracy and reliability of LLM models with facts fetched from external sources.

- **The Problem**: LLMs can hallucinate and their training data is cut off at a specific date. They don't know your company's internal documents.
- **The Solution**: Instead of relying solely on what the model "memorized" during training, RAG retrieves relevant information and feeds it to the model at runtime.
- **The Workflow**:
  1. **Retrieval**: When a user asks a question, the system searches a knowledge base (often using a Vector Database) for relevant text chunks.
  2. **Augmentation**: These chunks are pasted into the system prompt as context (e.g., "Answer the user's question using the following context: ...").
  3. **Generation**: The LLM generates an answer based on the retrieved facts.

## 3. LangGraph
**The Orchestration for Agents**

LangGraph is a library built on top of LangChain specifically designed to build stateful, multi-actor applications and agents.

- **The Shift from Chains to Graphs**:
  - Standard **LangChain Chains** are typically Directed Acyclic Graphs (DAGs). They flow linearly: Step A → Step B → Step C.
  - **LangGraph** models applications as Graphs with Cycles (loops). This is critical for agentic behaviors where an AI needs to try something, check the result, and potentially try again or take a different path based on the result.
- **Key Concepts**:
  - **State**: A shared data structure (like the `VideoState` in your project) that persists across steps.
  - **Nodes**: Functions that perform work (e.g., "Generate Script").
  - **Edges**: Logic that defines where to go next (e.g., "If error, go to Retry; else go to Upload").
- **Why it matters**: It allows for complex control flow like loops, conditional branching, and persistence, which are difficult to manage in simple linear chains.

## Summary: How They Fit Together

| Concept | Role | Analogy |
| :--- | :--- | :--- |
| **LangChain** | **The Toolbox** | The hammer, nails, and wood used to build the structure. |
| **RAG** | **The Reference Library** | The encyclopedia the builder looks up to verify facts before building. |
| **LangGraph** | **The Site Manager** | The coordinator who decides what to build next, checks quality, and orders rework (loops) if something fails. |