import { type NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"
import { v4 as uuidv4 } from "uuid"
import { CarDiagnosisChat } from "@/lib/diagnose-llm"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { manufacturer, model, year } = body

    // Validate input
    if (!manufacturer || !model || !year) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    // Generate a unique session ID
    const sessionId = `session_${uuidv4().slice(0, 8)}`

    // Create a new chat instance
    const chat = new CarDiagnosisChat()
    const response = chat.setCarDetails(manufacturer, model, year)

    // Store the chat session (in memory for now)
    // In a real app, you'd store this in a database
    global.chatSessions = global.chatSessions || {}
    global.chatSessions[sessionId] = chat

    // Create session metadata
    const sessionMetadata = {
      id: sessionId,
      user_id: cookies().get("user_id")?.value || "anonymous",
      car_details: { manufacturer, model, year },
      created_at: new Date().toISOString(),
      messages: [
        {
          role: "assistant",
          content: response.message,
          timestamp: new Date().toISOString(),
          car_image: response.car_image,
        },
      ],
    }

    // Save session metadata (in memory for now)
    global.sessionMetadata = global.sessionMetadata || {}
    global.sessionMetadata[sessionId] = sessionMetadata

    // Set user_id cookie if not present
    const responseObj = NextResponse.json({
      session_id: sessionId,
      message: response.message,
      car_image: response.car_image,
      car_details: { manufacturer, model, year },
    })

    if (!cookies().get("user_id")) {
      const newUserId = `user_${uuidv4().slice(0, 8)}`
      responseObj.cookies.set("user_id", newUserId, { maxAge: 31536000 }) // 1 year
    }

    return responseObj
  } catch (error) {
    console.error("Error starting chat:", error)
    return NextResponse.json({ error: "Failed to start chat" }, { status: 500 })
  }
}
