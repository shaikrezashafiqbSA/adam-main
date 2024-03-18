from anthropic import Anthropic
import numpy as np
import pandas as pd

class ClaudeHandler:
    """
    This class is a wrapper around the Anthropic's Claude API.

    It allows the user to easily interact with the API and perform various tasks.
    It has the following features:
    1) text --> text
    2) text + image --> text
    """

    def __init__(self, api_key):
        """
        api_key: str
            The API key for the Claude API
        """
        self.client = Anthropic.Client(api_key)

    def prompt(self, prompt, model="claude-v1"):
        """
        Sends a text prompt to the Claude API and returns the response.

        prompt: str
            The text prompt to send to the API
        model: str, optional
            The name of the model to use (default is "claude-v1")

        Returns:
            The response from the API as a string
        """
        response = self.client.completion(
            prompt=f"{prompt}",
            model=model,
            max_tokens_to_sample=1024,
            stop_sequences=[],
        )
        return response.result["completion"]

    def prompt_image(self, image_path, prompt, model="claude-v1.0"):
        """
        Sends a text prompt and an image to the Claude API and returns the response.

        image_path: str
            The path to the image file
        prompt: str
            The text prompt to send to the API
        model: str, optional
            The name of the model to use (default is "claude-v1.0")

        Returns:
            The response from the API as a string
        """
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        response = self.client.Image_completion(
            prompt=f"{prompt}",
            image=image_bytes,
            model=model,
            max_tokens_to_sample=1024,
            stop_sequences=[],
        )
        return response.result["completion"]

    def embed_text(self, text, model="claude-v1"):
        """
        Embeds a text using the Claude API's text embedding model.

        text: str
            The text to embed
        model: str, optional
            The name of the model to use (default is "claude-v1")

        Returns:
            A numpy array containing the embedding vector
        """
        response = self.client.embed_text(text, model=model)
        return np.array(response.result["embeddings"][0])

    def embed_df(self, df, text_column, model="claude-v1"):
        """
        Embeds the text in a DataFrame column using the Claude API's text embedding model.

        df: pandas.DataFrame
            The DataFrame containing the text to embed
        text_column: str
            The name of the column containing the text to embed
        model: str, optional
            The name of the model to use (default is "claude-v1")

        Returns:
            The original DataFrame with a new column containing the embedding vectors
        """
        df["Embeddings"] = df[text_column].apply(lambda text: self.embed_text(text, model))
        return df