// Historial local: [{ sender: "user" | "assistant", text: "..." }]
let conversationHistory = [];

const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const typingIndicator = document.getElementById("typing-indicator");

function appendMessage(sender, text) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender);

  const bubble = document.createElement("div");
  bubble.classList.add("message-bubble");

  // Render Markdown → HTML
  bubble.innerHTML = marked.parse(text);

  messageDiv.appendChild(bubble);
  chatWindow.appendChild(messageDiv);

  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setLoading(isLoading) {
  if (isLoading) {
    typingIndicator.classList.remove("hidden");
    sendButton.disabled = true;
  } else {
    typingIndicator.classList.add("hidden");
    sendButton.disabled = false;
  }
}

async function sendMessage(message) {
  if (!message.trim()) return;

  // Mostrar mensaje del usuario
  appendMessage("user", message);
  conversationHistory.push({ sender: "user", text: message });

  setLoading(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        history: conversationHistory,
      }),
    });

    const data = await response.json();

    if (!data.success) {
      const errorMsg =
        data.error || "Ocurrió un error al comunicarse con el agente.";
      appendMessage("assistant", errorMsg);
      conversationHistory.push({ sender: "assistant", text: errorMsg });
      return;
    }

    const assistantText = data.response || "(Respuesta vacía del modelo)";
    appendMessage("assistant", assistantText);
    conversationHistory.push({ sender: "assistant", text: assistantText });
  } catch (err) {
    console.error("Error al enviar mensaje:", err);
    const msg =
      "No se pudo contactar al servidor. Verifica que Flask esté en ejecución.";
    appendMessage("assistant", msg);
    conversationHistory.push({ sender: "assistant", text: msg });
  } finally {
    setLoading(false);
  }
}

// Manejo del formulario
chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = userInput.value;
  userInput.value = "";
  sendMessage(message);
});

// Enviar con Ctrl+Enter (opcional)
userInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    chatForm.dispatchEvent(new Event("submit"));
  }
});

// Mensaje de bienvenida
appendMessage(
  "assistant",
  "Hola, soy tu chatbot ADSO especializado en desarrollo de software.\n" +
    "Pregúntame sobre programación, buenas prácticas, arquitectura, APIs, etc."
);

marked.setOptions({
  highlight: function (code, lang) {
    return hljs.highlightAuto(code).value;
  },
});
