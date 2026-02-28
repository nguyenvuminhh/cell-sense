# CellSense: AI-Powered Google Sheets Assistant

## Basic Information
- **Project Title:** AI-Powered Google Sheets Assistant (CellSense)
- **Student Name:** Vu Minh Nguyen
- **Student ID:** 101676647
- **Advisor:** Leinonen Juho
- **Course:** ELEC-C0302 - Final Project in Digital Systems and Design
- **Duration:** Period II - Period III, 2025-2026
- **Running instance:** https://docs.google.com/spreadsheets/d/13uBCmtwEhp2BgL4xUM2KJt6KaRRpQXA5cPOytErKHkw/edit?gid=0#gid=0
---

## 1. Introduction

### 1.1 Problem

Google Sheets is a popular tool for statistics, data analysis, management, etc. It is widely used in many fields by people from different backgrounds. Therefore, many people find it difficult to remember complex syntax for formulas. To address this issue, this project developed an AI-powered assistant that integrates with Google Sheets to help users perform these tasks more efficiently by leveraging large language models (LLMs) to assist in generating formulas.

### 1.2 Objectives

The goal of this project is a functional Google Sheets add-on that allows users to interact with an AI assistant. The final version should be capable of:
- Generating formulas according to the user's instructions.
- Allowing users to attach cell contents as context for the AI assistant.
- Attaching previous messages in the chat as context for multi-turn conversations.
- Editing multiple cell ranges in one request.
- Supporting multiple LLM providers (Google, OpenAI , Anthropic).
- Allowing users to input their own API keys for their preferred LLM provider.
- Having user tiers: free users with a limited daily quota using the system API key, and users with their own API keys and no usage limits.
- Having user management, chat management, and authentication.
- Evaluating the performance of different LLM models on formula generation tasks. Incapable models are removed.

---

## 2. System Architecture

### 2.1 High-Level Overview

After receiving the user's request, the frontend (a Google Apps Script written in HTML and TypeScript) forwards it to the backend (a FastAPI server hosted on GCP Cloud Run). The backend then queries the database (a PostgreSQL database hosted on GCP Cloud SQL) and call to LLM providers' API (Google, OpenAI , Anthropic). After receiving and processing responses from the database and the LLM providers, the backends send the formulas with the explanation to the frontend. The frontend then displays the explanation and apply the formulas to the target cells.

### 2.2 Frontend — Google Apps Script

The frontend is a Google Apps Script add-on written in TypeScript, embedded directly into Google Sheets as a sidebar. It is managed as a separate Git submodule at `./google_apps_script/`.

#### 2.2.1 Project Structure

```
google_apps_script/
├── dist/                    # Build output (generated, pushed to Apps Script)
│   ├── Code.js              # Bundled entry point
│   └── html/                # HTML templates (copied from src/html/)
├── src/                     # Source code
│   ├── config.ts            # Configurations
│   ├── types.ts             # Auto-generated types from backend OpenAPI schema
│   ├── html/                # HTML templates for sidebar UI
│   ├── services/            # Service layer
│   └── other .ts files
├── scripts/                 # Build helper scripts
└── package.json             # Dependencies (esbuild, eslint, typescript)
```
#### 2.2.2 Build Pipeline

The TypeScript source is bundled and deployed to Google Apps Script using `esbuild` and `clasp`:

1. **Type generation** — `openapi-typescript` generates `types.ts` from the backend's OpenAPI schema (`make export_openapi_types`), keeping frontend types in sync with the backend.
2. **Bundle** — `esbuild` bundles all TypeScript into a single `dist/Code.js`.
3. **Post-process** — Custom scripts strip ES module `export` statements (not supported by Apps Script) and replace the API URL placeholder with the actual backend URL.
4. **Copy assets** — HTML templates and `appsscript.json` manifest are copied to `dist/`.
5. **Deploy** — `clasp push` uploads the `dist/` directory to the Apps Script project.


#### 2.2.3 Tabs

The frontend provides three sidebar views, accessible from the "CellSense" menu in Google Sheets:

- **Chat Interface** (`chat_interface.html`) — Main conversation view with message input, LLM model selector, "Select Context" / "Add Target" buttons for attaching cell ranges, and a "Revert Edit" button to undo applied formulas.

- **Chat History** (`chat_list.html`) — Lists previous chat sessions with titles and timestamps. Users can open a chat or create a new one.

- **Profile** (`profile.html`) — Shows account info, API key management (set/change/delete) for each provider, and remaining free quota.

### 2.3 Backend — FastAPI

#### 2.3.1 Project Structure

```
server/
├── main.py                # FastAPI app, middleware registration, health endpoints
├── config.py              # Environment variables and constants
├── constants.py           # Enums (LLMProviders, LLMModels, ChatRoles)
├── routers/               # API endpoint handlers. Call service layer
├── services/              # Business logic. Call CRUD layer
├── crud/                  # Database operations (SQLAlchemy)
├── middleware/            # Request verification and processing
├── prompts/               # Jinja2 prompt templates
└── utils/                 # Helper functions
```

#### 2.3.2 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Health check |
| `GET` | `/supported-models` | List available LLM models |
| `POST` | `/chat/new` | Create a new chat session |
| `GET` | `/chat/list` | Get user's chat sessions |
| `GET` | `/chat/{chat_id}/messages` | Get messages in a chat |
| `POST` | `/chat/{chat_id}/send-message` | Send message and receive AI response |
| `GET` | `/user/me` | Get current user info |
| `GET` | `/user/quota` | Get free tier quota |
| `PATCH` | `/user/api-key` | Update personal API keys |

