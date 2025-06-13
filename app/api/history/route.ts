import { type NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"

export async function GET(request: NextRequest) {
  try {
    const userId = cookies().get("user_id")?.value

    if (!userId) {
      return NextResponse.json({ sessions: [] })
    }

    // Get user's sessions
    const sessions = listUserSessions(userId)

    return NextResponse.json({ sessions })
  } catch (error) {
    console.error("Error getting history:", error)
    return NextResponse.json({ error: "Failed to get history" }, { status: 500 })
  }
}

function listUserSessions(userId: string) {
  global.sessionMetadata = global.sessionMetadata || {}

  // Filter sessions by user ID and create summaries
  const userSessions = Object.values(global.sessionMetadata)
    .filter((session: any) => session.user_id === userId)
    .map((session: any) => ({
      id: session.id,
      car_details: session.car_details,
      created_at: session.created_at,
      last_message: session.last_message,
      message_count: session.message_count,
    }))
    .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  return userSessions
}
