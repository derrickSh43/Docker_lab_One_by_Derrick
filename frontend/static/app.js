const term = new Terminal();
term.open(document.getElementById("terminal"));
term.focus();

let socket = null;

function updateWebSocket(labNumber) {
  if (socket && socket.readyState !== WebSocket.CLOSED) {
    socket.close();
  }
  term.clear();
  term.write('\r\n');

  if (!labNumber) {
    term.write('Select a lab to begin.\r\n');
    return;
  }

  const wsUrl = `ws://localhost:8000/ws/${labNumber}`;
  console.log("📡 Connecting to WebSocket at:", wsUrl);

  try {
    socket = new WebSocket(wsUrl);
    socket.onopen = () => {
      console.log("✅ WebSocket connected");
      term.write('Lab started. Enter commands here.\r\n');
    };
    socket.onerror = (err) => {
      console.error("❌ WebSocket error:", err);
      term.write('❌ WebSocket error occurred.\r\n');
    };
    socket.onclose = (event) => {
      console.warn("⚠️ WebSocket closed with code:", event.code, "reason:", event.reason);
      term.write('⚠️ WebSocket closed.\r\n');
    };
    socket.onmessage = (event) => {
      term.write(event.data);
      if (event.data.includes("Validation Result")) {
        document.getElementById("check-result").textContent = event.data;
      }
    };
    term.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(data);
      }
    });
    document.getElementById("check-btn").onclick = () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(`__VALIDATE__ ${currentTask + 1}`);
      }
    };
  } catch (err) {
    console.error("❌ Failed to create WebSocket:", err);
    term.write('❌ Failed to connect to WebSocket.\r\n');
  }
}

updateWebSocket(null);