export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { messages } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Invalid messages' });
  }

  let systemPrompt = '';
  let chatMessages = [];

  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i];
    if (i === 0 && msg.role === 'user') {
      systemPrompt = msg.content;
    } else if (i === 1 && msg.role === 'assistant') {
      // skip — this is the assistant acknowledgment of system prompt
    } else if (msg.role === 'user' || msg.role === 'assistant') {
      chatMessages.push({ role: msg.role, content: msg.content });
    }
  }

  if (chatMessages.length === 0) {
    return res.status(400).json({ error: 'No valid messages' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  console.log('Key length:', apiKey ? apiKey.length : 0, 'starts:', apiKey ? apiKey.substring(0, 14) : 'none');

  try {
    const body = {
      model: 'claude-3-5-haiku-20241022',
      max_tokens: 1024,
      messages: chatMessages,
    };

    if (systemPrompt) {
      body.system = systemPrompt;
    }

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(body),
    });

    const responseText = await response.text();
    console.log('Anthropic status:', response.status, 'body:', responseText.substring(0, 300));

    if (!response.ok) {
      let errData = {};
      try { errData = JSON.parse(responseText); } catch(e) {}
      return res.status(response.status).json({ error: errData.error || responseText });
    }

    const data = JSON.parse(responseText);
    const text = data.content[0].text;
    return res.status(200).json({ reply: text });

  } catch (err) {
    console.log('Catch error:', err.message);
    return res.status(500).json({ error: err.message });
  }
}
