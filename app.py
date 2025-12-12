from flask import Flask, render_template, request, jsonify
from config import SECRET_KEY, FLASK_ENV
from model.agente import generate_response

app = Flask(
  __name__,
  static_folder="static",
  template_folder="templates",
)

app.config["SECRET_KEY"] = SECRET_KEY
app.config["ENV"] = FLASK_ENV


# ---------------------------------------------------------
# RUTA PRINCIPAL: sirve la interfaz del chatbot
# ---------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
  return render_template("index.html")


# ---------------------------------------------------------
# API: /api/chat
# Recibe { message, history } y devuelve { success, response, history }
# ---------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def api_chat():
  try:
    data = request.get_json(force=True) or {}
  except Exception:
    return (
      jsonify(
        {
          "success": False,
          "error": "Request body must be valid JSON.",
        }
      ),
      400,
    )

  user_message = (data.get("message") or "").strip()
  history = data.get("history") or []

  if not user_message:
    return (
      jsonify(
        {
          "success": False,
          "error": "Message cannot be empty.",
        }
      ),
      400,
    )

  try:
    assistant_message = generate_response(user_message, history)
  except Exception as exc:
    # En un sistema real se registra el error con logging estructurado.
    print(f"[ERROR] /api/chat: {exc}")
    return (
      jsonify(
        {
          "success": False,
          "error": "Ocurrió un error generando la respuesta del agente.",
        }
      ),
      500,
    )

  # El frontend maneja y actualiza el history localmente.
  return jsonify(
    {
      "success": True,
      "response": assistant_message,
      "history": history,
    }
  )


if __name__ == "__main__":
  # Solo para desarrollo local
  app.run(host="127.0.0.1", port=5000, debug=True)
