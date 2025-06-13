import Image from "next/image"
import type { Message } from "@/types"

interface MessageProps {
  message: Message
}

export default function MessageComponent({ message }: MessageProps) {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  return (
    <div className={`message ${message.role === "user" ? "user" : "bot"}`}>
      <div className="message-avatar">
        <i className={`fas fa-${message.role === "user" ? "user" : "robot"}`}></i>
      </div>
      <div>
        <div className="message-content">
          <p>{message.content}</p>

          {message.car_image && (
            <div className="car-image-container">
              <Image
                src={message.car_image || "/placeholder.svg"}
                alt="Car"
                width={400}
                height={225}
                className="car-image"
              />
            </div>
          )}

          {message.products && message.products.length > 0 && (
            <div className="products-container">
              <div className="products-title">
                <i className="fas fa-shopping-cart"></i> Recommended Parts
              </div>
              {message.products.map((product, index) => (
                <div key={index} className="product-item">
                  <div className="product-info">
                    <div className="product-title">{product.title}</div>
                    <div className="product-category">{product.category}</div>
                  </div>
                  <div className="product-price">${product.price}</div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="message-timestamp">{formatTimestamp(message.timestamp)}</div>
      </div>
    </div>
  )
}
