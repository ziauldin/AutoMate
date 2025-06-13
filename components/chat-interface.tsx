"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import type { Message } from "@/types"
import MessageComponent from "./message"

interface ChatInterfaceProps {
  messages: Message[]
  title: string
  isViewingHistory: boolean
  onSendMessage: (message: string) => void
  onToggleSidebar: () => void
  onExportChat: () => void
}

export default function ChatInterface({
  messages,
  title,
  isViewingHistory,
  onSendMessage,
  onToggleSidebar,
  onExportChat,
}: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Suggestions for the chat
  const suggestions = [
    { text: "What are the specifications of my car?", icon: "info-circle", label: "Car specifications" },
    { text: "What maintenance is recommended for my mileage?", icon: "tools", label: "Maintenance schedule" },
    { text: "What does this warning light mean?", icon: "exclamation-triangle", label: "Warning lights" },
    { text: "Show me my car", icon: "car", label: "Show my car" },
  ]

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto"
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`
    }
  }, [inputValue])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSendMessage = () => {
    if (inputValue.trim() && !isViewingHistory) {
      onSendMessage(inputValue)
      setInputValue("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSuggestionClick = (text: string) => {
    if (!isViewingHistory) {
      onSendMessage(text)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <button onClick={onToggleSidebar} className="icon-btn">
          <i className="fas fa-bars"></i>
        </button>
        <div className="chat-title">
          <span>{title}</span>
        </div>
        <div className="chat-actions">
          <button onClick={onExportChat} className="icon-btn" title="Export Conversation">
            <i className="fas fa-download"></i>
          </button>
          <button className="icon-btn" title="Voice Input">
            <i className="fas fa-microphone"></i>
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <MessageComponent key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            id="user-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isViewingHistory
                ? "This is a past conversation. Start a new chat to continue."
                : "Ask about your vehicle..."
            }
            rows={1}
            disabled={isViewingHistory}
          />
          <div className="input-actions">
            <button className="icon-btn" title="Attach Image">
              <i className="fas fa-paperclip"></i>
            </button>
            <button id="send-btn" onClick={handleSendMessage} disabled={!inputValue.trim() || isViewingHistory}>
              <i className="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>

        <div className="chat-suggestions">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="suggestion-chip" onClick={() => handleSuggestionClick(suggestion.text)}>
              <i className={`fas fa-${suggestion.icon}`}></i> {suggestion.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
