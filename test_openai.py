import openai

# Replace "your_token_here" with your actual token
openai.api_key = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDI4NjdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.XpHrh14WeVNBhnNg3zhL3VX0Ai__1MOIIcnLXPbuB1U"

try:
    # Test a basic ChatCompletion request
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello."}
        ],
        max_tokens=10
    )
    print("Response:", response)
except Exception as e:
    print("Error:", str(e))
