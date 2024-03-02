import os
import requests

def get_image(path, workspace_path = "./workspace/food"):
    if path.startswith('http'):
        # Download image from URL
        filename = os.path.basename(path)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(path, headers=headers)
        with open(f"{workspace_path}/{filename}", 'wb') as f:
            f.write(response.content)
        print(f'Downloaded image from URL: {filename}')
        return response.content
    else:
        # Read local file
        with open(path, 'rb') as f:
            data = f.read()
            print(f'Read local file: {path}')
            return data