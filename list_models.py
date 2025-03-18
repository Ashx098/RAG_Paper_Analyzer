import google.generativeai as genai

genai.configure(api_key="AIzaSyCNOT1X_kRDcsx6UOZFCWNAUqFao4ffK-4")  # Replace with your actual API key

models = genai.list_models()

print("\n📌 Available Gemini Models:")
for model in models:
    print(f"- {model.name}: {model.description}")
