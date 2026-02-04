import React from 'react';
import './Sidebar.css';

const Sidebar = ({ uploadedFiles }) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button className="new-chat-btn">+ New chat</button>
      </div>
      <div className="uploaded-files-section">
        <h4>Uploaded Documents</h4>
        <ul className="file-list">
          {uploadedFiles.length > 0 ? (
            uploadedFiles.map((file, index) => (
              <li key={index}>{file.name}</li>
            ))
          ) : (
            <li className="no-files">No files uploaded yet.</li>
          )}
        </ul>
      </div>
      <div className="ecs-toggle-section">
        <span>Use Files from S3</span>
        <label className="switch">
          <input type="checkbox" disabled />
          <span className="slider round"></span>
        </label>
      </div>
    </aside>
  );
};

export default Sidebar;