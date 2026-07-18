# Services

This folder contains external integrations that act as bridges outside of the FinSight AI ecosystem.

## LLM Gateway
The primary service is the `llm_gateway`, an abstraction layer built around `google-genai` and `instructor`. 
It ensures that the core agents are decoupled from the specific LLM provider, allowing seamless switching between Gemini and future models like Claude.
