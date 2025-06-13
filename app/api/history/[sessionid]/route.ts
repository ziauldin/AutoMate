import { type NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"

export async function GET(request: NextRequest, { params }: { params: { sessionId: string } }) {
  try {
    const sessionId = params.sessionId
    const userId = cookies().get("user_id")?.value

    if (!userId) {
      return NextResponse.json({ error: "User not authenticated" }, { status: 401 })
    }

    // Get session
    global.sessionMetadata = global.sessionMetadata || {}
    const session = global.sessionMetadata[sessionId]

    if (!session || session.user_id !== userId) {
      return NextResponse.json({ error: "Session not found" }, { status: 404 })
    }

    return NextResponse.json(session)
  } catch (error) {
    console.error("Error getting session:", error)
    return NextResponse.json({ error: "Failed to get session" }, { status: 500 })
  }
}
