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

    // Get user from database
    const user = await db.user.findUnique({
      where: { firebaseUid },
      include: { subscription: true },
    });

    if (!user) {
      return NextResponse.json({ error: "User not found" }, { status: 404 });
    }

    const { priceId, planKey } = await request.json();

    // Check if user already has a Stripe customer ID
    let customerId = user.subscription?.stripeCustomerId;

    if (!customerId) {
      // Create a new Stripe customer
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: {
          userId: user.id,
          firebaseUid: user.firebaseUid,
        },
      });
      customerId = customer.id;

      // Create or update subscription record
      await db.subscription.upsert({
        where: { userId: user.id },
        update: { stripeCustomerId: customerId },
        create: {
          userId: user.id,
          stripeCustomerId: customerId,
          plan: "FREE",
        },
      });
    }

    // Create checkout session
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      payment_method_types: ["card"],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: "subscription",
      success_url: `${process.env.NEXT_PUBLIC_APP_URL}/billing?success=true&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing?canceled=true`,
      metadata: {
        userId: user.id,
        planKey,
      },
    });

    return NextResponse.json({ sessionUrl: session.url });
  } catch (error) {
    console.error("Error creating checkout session:", error);
    return NextResponse.json(
      { error: "Failed to create checkout session" },
      { status: 500 },
    );
  }
}
