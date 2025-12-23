# Meeting Report - November 24, 2025

## Progress Since Last Meeting
- Use past messages as context for LLM responses.
- Allow users to input their own API keys for LLM services.
- Implement free user quota management.
- Allow users to select model for inference.
- Fix Bug: Title generation prompt now uses the correct variable for user message.
- UI: Properly display error messages (e.g., out of quota, invalid API key) and info messages (e.g., added this range as target) instead of appending them to chat.

## Past Messages as Context
- When the user sends a message, the past messages (max 30) in the same chat are now used as context for LLM to generate response.
- The user's messages include the full prompt (template at `server/prompts/*md`), the selected ranges, together with the data of those ranges.
![alt text](./assets/4_full_prompt.png)
- The LLM's messages is in the form of stringified JSON.
![alt text](./assets/4_full_llm_response.png)

## User-provided API Keys and Free User Quota Management
- Each user now have 10 free requests quota per day, reset at midnight.
- If the user has remaining free quota, the system's API key will be used for LLM requests.
- If the user has exhausted their free quota, they can provide their own API key for LLM requests.
- If the user has exhausted their free quota and has not provided an API key, an error message will be shown in the UI.
- Note: The system will prioritize using the system API key if the user has remaining free quota, even if the user has provided their own API key.
- All the information are displayed in the My Profile section of the UI.
![alt text](./assets/4_user_profile.png)

## Model Selection
- The user can now select the model to use for inference before sending a message.
- The available models are listed in a dropdown menu.
![alt text](./assets/4_model_selection.png)

## Displaying Error and Info Messages in UI
- Error messages (e.g., out of quota, invalid API key) and info messages (e.g., added this range as target) are now properly displayed in the UI.
- Error messages are displayed in red text, while info messages are displayed in green text.
![alt text](./assets/4_error_and_info_messages.png)
