import React from "react"

interface SidebarProps {
  isOpen: boolean
  onNewChat: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onNewChat }) => {
  return (
    <div className={`sidebar ${isOpen ? "active" : ""}`}>
      <div className="sidebar-header">
        <div className="logo">
          <i className="fas fa-car-alt"></i>
          <span>AutoGenius</span>
        </div>
        <button className="new-chat-btn" onClick={onNewChat}>
          <i className="fas fa-plus"></i> New Chat
        </button>
      </div>
      
      <div className="sidebar-content">
        <div className="history-section">
          <h3>Recent Conversations</h3>
          <div className="history-list">
            <div className="history-empty">No past conversations</div>
          </div>
        </div>
      </div>
      
      <div className="sidebar-footer">
        <button className="sidebar-btn">
          <i className="fas fa-trash"></i> Clear History
        </button>
        <button className="sidebar-btn">
          <i className="fas fa-moon"></i> Dark Mode
        </button>
      </div>
    </div>
  )
}

export default Sidebar