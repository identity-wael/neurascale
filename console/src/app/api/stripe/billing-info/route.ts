import { NextRequest, NextResponse } from "next/server";
import { initAdmin, auth } from "@/lib/firebase-admin";
import { db } from "@/lib/db";

// Initialize Firebase Admin
initAdmin();

export async function GET(request: NextRequest) {
  try {
    // Get the authorization header
    const authHeader = request.headers.get("authorization");
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Verify the Firebase token
    const token = authHeader.substring(7);
    const decodedToken = await auth().verifyIdToken(token);
    const firebaseUid = decodedToken.uid;

    // Get user with subscription and invoices
    const user = await db.user.findUnique({
      where: { firebaseUid },
      include: {
        subscription: true,
        invoices: {
          orderBy: { createdAt: "desc" },
          take: 10,
        },
      },
    });

    if (!user) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    return NextResponse.json({
      subscription: user.subscription,
      invoices: user.invoices,
    });
  } catch (error) {
    console.error("Error fetching billing info:", error);
    return NextResponse.json(
      { error: "Failed to fetch billing info" },
      { status: 500 },
    );
  }
}
