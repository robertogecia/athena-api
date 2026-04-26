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
      // skip
    } else if (msg.role === 'user' || msg.role === 'assistant') {
      chatMessages.push({ role: msg.role, content: msg.content });
    }
  }

  if (chatMessages.length === 0) {
    return res.status(400).json({ error: 'No valid messages' });
  }

  try {
    const body = {
      model: 'claude-3-haiku-20240307',
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
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      return res.status(response.status).json({ error: errData.error || 'Anthropic API error' });
    }

    const data = await response.json();
    const text = data.content[0].text;
    return res.status(200).json({ content: text });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
