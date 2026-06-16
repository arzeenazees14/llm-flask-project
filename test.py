from llm_processor import generate_product_json

user_input = input("Enter product description: ")

result = generate_product_json(user_input)

print(result)