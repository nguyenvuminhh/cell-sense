# CellSense

AI assistant for Google Sheets — like GitHub Copilot, but for spreadsheets.

Cell-ense brings AI-powered assistance directly into Google Sheets, helping users write formulas, understand data, and automate spreadsheet workflows using natural language.

## 🚀 Overview

CellSense is an AI productivity tool designed to enhance Google Sheets with intelligent suggestions and contextual assistance. Inspired by GitHub Copilot, it allows users to interact with their spreadsheets conversationally, turning natural-language prompts into formulas, explanations, and automation logic.

The frontend runs as a Google Apps Script extension, built with HTML and JavaScript, and is embedded directly into Google Sheets. The backend is hosted on Google Cloud Platform (GCP) and acts as a secure API layer that connects the Sheets UI to multiple large language models.

## 🤖 AI Model Support
- Google Gemini: "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"
- OpenAI GPT: "gpt-5", "gpt-5-pro", "gpt-5-mini", "gpt-5-nano"
- Anthropic Claude: "claude-haiku-4-5", "claude-sonnet-4-5", "claude-opus-4-5"

The backend is designed to be model-agnostic, allowing flexible switching or expansion across AI providers.

## ✨ Features
- 🧠 Natural-language assistance inside Google Sheets
- 🧮 Formula generation and explanation
- 📊 Data analysis, summaries, and insights
- ⚙️ Spreadsheet workflow automation support
- 🤖 Multi-LLM backend architecture
- ☁️ Secure, scalable backend hosted on GCP

## 🧩 Architecture
```
Google Sheets
(HTML + JS via Apps Script)
        │
        ▼
   GCP-Hosted Backend API
        │
        ▼
   AI Providers
    ├── Gemini
    ├── ChatGPT
    └── Claude
```
## 🛠 Tech Stack
- Frontend: Google Apps Script (HTML + JavaScript)
- Backend: Python-based API (hosted on GCP)
- AI Services: Gemini, ChatGPT, Claude
- Cloud Platform: Google Cloud Platform

## 🧪 Test Instance

Testing instance is available at https://docs.google.com/spreadsheets/d/13uBCmtwEhp2BgL4xUM2KJt6KaRRpQXA5cPOytErKHkw/edit?usp=drivesdk. As the project is still under development (TBD), please grant all requested permissions when prompted. For your assurance and to avoid affecting existing data or settings, it is recommended to use a brand-new Google account when accessing the testing instance.
