import { NextRequest, NextResponse } from "next/server";
import { headers } from "next/headers";
import Stripe from "stripe";
import { stripe } from "@/lib/stripe";
import { db } from "@/lib/db";

const relevantEvents = new Set([
  "checkout.session.completed",
  "customer.subscription.created",
  "customer.subscription.updated",
  "customer.subscription.deleted",
  "invoice.payment_succeeded",
  "invoice.payment_failed",
]);

export async function POST(request: NextRequest) {
  const body = await request.text();
  const headersList = await headers();
  const sig = headersList.get("stripe-signature") as string;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!,
    );
  } catch (err) {
    console.error("Webhook signature verification failed:", err);
    return NextResponse.json(
      { error: "Webhook signature verification failed" },
      { status: 400 },
    );
  }

  if (relevantEvents.has(event.type)) {
    try {
      switch (event.type) {
        case "checkout.session.completed": {
          const checkoutSession = event.data.object as Stripe.Checkout.Session;

          // Get the user and plan information
          const userId = checkoutSession.metadata?.userId;
          const planKey = checkoutSession.metadata?.planKey;

          if (userId && planKey) {
            // Update the subscription
            await db.subscription.update({
              where: { userId },
              data: {
                stripeSubscriptionId: checkoutSession.subscription as string,
                stripePriceId: checkoutSession.metadata?.priceId,
                plan: planKey as any,
                status: "ACTIVE",
              },
            });
          }
          break;
        }

        case "customer.subscription.updated": {
          const subscription = event.data.object as Stripe.Subscription;

          // Update subscription status
          await db.subscription.update({
            where: { stripeSubscriptionId: subscription.id },
            data: {
              status: subscription.status.toUpperCase() as any,
              currentPeriodStart: new Date(
                subscription.current_period_start * 1000,
              ),
              currentPeriodEnd: new Date(
                subscription.current_period_end * 1000,
              ),
              cancelAtPeriodEnd: subscription.cancel_at_period_end,
            },
          });
          break;
        }

        case "customer.subscription.deleted": {
          const subscription = event.data.object as Stripe.Subscription;

          // Update subscription to canceled
          await db.subscription.update({
            where: { stripeSubscriptionId: subscription.id },
            data: {
              status: "CANCELED",
              plan: "FREE",
            },
          });
          break;
        }

        case "invoice.payment_succeeded": {
          const invoice = event.data.object as Stripe.Invoice;

          // Record the invoice
          const user = await db.user.findFirst({
            where: {
              subscription: {
                stripeCustomerId: invoice.customer as string,
              },
            },
          });

          if (user) {
            await db.invoice.create({
              data: {
                stripeInvoiceId: invoice.id,
                userId: user.id,
                amountPaid: invoice.amount_paid || 0,
                amountDue: invoice.amount_due || 0,
                currency: invoice.currency,
                status: invoice.status || "paid",
                hostedInvoiceUrl: invoice.hosted_invoice_url || null,
                invoicePdf: invoice.invoice_pdf || null,
                periodStart: invoice.period_start
                  ? new Date(invoice.period_start * 1000)
                  : new Date(),
                periodEnd: invoice.period_end
                  ? new Date(invoice.period_end * 1000)
                  : new Date(),
              },
            });
          }
          break;
        }

        case "invoice.payment_failed": {
          const invoice = event.data.object as Stripe.Invoice;

          // Update subscription status if payment fails
          const subscription = await db.subscription.findFirst({
            where: { stripeCustomerId: invoice.customer as string },
          });

          if (subscription) {
            await db.subscription.update({
              where: { id: subscription.id },
              data: { status: "PAST_DUE" },
            });
          }
          break;
        }
      }
    } catch (error) {
      console.error("Error processing webhook:", error);
      return NextResponse.json(
        { error: "Webhook processing failed" },
        { status: 500 },
      );
    }
  }

  return NextResponse.json({ received: true });
}
