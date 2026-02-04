import React, { useState, useRef } from 'react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, onFileSelect }) => { 
  const [input, setInput] = useState('');
  const [isRagMode, setIsRagMode] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleSend = () => {
    onSendMessage(input, isRagMode, selectedFile);
    setInput('');
    setSelectedFile(null);
    if(fileInputRef.current) {
        fileInputRef.current.value = '';
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    
    // 2. Call the function passed down from App.js IMMEDIATELY
    if (file) {
      onFileSelect(file); 
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current.click();
  }

  return (
    <div className="chat-input-container">
      <div className="input-bar">
        <button className="upload-btn" onClick={triggerFileSelect}>+</button>
        <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            style={{ display: 'none' }} 
            accept=".pdf"
        />
        <input
          type="text"
          className="text-input"
          placeholder="Ask anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="send-btn" onClick={handleSend}>Send</button>
      </div>
      <div className="rag-toggle-container">
        <label className="switch">
          <input 
            type="checkbox" 
            checked={isRagMode} 
            onChange={() => setIsRagMode(!isRagMode)} 
          />
          <span className="slider round"></span>
        </label>
        <span>Enable RAG Mode</span>
      </div>
    </div>
  );
};

export default ChatInput;
