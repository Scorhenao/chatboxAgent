import google.generativeai as genai
from config import get_gemini_api_key

genai.configure(api_key=get_gemini_api_key())

print("\n==== MODELOS DISPONIBLES PARA TU KEY ====\n")
for m in genai.list_models():
    print(m.name)
