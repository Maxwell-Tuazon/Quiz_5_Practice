import React, { useState, useRef, useEffect } from 'react';
import { Card, Form, Button, ListGroup, InputGroup } from 'react-bootstrap';

function ChatbotScreen() {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'Artificial Idiot', text: 'Hi — I\'m your local AI chatbot. How can I help?' },
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const nextId = useRef(2);
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { id: nextId.current++, sender: 'user', text: input };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setSending(true);

    try {
      const res = await fetch('/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.text }),
      });
      const data = await res.json();
      const botMsg = {
        id: nextId.current++,
        sender: 'Artificial Idiot',
        text: data.reply || 'No reply from server',
      };
      setMessages((m) => [...m, botMsg]);
    } catch (err) {
      const botMsg = { id: nextId.current++, sender: 'Artificial Idiot', text: `Error: ${err.message}` };
      setMessages((m) => [...m, botMsg]);
    } finally {
      setSending(false);
    }
  };

  return (
    <Card>
      <Card.Header>AI Chatbot</Card.Header>
      <Card.Body style={{ height: '60vh', display: 'flex', flexDirection: 'column' }}>
        <ListGroup variant="flush" style={{ overflowY: 'auto', flex: 1 }}>
          {messages.map((msg) => (
            <ListGroup.Item key={msg.id} className={msg.sender === 'user' ? 'text-end' : ''}>
              <div><strong>{msg.sender === 'user' ? 'You' : 'Artificial Idiot'}</strong></div>
              <div>{msg.text}</div>
            </ListGroup.Item>
          ))}
          <div ref={bottomRef} />
        </ListGroup>

        <Form onSubmit={handleSend} className="mt-3">
          <InputGroup>
            <Form.Control
              placeholder="Type a message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <Button type="submit" variant="primary" disabled={sending}>
              {sending ? 'Sending…' : 'Send'}
            </Button>
          </InputGroup>
        </Form>
      </Card.Body>
    </Card>
  );
}

export default ChatbotScreen;
