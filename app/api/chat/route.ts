import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { session_id, message } = body

    // Validate input
    if (!session_id || !message) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    // Get chat session
    global.chatSessions = global.chatSessions || {}
    const chat = global.chatSessions[session_id]

    if (!chat) {
      return NextResponse.json({ error: "Session not found" }, { status: 404 })
    }

    // Get diagnosis
    const response = await chat.getDiagnosis(message)

    // Get recommendations if diagnosis is complete
    let products = []
    if (chat.diagnosis_complete) {
      const keywords = chat.extractRecommendationKeywords()
      products = getRecommendations(keywords)
    }

    // Update session history
    updateSessionHistory(session_id, message, response.message, response.car_image, products)

    return NextResponse.json({
      message: response.message,
      car_image: response.car_image,
      products: products,
    })
  } catch (error) {
    console.error("Error in chat:", error)
    return NextResponse.json({ error: "Failed to process message" }, { status: 500 })
  }
}

// Helper functions
function getRecommendations(keywords: string[]) {
  // In a real app, this would query a database
  // For now, return mock data
  if (!keywords || keywords.length === 0) {
    return []
  }

  const mockProducts = [
    { title: "Oil Filter Premium", price: 12.99, category: "Filters" },
    { title: "Synthetic Oil 5W-30", price: 32.99, category: "Fluids" },
    { title: "Brake Pads (Front)", price: 45.99, category: "Brakes" },
    { title: "Air Filter", price: 15.99, category: "Filters" },
    { title: "Spark Plugs Set", price: 28.99, category: "Ignition" },
  ]

  // Filter products based on keywords
  return mockProducts
    .filter((product) =>
      keywords.some(
        (keyword) => product.title.toLowerCase().includes(keyword) || product.category.toLowerCase().includes(keyword),
      ),
    )
    .slice(0, 3) // Return top 3 matches
}

function updateSessionHistory(
  sessionId: string,
  userMessage: string,
  assistantMessage: string,
  carImage?: string,
  products?: any[],
) {
  global.sessionMetadata = global.sessionMetadata || {}
  const session = global.sessionMetadata[sessionId]

  if (!session) return

  // Add user message
  session.messages.push({
    role: "user",
    content: userMessage,
    timestamp: new Date().toISOString(),
  })

  // Add assistant message
  session.messages.push({
    role: "assistant",
    content: assistantMessage,
    timestamp: new Date().toISOString(),
    car_image: carImage,
    products: products,
  })

  // Update last message and count
  session.last_message = assistantMessage.slice(0, 50) + (assistantMessage.length > 50 ? "..." : "")
  session.message_count = session.messages.length
}