### 2.4 Database Schema

<!-- Describe the PostgreSQL schema managed by Alembic migrations -->

| Table | Description |
|-------|-------------|
| `users` | Manage users (their emails and API keys)|
| `chats` | Manage chats of the users |
| `chat_messages` | Manage messages within chats |
| `free_user_quota` | Daily free request quota tracking |
| `system_api_key_usage` | System API key daily usage limits |

![alt text](./assets/9_schema.png)

### 2.5 Cloud Infrastructure
- Google Cloud Platform (GCP) is used for hosting the backend and database.
- Resources:
    - **Google Cloud Run** is used for serverless deployment of the FastAPI backend. It is also used for CI/CD deployment's jobs (migrating database schema).
    - **Google Container Registry** is used for storing Docker images. Cloud Run pulls from the Container Registry to deploy the backend.
    - **Google Cloud SQL for PostgreSQL** is used to store user data and chat history.
    - **Google Apps Script** is used for the frontend, deployed as a Google Sheets add-on. The production Apps Script is binded to a Google Sheets document, allowing everyone to use the app via that document.
---

## 3. LLM Integration

### 3.1 Supported Models

| Provider | Models |
|----------|--------|
| Google Gemini | gemini-2.5-pro, gemini-2.5-flash |
| OpenAI GPT | gpt-5, gpt-5-mini |
| Anthropic Claude | claude-opus-4-5, claude-haiku-4-5 |

### 3.2 Structured Input

Input prompts are managed using Jinja2 templates stored in `server/prompts/`. Jinja2 is a templating engine that allows embedding placeholders (e.g., `{{ variable }}`) and control structures (e.g., `{% for %}` loops) inside text files. At runtime, these placeholders are replaced with actual data from a json input, producing the final prompt string sent to the LLM. This separates prompt logic from application code, making it easy to iterate on prompt design without modifying the service layer.

The main prompt template (`llm_request_prompt.md`) defines the LLM's role as a "spreadsheet reasoning agent". It receives a JSON as input:

```json
{
  "decoded_message": "<natural language instruction from the user>",
  "selected_ranges": [
    {
      "sheet_name": "<sheet name>",
      "range": "<A1 range>",
      "cell_values": "<2D array of cell values>"
    }
  ],
  "target_ranges": [
    {
      "sheet_name": "<sheet name>",
      "range": "<A1 range>",
      "cell_values": "<2D array of current cell values>"
    }
  ]
}
```

### 3.3 Structured Output

All models are instructed to return a JSON object with a fixed schema:

```json
{
  "message": "<natural language explanation>",
  "filled_ranges": [
    {
      "sheet_name": "<sheet name>",
      "range": "<A1 range>",
      "a1_value": "<formula or literal>"
    }
  ]
}
```


### 3.4 Conversation Context

To support multi-turn conversations, the backend attaches previous messages from the current chat session to each LLM request. When a user sends a new message, the service fetches up to 30 most recent messages from the database for that chat. These messages are prepended to the new user prompt before sending to the LLM. This allows the model to reference earlier instructions, follow up on previous formulas, and maintain coherent dialogue across multiple exchanges within a chat session.


## 4. User and API Key Management

Users are automatically created on their first API request. The `extract_user_from_request` middleware looks up the user by the email from the query. If no user exists, one is created automatically — there is no separate registration step.

Each user can optionally store personal API keys for Gemini, ChatGPT, and Claude. These keys are stored in the database and can be set, changed, or deleted from the Profile tab.

When a user sends a request, the API key is resolved depending on the chosen model.

- **Gemini models:** The system API key is used first (prioritized even when the user has a personal key). Each use decrements the user's daily free quota (10/day) and the system-wide daily limit (150/day). Only when the free quota is exhausted does the system fall back to the user's personal Gemini key. If neither is available, the request is rejected.
- **OpenAI / Anthropic requests:** There is no system key for these providers. The user must provide their own API key — otherwise the request is rejected with an error noting that only Gemini has free quota.

---

## 5. Security

### 5.1 Authentication with OpenID Connect (OIDC)

Authentication is handled using OpenID Connect (OIDC), a protocol built on top of OAuth 2.0.

The frontend (Apps Script) attaches an OIDC token of the effective user (the logged-in user) to all requests. OIDC is a JSON Web Token (JWT) signed by Google. The backend then decodes the JWT token and confirms the signature — at this point, we can confirm that the token has not been tampered with, and it is indeed issued by Google.

The body of the decoded token contains the effective user's email, audience (target client ID), and other fields. The effective user's email is used to create an account (if one does not already exist). The audience must match the OAuth client ID of the Apps Script — at this point, we can confirm that the token was issued for the Google Apps Script of our app, and we can authenticate the logged-in user.

### 5.2 Rejecting Old Requests

All requests older than 1 minute are rejected. This prevents replay/delay attacks, where an attacker could intercept a valid request and resend it at a later time.

---

## 6. Testing and Code Quality

Tests use `pytest` with `pytest-asyncio` for async support. A separate PostgreSQL 16 database runs via `docker-compose.test.yml`. Each test function gets a fresh database session that is rolled back after execution, ensuring test isolation. Tests are run with `make run_test`, which spins up the test database, runs migrations, executes all tests, and cleans up.

Code quality is enforced through pre-commit hooks: Ruff (linting), Pyright (type checking), Black (formatting), isort (import sorting), Bandit (security analysis), and detect-secrets (credential detection).

---
## 7 Model Evaluation

See evaluation/report.md.
