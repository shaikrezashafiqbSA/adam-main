#%%
import json
import re

# def json_search(response_string):
#     # Regex to extract JSON data, else return the response string
#     json_match = re.search(r'{\n(.*?)\n}', response_string, re.DOTALL)
#     try: 
#         json_data = json.loads(response_string)
#         return(json_data)
#     except Exception as e:
#         if json_match:
#             json_string = json_match.group(1).strip()  # Extract matched JSON string
#             json_data = json.loads("{"+f"{json_string}"+"}")
#             return(json_data)
#         else:
#             return(response_string)
        
import json
import warnings

def json_search(string: str):
    start_index = string.find("```json")
    if start_index == -1:
        return string
    start_index += len("```json")
    end_index = string.find("```", start_index)
    if end_index == -1:
        return string
    json_string = string[start_index:end_index].strip()
    json_string = json_string.replace(",\n    ]", "\n    ]") # remove trailing comma
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        warnings.warn(f"JSONDecodeError: {e}")
        return string
    
#%%
if __name__ == "__main__":
    string = "```json\n{\n    \"name\": \"Nasi Lemak\",\n    \"description\": \"Nasi Lemak is a popular Malay rice dish that is made with coconut milk, pandan leaves, and rice. It is typically served with chicken, eggs, peanuts, and cucumbers. Nasi Lemak is a relatively healthy dish that is low in calories and fat. It is a good source of protein and fiber.\",\n    \"serving_size\": \"250g\",\n    \"ingredients\": [\n        \"2 cups basmati rice\",\n        \"1 can (14 ounces) coconut milk\",\n        \"1 pandan leaf, tied in a knot\",\n        \"1/2 teaspoon salt\",\n        \"1/2 teaspoon ground turmeric\",\n        \"1/2 teaspoon ground cumin\",\n        \"1/4 teaspoon ground coriander\",\n        \"1/4 teaspoon black pepper\",\n        \"1/4 cup chopped peanuts\",\n        \"1 hard-boiled egg, sliced\",\n        \"1 cucumber, sliced\",\n        \"1 chicken thigh, cooked and shredded\"\n    ],\n    \"nutrition_per_serving\": {\n        \"calories\": 350,\n        \"fat\": 10g,\n        \"carbohydrates\": 45g,\n        \"protein\": 15g\"\n    },\n    \"recipe_per_serving\": [\n        \"Cook the rice according to the package directions.\",\n        \"While the rice is cooking, heat the coconut milk in a saucepan over medium heat. Add the pandan leaf, salt, turmeric, cumin, coriander, and black pepper. Bring to a simmer and cook for 5 minutes.\",\n        \"To serve, place the rice in a bowl and top with the coconut milk sauce, peanuts, egg, cucumber, and chicken. Enjoy!\"\n    ]\n}\n```"
    

    start_index = string.find("```json")
    if start_index == -1:
        print(string)
    start_index += len("```json")
    end_index = string.find("```", start_index)
    if end_index == -1:
        print(string)
    json_string = string[start_index:end_index].strip()
    json_string = json_string.replace(",\n    ]", "\n    ]") # remove trailing comma
    try:
        json_string_output = json.loads(json_string)
    except json.JSONDecodeError as e:
        warnings.warn(f"JSONDecodeError: {e}")



