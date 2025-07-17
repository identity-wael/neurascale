import { NextRequest, NextResponse } from "next/server";
import { initAdmin, auth } from "@/lib/firebase-admin";
import { stripe } from "@/lib/stripe";
import { db } from "@/lib/db";

// Initialize Firebase Admin
initAdmin();

export async function POST(request: NextRequest) {
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

    // Get user with subscription
    const user = await db.user.findUnique({
      where: { firebaseUid },
      include: { subscription: true },
    });

    if (!user || !user.subscription?.stripeCustomerId) {
      return NextResponse.json(
        { error: "No subscription found" },
        { status: 404 },
      );
    }

    // Create portal session
    const session = await stripe.billingPortal.sessions.create({
      customer: user.subscription.stripeCustomerId,
      return_url: `${process.env.NEXT_PUBLIC_APP_URL}/billing`,
    });

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error("Error creating portal session:", error);
    return NextResponse.json(
      { error: "Failed to create portal session" },
      { status: 500 },
    );
  }
}
