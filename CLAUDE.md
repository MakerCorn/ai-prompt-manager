# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Install dependencies:**
```bash
poetry install
```

**Run the application:**
```bash
python prompt_manager.py
```

**Docker build and run:**
```bash
docker build -t ai-prompt-manager .
docker run -p 7860:7860 ai-prompt-manager
```

## Architecture

This is a Gradio-based web application for managing AI prompts with a modular architecture:

### Core Components
- `prompt_manager.py` - Main application with Gradio UI and business logic
- `prompt_data_manager.py` - Database abstraction layer supporting both SQLite and PostgreSQL

### Database Architecture
The application uses a dual-database approach:
- **Default**: SQLite with local `prompts.db` file
- **Optional**: PostgreSQL via environment configuration
- Database selection controlled by `.env` file with `DB_TYPE` and connection parameters

### Key Features Architecture
- **Name-based prompt system**: All prompts require unique names for identification
- **Dual AI service configuration**: Separate configs for primary execution and prompt enhancement
- **Category-based organization**: Tree view display with category grouping
- **Enhancement system**: Uses different AI models to improve existing prompts

### Data Flow
1. `PromptDataManager` handles all database operations
2. `AIPromptManager` wraps data operations and adds AI service integration
3. Gradio interface functions bridge UI events to business logic
4. AI service calls support OpenAI, LM Studio, Ollama, and Llama.cpp APIs

## Database Configuration

Configure via `.env` file:
- SQLite: `DB_TYPE=sqlite` and `DB_PATH=prompts.db`
- PostgreSQL: `DB_TYPE=postgres` and `POSTGRES_DSN=connection_string`

## AI Service Integration

The application supports multiple AI services with unified interface:
- OpenAI-compatible (including LM Studio)
- Ollama native API
- Llama.cpp server API

Each service type has specific payload formatting in `call_ai_service()` method.