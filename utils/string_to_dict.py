import re

def convert_string_to_dict0(text, headers = ["name", "description", "serving_size", "ingredients", "nutrition_per_serving", "recipe_per_serving"]):
    if type(headers) == str:
        headers = [item.strip().replace(',', '') for item in headers.split("\n") if item.strip()]
    headers_regex = "|".join(headers)
    headers_regex_no_underscores = "|".join([re.sub(r"_", " ", header) for header in headers])
    pattern = re.compile(rf"({headers_regex}|{headers_regex_no_underscores}):(.+?)(?={headers_regex}|{headers_regex_no_underscores}:|$)", re.DOTALL | re.IGNORECASE)

    result = {}
    for match in pattern.finditer(text):
        header = re.sub(r"\s+", "_", match.group(1).lower())
        content = match.group(2).strip()
        # print(f"content: {content}")
        if header in headers[-3:]:
            # print(f"---content: {content}")
            content_list = content.split("\n")
            indexes_to_drop = []
            for line_str_i, line_str in enumerate(content_list):
                # print(f"----checking if '{line_str}' is smaller than 4---> {len(line_str)}<{4}")
                if len(line_str)<4:
                    indexes_to_drop.append(line_str_i)
            
            # print(f"---indexes_to_drop: {indexes_to_drop}")
            if header == headers[-1]:
                indexes_to_drop.append(len(content_list)-1)
                content = [item for i, item in enumerate(content_list) if i not in indexes_to_drop]
            else: 
                content = [item for i, item in enumerate(content_list) if i not in indexes_to_drop]
        result[header] = content
    # print(f"result: {result.keys()}\nresult len: {len(result)}")
    return result



def convert_string_to_dict1(text, headers = ["name", "description", "serving_size", "ingredients", "nutrition_per_serving", "recipe_per_serving"]):
    if type(headers) == str:
        headers = [item.strip().replace(',', '') for item in headers.split("\n") if item.strip()]
    headers_regex = "|".join(headers)
    headers_regex_no_underscores = "|".join([re.sub(r"_", " ", header) for header in headers])
    pattern = re.compile(rf"({headers_regex}|{headers_regex_no_underscores}):(.+?)(?={headers_regex}|{headers_regex_no_underscores}:|$)", re.DOTALL | re.IGNORECASE)

    result = {}
    for match in pattern.finditer(text):
        header = re.sub(r"\s+", "_", match.group(1).lower())
        content = match.group(2).strip()
        # print(f"content: {content}")
        if header in headers[-3:]:
            # print(f"---content: {content}")
            content_list = content.split("\n")
            indexes_to_drop = []
            for line_str_i, line_str in enumerate(content_list):
                # print(f"----checking if '{line_str}' is smaller than 4---> {len(line_str)}<{4}")
                if len(line_str)<4:
                    indexes_to_drop.append(line_str_i)
            
            # print(f"---indexes_to_drop: {indexes_to_drop}")
            if header == headers[-1]:
                indexes_to_drop.append(len(content_list)-1)
                content = [item for i, item in enumerate(content_list) if i not in indexes_to_drop]
            else: 
                content = [item for i, item in enumerate(content_list) if i not in indexes_to_drop]
                
            # Remove unwanted characters from the beginning of each string
            content = [re.sub(r'^\s*[-\d]+\.\s*', '', item) for item in content]
            content = [re.sub(r'^\s*-\s*', '', item) for item in content]
        result[header] = content
    # print(f"result: {result.keys()}\nresult len: {len(result)}")
    return result

def convert_string_to_dict(text, headers = ["name", "description", "serving_size", "ingredients", "nutrition_per_serving", "recipe_per_serving"]):
    if type(headers) == str:
        headers = [item.strip().replace(',', '') for item in headers.split("\n") if item.strip()]
    headers_regex = "|".join(headers)
    headers_regex_no_underscores = "|".join([re.sub(r"_", " ", header) for header in headers])
    pattern = re.compile(rf"({headers_regex}|{headers_regex_no_underscores}):(.+?)(?={headers_regex}|{headers_regex_no_underscores}:|$)", re.DOTALL | re.IGNORECASE)

    result = {}
    for match in pattern.finditer(text):
        header = re.sub(r"\s+", "_", match.group(1).lower())
        content = match.group(2).strip()
        # print(f"content: {content}")
        if header in headers[-3:]:
            # print(f"---content: {content}")
            content_list = content.split("\n")
            indexes_to_drop = []
            for line_str_i, line_str in enumerate(content_list):
                # print(f"----checking if '{line_str}' is smaller than 4---> {len(line_str)}<{4}")
                if len(line_str)<4:
                    indexes_to_drop.append(line_str_i)
            
            # print(f"---indexes_to_drop: {indexes_to_drop}")
            if header == headers[-1]:
                indexes_to_drop.append(len(content_list)-1)
                content = [item for i, item in enumerate(content_list) if i not in indexes_to_drop]
            else: 
                content = [item for i, item in enumerate(content_list) if i not in indexes_to_drop]
                
            # Remove unwanted characters from the beginning of each string
            content = [re.sub(r'^\s*[-\d]+\.\s*', '', item) for item in content]
            content = [re.sub(r'^\s*[-*]\s*', '', item) for item in content]
        result[header] = content
    # print(f"result: {result.keys()}\nresult len: {len(result)}")
    return result
