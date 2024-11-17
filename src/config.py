import os
from typing import List,  Dict, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

def configure_api_keys():
    """Configure and verify API keys for LLM services."""
    
    load_dotenv()
    api_key = os.getenv("NEMOTRON_4_340B_INSTRUCT_KEY")

    # Set environment variable
    # os.environ['NEMOTRON_4_340B_INSTRUCT_KEY'] = api_key
    
    # Print configuration status
    print(api_key)
    is_configured = bool(api_key)
    print(f"API Key configured: {is_configured}")
    return is_configured

api_configured = configure_api_keys()
if not api_configured:
    print("\nAPI key not found. Please ensure you have:")
    print("1. Set up your API key in Google Colab secrets, or")
    print("2. Created a .env file with NEMOTRON_4_340B_INSTRUCT_KEY")
    
class LLMConfig:
    """Configuration settings for the LLM."""
    base_url: str = "https://integrate.api.nvidia.com/v1"
    model: str = "nvidia/nemotron-4-340b-instruct"
    max_tokens: int = 1024
    default_temp: float = 0.5

class NeMoLLaMa:
  """
  A class to interact with NVIDIA's nemotron-4-340b-instruct model through their API
  This implementation uses AsyncOpenAI client for asynchronous operations
  """

  def __init__(self, api_key: str):
    """Initialize NeMoLLaMa with API key.

    Args:
        api_key (str): NVIDIA API authentication key
    """
    self.config = LLMConfig()
    self.client = AsyncOpenAI(
        base_url=self.config.base_url,
        api_key=api_key
    )
    self._is_authenticated = False

  async def check_auth(self) -> bool:
      """Verify API authentication with test request.

      Returns:
          bool: Authentication status

      Example:
          >>> is_valid = await llm.check_auth()
          >>> print(f"Authenticated: {is_valid}")
      """
      test_message = [{"role": "user", "content": "test"}]
      try:
          await self.agenerate(test_message, temperature=0.7)
          self._is_authenticated = True
          return True
      except Exception as e:
          print(f"❌ Authentication failed: {str(e)}")
          return False

  async def agenerate(
      self,
      messages: List[Dict],
      temperature: Optional[float] = None
  ) -> str:
      """Generate text using NeMo LLaMa model.

      Args:
          messages: List of message dicts with 'role' and 'content'
          temperature: Sampling temperature (0.0 to 1.0, default from config)

      Returns:
          str: Generated text response

      Example:
          >>> messages = [
          ...     {"role": "system", "content": "You are a helpful assistant"},
          ...     {"role": "user", "content": "Plan my study schedule"}
          ... ]
          >>> response = await llm.agenerate(messages, temperature=0.7)
      """
      completion = await self.client.chat.completions.create(
          model=self.config.model,
          messages=messages,
          temperature=temperature or self.config.default_temp,
          max_tokens=self.config.max_tokens,
          stream=False
      )
      return completion.choices[0].message.content