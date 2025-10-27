# Digital Systems and Design Final Project Plan

## Basic Information
- **Project Title:** AI-Powered Google Sheets Assistant
- **Student Name:** Vu Minh Nguyen
- **Student ID:** 101676647
- **Advisor:** Leinonen Juho

## Introduction
Google Sheets is a widely used tool for data organization, analysis, and collaboration. However, many users struggle with complex formulas, data manipulation, and automation tasks. The goal of this project is to develop an AI-powered assistant that integrates with Google Sheets to help users perform these tasks more efficiently by leveraging large language models (LLMs) to aid users in generating formulas.

## Expected Outcome
The expected outcome of this project is a functional Google Sheets add-on that allows users to interact with an AI assistant. The assistant will be capable of understanding user queries and attached data ranges and generating appropriate formulas.

The project will be consist of the following components:
1. Google Apps Script for frontend
2. FastAPI backend, hosted on Google Cloud Platform
3. PostgreSQL database for storing user data and chat history, hosted on Google Cloud Platform
4. LLM providers (e.g., Google Gemini, OpenAI ChatGPT, or Anthropic Claude) for natural language processing and formula generation.

## Task Breakdown

### Product Development Tasks
1. Make a simple frontend using Google Apps Script that can send user queries and selected data ranges to the backend.
2. Set up a simple FastAPI backend that can receive requests from the frontend, process them.
3. Integrate a LLM provider (Google Gemini) into the backend to handle natural language processing and formula generation.
4. Implement user management and chat management using PostgreSQL database.
5. Implement authorization and authentication (RBAC or Linux model) for secure access to the backend. Implement user tiers. Free user can use system's API key with limited usage and models, while paid user can use their own API key with no limit regarding usage or model.
6. Implement chat session management and attach history to LLM requests for better context.
7. Integrate additional LLM providers (OpenAI ChatGPT, Anthropic Claude), and allow user to input their own API keys.
8. Do prompt engineering to improve the quality of generated formulas.
9. Polishing the frontend, with better error display, loading effects, etc. Allow user to reject changes suggested by the AI assistant.
10. Testing and debugging the entire system to ensure reliability and performance.
More tasks/features may be added as the project progresses.

### Logistics Tasks
1. Implement test cases for backend API endpoints.
2. Set up continuous integration and deployment (CI/CD) pipelines for automated testing and deployment.
3. Prepare project documentation, including user guides and technical documentation.
4. Regular meetings with advisor for progress updates and feedback.
5. Final project report and presentation preparation.

## Project Management and Documentation
- The project code base will be managed using Git and hosted on GitHub.
- Documentation will be maintained in a dedicated `docs/` directory within the repository.
- Meetings with advisor will be held bi-weekly to discuss progress, challenges, and next steps.
- There will be a project report for each meeting summarizing progress and any issues encountered.
- There will be a final project report and presentation/demo at the end of the semester.
