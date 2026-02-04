import React from 'react';
import './ChatMessage.css';

const ChatMessage = ({ sender, text }) => {
  return (
    <div className={`chat-message ${sender}`}>
      <div className="message-content">
        <p>{text}</p>
      </div>
    </div>
  );
};

export default ChatMessage;
