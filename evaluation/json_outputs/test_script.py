# """
# Repeatability Evaluation Test Script

# Runs each evaluation task (e1-e3, m1-m3, h1-h3) against all 10 LLM models,
# 3 times each, to evaluate formula generation repeatability.
# """

# import asyncio
# import json
# import os
# import sys
# from pathlib import Path

# import dotenv

# import server.routers.chat_router  # noqa: F401
# from server.constants import JinjaPromptTemplatesNames, LLMModels, LLMProviders
# from server.models.message_models import MessageRequest, MessageResponse
# from server.services.llm_service import generate_response

# # Add project root to sys.path for imports
# PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# sys.path.insert(0, str(PROJECT_ROOT))

# dotenv.load_dotenv(".env")

# # Set dummy DATABASE_URL to prevent import errors (not used in this script)
# if "DATABASE_URL" not in os.environ:
#     os.environ["DATABASE_URL"] = "DATABASE_URL"

# # Configuration
# MODELS_TO_TEST = [
#     (LLMProviders.GOOGLE, LLMModels.GOOGLE_GEMINI_2_5_FLASH),
#     (LLMProviders.GOOGLE, LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE),
#     (LLMProviders.GOOGLE, LLMModels.GOOGLE_GEMINI_2_5_PRO),
#     (LLMProviders.OPENAI, LLMModels.OPENAI_GPT_5),
#     (LLMProviders.OPENAI, LLMModels.OPENAI_GPT_5_PRO),
#     (LLMProviders.OPENAI, LLMModels.OPENAI_GPT_5_MINI),
#     (LLMProviders.OPENAI, LLMModels.OPENAI_GPT_5_NANO),
#     (LLMProviders.ANTHROPIC, LLMModels.ANTHROPIC_CLAUDE_HAIKU_4_5),
#     (LLMProviders.ANTHROPIC, LLMModels.ANTHROPIC_CLAUDE_SONNET_4_5),
#     (LLMProviders.ANTHROPIC, LLMModels.ANTHROPIC_CLAUDE_OPUS_4_5),
# ]

# RUNS = ["first", "second", "third"]

# INPUT_DIR = PROJECT_ROOT / "evaluation" / "raw_json_inputs"
# OUTPUT_DIR = PROJECT_ROOT / "evaluation" / "repeatability_evalution" / "results"

# INPUT_FILES = [
#     "e1_request.json",
#     "e2_request.json",
#     "e3_request.json",
#     "m1_request.json",
#     "m2_request.json",
#     "m3_request.json",
#     "h1_request.json",
#     "h2_request.json",
#     "h3_request.json",
# ]


# def load_api_keys() -> dict[str, str]:
#     """Load API keys from environment variables."""
#     keys = {
#         "google": os.environ.get("GEMINI_API_KEY", ""),
#         "openai": os.environ.get("CHATGPT_API_KEY", ""),
#         "anthropic": os.environ.get("CLAUDE_API_KEY", ""),
#     }
#     missing = [k for k, v in keys.items() if not v]
#     if missing:
#         raise ValueError(f"Missing API keys for: {', '.join(missing)}")
#     return keys


# def get_api_key_for_provider(
#     provider: LLMProviders, api_keys: dict[str, str]
# ) -> str:
#     """Get the appropriate API key for a provider."""
#     if provider == LLMProviders.GOOGLE:
#         return api_keys["google"]
#     elif provider == LLMProviders.OPENAI:
#         return api_keys["openai"]
#     elif provider == LLMProviders.ANTHROPIC:
#         return api_keys["anthropic"]
#     else:
#         raise ValueError(f"Unknown provider: {provider}")


# def extract_formulas(response_text: str) -> dict[str, str]:
#     """Parse JSON response and return {range: formula} dict."""
#     try:
#         data = json.loads(response_text)
#         formulas = {}
#         if "filled_ranges" in data:
#             for item in data["filled_ranges"]:
#                 range_key = item.get("range", "")
#                 formula = item.get("a1_value", "")
#                 formulas[range_key] = formula
#         return formulas
#     except json.JSONDecodeError as e:
#         print(f"  Error parsing JSON response: {e}")
#         return {"error": str(e)}


# async def run_tests():
#     """Main loop: for each input file, for each model, run 3 times."""
#     # Ensure output directory exists
#     OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

#     # Load API keys
#     api_keys = load_api_keys()

#     for input_file in INPUT_FILES:
#         input_path = INPUT_DIR / input_file
#         task_name = input_file.replace("_request.json", "")
#         output_file = OUTPUT_DIR / f"{task_name}_results.json"

#         print(f"\n{'='*60}")
#         print(f"Processing: {input_file}")
#         print(f"{'='*60}")

#         # Load input JSON
#         with open(input_path, "r") as f:
#             input_data = json.load(f)

#         # Results for this input file
#         results: dict[str, dict[str, dict[str, str]]] = {}

#         for provider, model in MODELS_TO_TEST:
#             model_name = model.value
#             print(f"\n  Model: {model_name}")
#             results[model_name] = {}

#             # Create MessageRequest with current provider/model
#             input_data["llm_provider"] = provider.value
#             input_data["llm_model"] = model.value
#             message_request = MessageRequest(**input_data)

#             # Get the appropriate API key
#             api_key = get_api_key_for_provider(provider, api_keys)

#             for run in RUNS:
#                 print(f"    Run: {run}...", end=" ", flush=True)
#                 try:
#                     # Call generate_response with session=None and chat_id=None
#                     response = await generate_response(
#                         session=None,  # type: ignore
#                         message_request=message_request,
#                         template_name=JinjaPromptTemplatesNames.LLM_REQUEST_PROMPT,
#                         response_schema=MessageResponse,
#                         api_key=api_key,
#                         chat_id=None,
#                     )
#                     formulas = extract_formulas(response.full_model_response)
#                     results[model_name][run] = formulas
#                     print("OK")
#                 except Exception as e:
#                     print(f"ERROR: {e}")
#                     results[model_name][run] = {"error": str(e)}

#             # Save partial results after each model (in case of failures)
#             with open(output_file, "w") as f:
#                 json.dump(results, f, indent=2)

#         print(f"\nResults saved to: {output_file}")

#     print("\n" + "=" * 60)
#     print("All tests completed!")
#     print("=" * 60)


# if __name__ == "__main__":
#     asyncio.run(run_tests())
