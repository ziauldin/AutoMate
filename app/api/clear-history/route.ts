import { type NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"

export async function POST(request: NextRequest) {
  try {
    const userId = cookies().get("user_id")?.value

    if (!userId) {
      return NextResponse.json({ error: "User not authenticated" }, { status: 401 })
    }

    // Clear user's sessions
    clearUserSessions(userId)

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error clearing history:", error)
    return NextResponse.json({ error: "Failed to clear history" }, { status: 500 })
  }
}

function clearUserSessions(userId: string) {
  global.sessionMetadata = global.sessionMetadata || {}

  // Filter out sessions for this user
  Object.keys(global.sessionMetadata).forEach((sessionId) => {
    if (global.sessionMetadata[sessionId].user_id === userId) {
      delete global.sessionMetadata[sessionId]

      // Also delete chat session if it exists
      if (global.chatSessions && global.chatSessions[sessionId]) {
        delete global.chatSessions[sessionId]
      }
    }
  })
}
