const API_URL = "http://127.0.0.1:8000/chat";

export async function sendMessage(
  message,
  sessionId,
  accessToken,
  onToken
) {

  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",

      ...(accessToken && {
        Authorization: `Bearer ${accessToken}`,
      }),
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId || null,
    }),
  });


  if (!response.ok) {
    throw new Error("Failed to contact AI");
  }


  const newSessionId = response.headers.get("X-Session-Id");


  const reader = response.body.getReader();
  const decoder = new TextDecoder();


  let fullReply = "";


  while (true) {

    const { value, done } = await reader.read();


    if (done) break;


    const chunk = decoder.decode(value, {
      stream: true,
    });


    fullReply += chunk;


    if (onToken) {
      onToken(chunk);
    }
  }


  return {
    reply: fullReply,
    sessionId: newSessionId,
  };
}
export async function getConversations(accessToken) {

    const response = await fetch(
        "http://127.0.0.1:8000/sessions",
        {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        }
    );

    return await response.json();

}
export async function getMessages(sessionId, accessToken) {

    const response = await fetch(
        `http://127.0.0.1:8000/sessions/${sessionId}/messages`,
        {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        }
    );

    return await response.json();

}