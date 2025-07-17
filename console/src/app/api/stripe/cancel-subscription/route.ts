import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { db } from "@/lib/db";
import { initAdmin, auth } from "@/lib/firebase-admin";

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

    // Get user and subscription from database
    const user = await db.user.findUnique({
      where: { firebaseUid },
      include: { subscription: true },
    });

    if (!user || !user.subscription) {
      return NextResponse.json(
        { error: "Subscription not found" },
        { status: 404 },
      );
    }

    const { stripeSubscriptionId } = user.subscription;

    if (!stripeSubscriptionId) {
      return NextResponse.json(
        { error: "No active subscription" },
        { status: 400 },
      );
    }

    // Cancel the subscription at period end
    const subscription = await stripe.subscriptions.update(
      stripeSubscriptionId,
      {
        cancel_at_period_end: true,
      },
    );

    // Update database
    await db.subscription.update({
      where: { id: user.subscription.id },
      data: {
        cancelAtPeriodEnd: true,
      },
    });

    return NextResponse.json({
      success: true,
      subscription: {
        id: subscription.id,
        status: subscription.status,
        cancelAtPeriodEnd: subscription.cancel_at_period_end,
        currentPeriodEnd: (subscription as any).current_period_end,
      },
    });
  } catch (error) {
    console.error("Error canceling subscription:", error);
    return NextResponse.json(
      { error: "Failed to cancel subscription" },
      { status: 500 },
    );
  }
}
