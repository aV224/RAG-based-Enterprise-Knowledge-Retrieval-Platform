import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // New function to handle the problem of files uploading only after next chat message is typed in and clicked enter
  const handleFileSelect = (file) => {
    if (file) {
      // Check for duplicates before adding
      if (!uploadedFiles.some(f => f.name === file.name)) {
        setUploadedFiles(prev => [...prev, file]);
      }
    }
  };

  const handleSendMessage = async (input, isRagMode, file) => {
    if (!input.trim() && !file) return;

    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);

    const formData = new FormData();
    formData.append('question', input);
    formData.append('private', isRagMode);
    if (isRagMode && file) {
      formData.append('file', file);
    }

    try {
      const response = await axios.post('http://127.0.0.1:8000/chat', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',  
        },
      });

      const botMessage = { sender: 'bot', text: response.data.response || response.data.error };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      const errorMessage = { sender: 'bot', text: `Error: ${error.message}` };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="App">
      <Sidebar uploadedFiles={uploadedFiles} />
      <main className="chat-area">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>What are you working on?</h2>
            </div>
          ) : (
            messages.map((msg, index) => (
              <ChatMessage key={index} sender={msg.sender} text={msg.text} />
            ))
          )}
        </div>
        <ChatInput
          onSendMessage={handleSendMessage}
          onFileSelect = {handleFileSelect} 
        />
      </main>
    </div>
  );
}

export default App;
