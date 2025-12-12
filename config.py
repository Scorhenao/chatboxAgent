import os
from dotenv import load_dotenv

# Carga variables desde .env
load_dotenv()

# Configuración básica
FLASK_ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_key_insegura")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def get_gemini_api_key() -> str:
  """
  Devuelve la API key de Gemini o lanza un error claro si no existe.
  """
  if not GEMINI_API_KEY:
    raise RuntimeError(
      "No se encontró GEMINI_API_KEY. "
      "Configúrala en el archivo .env."
    )
  return GEMINI_API_KEY


def get_gemini_model():
    return os.getenv("GEMINI_MODEL", "models/gemini-flash-latest")
