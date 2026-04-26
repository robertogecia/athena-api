export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
}

  const { messages } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Invalid messages' });
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'x-api-key': process.env.ANTHROPIC_API_KEY,
              'anthropic-version': '2023-06-01',
      },
            body: JSON.stringify({
              model: 'claude-3-5-haiku-20241022',
              max_tokens: 1024,
              messages: messages,
      }),
      });

    if (!response.ok) {
      const error = await response.text();
      return res.status(500).json({ error: 'API error', details: error });
    }

    const data = await response.json();
    const reply = data.content[0].text;

    res.setHeader('Access-Control-Allow-Origin', 'https://robertogrecia.com');
    res.setHeader('Access-Control-Allow-Methods', 'POST');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    return res.status(200).json({ reply });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
