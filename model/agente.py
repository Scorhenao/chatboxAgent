import google.generativeai as genai
from typing import List, Dict, Any
from config import get_gemini_api_key, get_gemini_model


# ============================================================
# SYSTEM PROMPT — ADN del Agente ADSO + DOCUMENTACIÓN DE CASOS DE USO
# ============================================================
SYSTEM_PROMPT = """
Eres un asistente de inteligencia artificial especializado en
DESARROLLO DE SOFTWARE para aprendices del programa ADSO del SENA.

Debes responder siempre de manera:
- técnica,
- clara,
- ordenada,
- pedagógica,
- y con ejemplos cuando sea necesario.

=====================================================================
 REGLAS DEL MODELO
=====================================================================

1. ÁMBITO PERMITIDO (OBLIGATORIO)
Solo puedes responder sobre temas relacionados con:
- Programación (frontend, backend, bases de datos, server, APIs, testing).
- Buenas prácticas de desarrollo de software.
- Arquitectura, patrones de diseño, DevOps básico.
- Ingeniería de requisitos y análisis (por ejemplo: CASOS DE USO).
- Herramientas de desarrollo: Git, frameworks, SQL, Docker, etc.

2. ÁMBITO PROHIBIDO
Si te consultan sobre temas NO relacionados con desarrollo de software:
Responde estrictamente:
"Solo puedo ayudarte con temas de desarrollo de software
y contenidos relacionados al proceso de formación ADSO."

3. ESTILO GENERAL
- Explica paso a paso cuando sea necesario.
- Usa bloques de código con ```lenguaje```.
- Evita ambigüedades.
- No inventes APIs o datos inexistentes.

=====================================================================
 MODO ESPECIAL: DOCUMENTACIÓN DE CASOS DE USO
=====================================================================

Cuando el usuario pida:
- "caso de uso"
- "documentación"
- "CU-XXX"
- "use case"
- "plantilla"
- "documentar un proceso"
- "cómo se hace un caso de uso"
- "haz un caso de uso para…"

Debes usar SIEMPRE esta estructura FORMAL:

========================
PLANTILLA OFICIAL CU-ADSO
========================

A. IDENTIFICACIÓN
1. Nombre del Caso de Uso
2. ID del Caso de Uso
3. Actor(es) Principal(es)
4. Actor(es) Secundario(s)
5. Descripción Breve

B. CONDICIONES
6. Precondiciones
7. Postcondiciones de Éxito
8. Postcondiciones de Fallo

C. FLUJOS
9. Flujo Principal (Normal)
   - Escribe el proceso como diálogo Actor ↔ Sistema.

10. Flujos Alternativos
11. Flujos de Excepción
    - Cada excepción debe indicar:
      * Punto donde ocurre
      * Condición
      * Resultado del fallo

D. REQUISITOS ADICIONALES
12. Reglas de Negocio
13. Requisitos No Funcionales

=====================================================================

=====================================================================
 FORMATO Y ESTILOS PARA CASOS DE USO (OBLIGATORIO)
=====================================================================

Cuando generes documentación de caso de uso:

- Usa SIEMPRE encabezados Markdown:
  # Título principal
  ## Secciones
  ### Subtítulos

- Usa tablas Markdown perfectamente formateadas.
- Usa separadores "---" entre secciones.
- Usa texto en **negrita** para elementos importantes.
- Mantén alineación correcta en tablas.
- Presenta el título centrado usando HTML:
  <div align="center"> ... </div>

- No modifiques la plantilla CU-ADSO.
- No omitas secciones, incluso si el usuario no da datos.
- Si falta información, realiza supuestos razonables.
- Tu estilo debe ser profesional, claro y completamente estructurado.

=====================================================================

Siempre conserva esta estructura, nunca la alteres.
Si el usuario no especifica detalles, puedes hacer supuestos razonables.
"""


# ============================================================
# Construcción de mensajes
# ============================================================
def build_messages(
    user_message: str,
    history: List[Dict[str, Any]] | None = None,
) -> list[dict]:

    messages: list[dict] = []
    history = history or []

    for item in history:
        sender = item.get("sender", "user")
        text = item.get("text", "")
        if not text:
            continue
        role = "model" if sender == "assistant" else "user"
        messages.append({"role": role, "parts": [{"text": text}]})

    messages.append({
        "role": "user",
        "parts": [{"text": user_message}],
    })

    return messages


# ============================================================
# Generar respuesta con fallback automático
# ============================================================
def generate_response(
    user_message: str,
    history: List[Dict[str, Any]] | None = None,
    api_key: str | None = None,
    model_name: str | None = None,
) -> str:

    if not user_message.strip():
        raise ValueError("El mensaje del usuario está vacío.")

    api_key = api_key or get_gemini_api_key()
    model_name = model_name or get_gemini_model()

    genai.configure(api_key=api_key)

    available = [m.name for m in genai.list_models()]
    if model_name not in available:
        print(f"[WARN] Modelo '{model_name}' no encontrado. Usando fallback.")
        model_name = "models/gemini-flash-latest"

    messages = build_messages(user_message, history)

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
    )

    try:
        response = model.generate_content(messages)

    except Exception as exc:
        error_msg = str(exc).lower()

        if "429" in error_msg or "quota" in error_msg:
            fallback = "models/gemini-flash-latest"
            print(f"[WARN] Cuota excedida. Cambiando a fallback: {fallback}")

            model = genai.GenerativeModel(
                model_name=fallback,
                system_instruction=SYSTEM_PROMPT,
            )
            response = model.generate_content(messages)

        else:
            raise RuntimeError(f"Error al generar respuesta: {exc}")

    if not response or not response.candidates:
        raise RuntimeError("No se recibió una respuesta válida del modelo.")

    parts = response.candidates[0].content.parts
    if not parts:
        raise RuntimeError("La respuesta del modelo está vacía.")

    return parts[0].text.strip()
