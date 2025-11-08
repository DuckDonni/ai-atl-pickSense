"""
Helper script to list available Gemini models.
Run this if you need to see what models are available.
"""
import google.generativeai as genai

genai.configure(api_key="AIzaSyBEMwJNKQrZbkpvGGKL-4wng0qDO_dAsQU")

print("Available Gemini models:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print()

