# CellSense

AI-powered Google Sheets add-on that turns plain English into spreadsheet formulas.

> The hosted instance is currently down due to GCP billing. Screenshots below show what it looks like.

## Features

- Generate formulas from natural language
- Multi-turn chat with conversation history
- Attach cell ranges as context for the model
- Edit multiple ranges in a single request
- Pick from Gemini, GPT, or Claude models
- 10 free requests/day, or bring your own API key
- Revert the last set of applied formulas

## Supported Models

| Provider | Models |
|----------|--------|
| Google Gemini | `gemini-2.5-pro`, `gemini-2.5-flash` |
| OpenAI GPT | `gpt-5`, `gpt-5-mini` |
| Anthropic Claude | `claude-opus-4-5`, `claude-haiku-4-5` |

## Architecture

The frontend is a Google Apps Script sidebar in Google Sheets (TypeScript). It talks to a FastAPI backend that handles chat logic and LLM calls, with PostgreSQL for storage. Everything runs on GCP — Cloud Run for the backend, Cloud SQL for the database.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic, Jinja2
- **Frontend:** TypeScript, Google Apps Script
- **Database:** PostgreSQL
- **LLM SDKs:** google-genai, openai, anthropic
- **Infra:** GCP Cloud Run, Cloud SQL, Artifact Registry
- **Testing:** pytest, pytest-asyncio
- **Code quality:** Ruff, Pyright, Black, isort, Bandit, detect-secrets

## Evaluation

Nine models were tested on 9 sheets across 3 difficulty levels (Easy, Medium, Hard), 3 attempts each. Scored on consistency (do repeated attempts give the same correct answer?) and style (is the formula clean?).

Three models got dropped for bad results: Gemini 2.5 Flash Lite, GPT-5 Nano, and Claude Sonnet 4.5.

![Consistency results](evaluation/assets/consistency_result.png)

![Style results](evaluation/assets/style_result.png)

<details>
<summary>Test sheets used for evaluation</summary>

#### Easy

| | |
|---|---|
| ![E1](evaluation/assets/sheet_e1.png) | ![E2](evaluation/assets/sheet_e2.png) |
| **E1:** Sales revenue totals | **E2:** Student grade averages and pass/fail |

![E3](evaluation/assets/sheet_e3.png)

**E3:** Inventory stock value and reorder alerts

#### Medium

| | |
|---|---|
| ![M1](evaluation/assets/sheet_m1.png) | ![M2](evaluation/assets/sheet_m2.png) |
| **M1:** Employee bonus with VLOOKUP | **M2:** Order analysis with SUMIFS/COUNTIFS |

![M3](evaluation/assets/sheet_m3.png)

**M3:** Project duration and budget status

#### Hard

| | |
|---|---|
| ![H1](evaluation/assets/sheet_h1.png) | ![H2](evaluation/assets/sheet_h2.png) |
| **H1:** Financial metrics with running totals | **H2:** Tiered commission with lookup |

![H3](evaluation/assets/sheet_h3.png)

**H3:** Weighted scoring with ranking

</details>

## Database Schema

![Schema](docs/assets/9_schema.png)

## Screenshots

<table>
  <tr>
    <td><img src="docs/assets/4_error_and_info_messages.jpeg" alt="Chat UI" width="400"></td>
    <td><img src="docs/assets/5_loading_effect.png" alt="Loading state" width="300"></td>
  </tr>
  <tr>
    <td><em>Chat interface with error handling</em></td>
    <td><em>Loading while the model thinks</em></td>
  </tr>
  <tr>
    <td><img src="docs/assets/4_model_selection.png" alt="Model picker" width="300"></td>
    <td><img src="docs/assets/4_user_profile.png" alt="Profile page" width="300"></td>
  </tr>
  <tr>
    <td><em>Model picker</em></td>
    <td><em>Profile and API key management</em></td>
  </tr>
  <tr>
    <td><img src="docs/assets/5_allow_revert.png" alt="Revert feature" width="300"></td>
  </tr>
  <tr>
    <td><em>One-click revert</em></td>
  </tr>
</table>
