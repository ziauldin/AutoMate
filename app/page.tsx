"use client"

import { useState } from "react"
import Sidebar from "@/components/sidebar"
import WelcomeScreen from "@/components/welcome-screen"
import ChatInterface from "@/components/chat-interface"
import { useTheme } from "next-themes"

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showWelcome, setShowWelcome] = useState(true)
  const [messages, setMessages] = useState<any[]>([])
  const { theme, setTheme } = useTheme()

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const startNewChat = () => setShowWelcome(true)

  const handleStartChat = (manufacturer: string, model: string, year: number) => {
    setMessages([{
      content: `Chat started for ${year} ${manufacturer} ${model}`,
      role: "assistant"
    }])
    setShowWelcome(false)
  }

  const handleSendMessage = (message: string) => {
    if (!message.trim()) return
    
    setMessages(prev => [...prev, {
      content: message,
      role: "user"
    }])
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        content: "This is a simulated AI response",
        role: "assistant"
      }])
    }, 1000)
  }

  return (
    <div className="app-container">
      <Sidebar 
        isOpen={sidebarOpen} 
        onNewChat={startNewChat}
      />
      
      <div className="main-content">
        {showWelcome ? (
          <WelcomeScreen onStartChat={handleStartChat} />
        ) : (
          <ChatInterface 
            messages={messages}
            onSendMessage={handleSendMessage}
            onToggleSidebar={toggleSidebar}
          />
        )}
      </div>
    </div>
  )
}