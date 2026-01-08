# Meeting Report - January 5, 2026

## Progress Since Last Meeting
- Deploy to production environment on Google Cloud Platform (GCP).
- Implement CI/CD pipelines for automated testing and deployment.
- Integrate additional LLM providers: OpenAI ChatGPT, Anthropic Claude.

## Deployment to Production on GCP
- The backend FastAPI server is now deployed to a production environment on Google Cloud Platform (GCP).
- Resources:
    - **Google Cloud Run** is used for serverless deployment of the FastAPI backend. It is also used for CI/CD deployment's jobs (migrating database schema).
    - **Google Container Registry (GCR)** is used for storing Docker images.
    - **Google Cloud SQL for PostgreSQL** is used to store user data and chat history.
    - **Google Apps Script** is used for the frontend, deployed as a Google Sheets add-on. The production Apps Script is binded to a Google Sheets document, allowing everyone to use the app via that document.

- There are now 2 separate environments: development and production.
    - Development environment is used for testing new features and bug fixes. The backend is hosted locally and exposed to the internet using ngrok. The frontend Apps Script is binded to a separate Google Sheets document. Each change is manually deployed to the development environment for testing.
    - Production environment is used for end-users. The backend is hosted on GCP Cloud Run, and the frontend Apps Script is binded to a separate Google Sheets document for public use.

## CI/CD Pipelines
- CI/CD pipelines are implemented using GitHub Actions.
- It is triggered on every PR or push to the main branch.

### Pipeline Steps for Backend
1. Run pre-commit checks (linting, formatting, type checking, etc.)
2. Run tests
3. Build and push Docker image to Google Container Registry (GCR)
4. Restart Cloud Run service so that it pulls the latest Docker image
5. Migrate traffic to the new revision
6. Migrate database schema using Alembic via a Google Cloud Run job

### Pipeline Steps for Frontend
1. Push code to Apps Script
2. Create a new version of the Apps Script project
3. Update the deployment to use the new version

## Integration of Additional LLM Providers
- Integrated OpenAI ChatGPT and Anthropic Claude as additional LLM providers.
- Users can now select which LLM provider to use for inference in the UI.
- Users can also input their own API keys for these LLM providers in the My Profile section of the UI.
- The system will use the user's provided API key if available; otherwise, it will use the system's API key. Note that system's API key usage is only available for Gemini models.

- Supported models:
    - Google Gemini: "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"
    - OpenAI ChatGPT: "gpt-5", "gpt-5-pro", "gpt-5-mini", "gpt-5-nano"
    - Anthropic Claude: "claude-haiku-4-5",
    "claude-sonnet-4-5", "claude-opus-4-5"

## Comparison between using Google Cloud Run vs Google Compute Engine for backend deployment
### Google Cloud Run (Current Approach)
#### Pros:
- Serverless: No need to manage servers or infrastructure.
- Automatic scaling: Scales up and down based on traffic.
- Does not charge for idle time, i.e., you only pay for the resources used during request processing.
#### Cons:
- Cold starts: May experience latency during cold starts when the service has been idle for a while.
- Limited customization: Less control over the underlying infrastructure compared to Compute Engine.

### Google Compute Engine
#### Pros:
- No cold starts: The server is always running, so there is no latency due to cold starts.
- Full control over the underlying infrastructure, allowing for more customization.
#### Cons:
- Requires managing servers and infrastructure.
- Manual scaling: Need to set up autoscaling or manually adjust instance counts.
- Charges for uptime, i.e., you pay for the instance being up regardless of traffic.

### For this project, Google Cloud Run is a better fit:
- Very few users (me and a couple of testers, e.g., my friends), so the app will have long idle times.
- The use case is not critical, so occasional cold starts are acceptable.
- Limited budget for hosting (300 USD of free GCP credits), so minimizing costs is important.

## Comparison between publishing the Google Sheets add-on vs sharing a Google Sheets document with the add-on installed
### Publishing the Add-on
#### Pros:
- Easier for users to find and install the add-on directly from the Google Workspace Marketplace.
- Users feel more comfortable using an add-on from the marketplace rather than using a shared document.
- Users have less concern about data privacy since the add-on is installed in their own documents.
- Users don't see Google's warning about using add-ons from unverified developers when installing from the marketplace.
#### Cons:
- The add-on will be available to all Google Sheets users via the Google Workspace Marketplace.
- Requires going through Google's review process, which can take a long time. The procedures are also very complicated, including preparing documents (Terms of Service, Privacy Policy, etc.), designing icons and images, setting up developer profile page (my own profile), etc.

### Sharing a Google Sheets Document with the Add-on Installed (Current Approach)
#### Pros:
- Quicker to set up and deploy since it only requires sharing a document link.
- No need to go through Google's review process.
#### Cons:
- Users may have concerns about data privacy since they are using a shared document.
- Less discoverable since users need to have the document link to access the add-on.
- Users see Google's warning about using add-ons from unverified developers when they open the document.
