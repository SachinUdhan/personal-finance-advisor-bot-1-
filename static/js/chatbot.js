/**
 * AI Financial Advisor Interactive Chatbot
 */

document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const messagesContainer = document.getElementById('chat-messages');
  const sendButton = document.getElementById('btn-send-chat');

  if (!chatForm || !chatInput || !messagesContainer) return;

  // Simple Markdown renderer for basic bot formatting (bold, bullet points, headers)
  function formatMarkdown(text) {
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Bullet points
    html = html.replace(/^- (.*$)/gim, '<li style="margin-left: 1.25rem;">$1</li>');
    // Headers ###
    html = html.replace(/^### (.*$)/gim, '<h4 style="margin: 0.5rem 0; font-size: 1rem;">$1</h4>');
    // Numbered lists 1. text
    html = html.replace(/^\d+\. (.*$)/gim, '<li style="margin-left: 1.25rem; list-style-type: decimal;">$1</li>');
    // Line breaks
    html = html.replace(/\n\n/g, '<p style="margin-top: 0.5rem;"></p>');
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  function appendMessage(sender, text, isMarkdown = false, meta = '') {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;

    const contentDiv = document.createElement('div');
    if (isMarkdown) {
      contentDiv.innerHTML = formatMarkdown(text);
    } else {
      contentDiv.textContent = text;
    }
    msgDiv.appendChild(contentDiv);

    if (meta) {
      const metaDiv = document.createElement('div');
      metaDiv.className = 'message-meta';
      metaDiv.textContent = meta;
      msgDiv.appendChild(metaDiv);
    }

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return msgDiv;
  }

  // Handle form submit
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Append user message
    appendMessage('user', query, false, 'You');
    chatInput.value = '';

    // Append temporary typing indicator
    const typingMsg = appendMessage('bot', 'Analyzing your live finances...', false, 'Advisor Bot');
    if (sendButton) sendButton.disabled = true;

    try {
      const res = await fetch('/api/chatbot/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query })
      });

      const data = await res.json();
      typingMsg.remove();

      if (res.ok) {
        const sourceLabel = data.source === 'gemini_api' ? 'Gemini AI &bull; Context Aware' : 'Smart Advisor &bull; Context Aware';
        appendMessage('bot', data.reply, true, sourceLabel);
      } else {
        appendMessage('bot', data.error || 'Failed to process advice query.', false, 'Error');
      }
    } catch (err) {
      typingMsg.remove();
      appendMessage('bot', 'Network or server error while connecting to advisor.', false, 'Connection Error');
    } finally {
      if (sendButton) sendButton.disabled = false;
      chatInput.focus();
    }
  });

  window.sendQuickPrompt = (promptText) => {
    chatInput.value = promptText;
    chatForm.dispatchEvent(new Event('submit'));
  };

  window.clearChatHistory = () => {
    messagesContainer.innerHTML = `
      <div class="message bot">
        <p>Chat cleared. Ask any question about your budget, savings targets, or spending habits!</p>
        <div class="message-meta">Advisor Bot</div>
      </div>
    `;
  };
});
