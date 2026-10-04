from openai import(
   OpenAI,
   APIConnectionError,
   APITimeoutError,
   AuthenticationError,
   InternalServerError,
   RateLimitError,
)

from app.core.config import settings
from app.core.exceptions import AIUnavailable
from app.logging_config import logger


AI_TIMEOUT_SECONDS = 20
AI_MAX_RETRIES = 1 

TRANSIENT_ERRORS = (
   APITimeoutError,
   APIConnectionError,
   RateLimitError,
   InternalServerError
)

def get_client()  -> OpenAI:
   if not settings.openai_api_key:
      raise AIUnavailable("не задан OPENAI_API_KEY")
   return OpenAI(
      api_key=settings.openai_api_key,
      timeout=AI_TIMEOUT_SECONDS,
      max_retries= AI_MAX_RETRIES,
   )



def ask(client: OpenAI, **kwargs):
   try:
      return client.chat.completions.create(**kwargs)
   except TRANSIENT_ERRORS as error:
      raise AIUnavailable(f"{type(error).__name__}:{error}")
   except AuthenticationError as error:
      logger.error("OpenAI отклонил ключ:  %s", error)
      raise AIUnavailable("ключ OpanAI отклонен")
