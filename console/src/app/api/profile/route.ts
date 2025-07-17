import { NextRequest, NextResponse } from "next/server";
import { cookies, headers } from "next/headers";
import { db } from "@/lib/db";

async function verifyAuth(request: NextRequest) {
  // For development, we'll use a simpler auth check
  // This should be replaced with proper Firebase Admin SDK verification in production
  const headersList = await headers();
  const authorization = headersList.get("authorization");

  if (!authorization?.startsWith("Bearer ")) {
    return null;
  }

  // Extract the token (this is temporary - should verify with Firebase Admin)
  const token = authorization.split("Bearer ")[1];

  // For now, we'll decode the JWT without verification (NOT for production!)
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const payload = JSON.parse(Buffer.from(parts[1], "base64").toString());
    return payload;
  } catch (error) {
    console.error("Token decode error:", error);
    return null;
  }
}

export async function GET(request: NextRequest) {
  try {
    const decodedToken = await verifyAuth(request);

    if (!decodedToken) {
      return NextResponse.json(
        { error: "Unauthorized - No valid token" },
        { status: 401 },
      );
    }

    console.log("Decoded token:", decodedToken);

    // First try to find by Firebase UID
    let user = await db.user.findUnique({
      where: {
        firebaseUid: decodedToken.user_id || decodedToken.uid,
      },
      select: {
        id: true,
        email: true,
        name: true,
        image: true,
        organization: true,
        department: true,
        role: true,
        createdAt: true,
        lastLoginAt: true,
      },
    });

    // If not found by UID, try by email and create if necessary
    if (!user && decodedToken.email) {
      user = await db.user.findUnique({
        where: {
          email: decodedToken.email,
        },
        select: {
          id: true,
          email: true,
          name: true,
          image: true,
          organization: true,
          department: true,
          role: true,
          createdAt: true,
          lastLoginAt: true,
        },
      });

      // Create user if not exists
      if (!user) {
        user = await db.user.create({
          data: {
            email: decodedToken.email,
            firebaseUid: decodedToken.user_id || decodedToken.uid,
            name: decodedToken.name || null,
            image: decodedToken.picture || null,
            lastLoginAt: new Date(),
          },
          select: {
            id: true,
            email: true,
            name: true,
            image: true,
            organization: true,
            department: true,
            role: true,
            createdAt: true,
            lastLoginAt: true,
          },
        });
      }
    }

    if (!user) {
      return NextResponse.json(
        { error: "User not found and could not be created" },
        { status: 404 },
      );
    }

    // Update last login
    await db.user.update({
      where: { id: user.id },
      data: { lastLoginAt: new Date() },
    });

    return NextResponse.json(user);
  } catch (error) {
    console.error("Error fetching profile:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error.message },
      { status: 500 },
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const decodedToken = await verifyAuth(request);

    if (!decodedToken) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { name, organization, department } = body;

    const updatedUser = await db.user.update({
      where: {
        firebaseUid: decodedToken.user_id || decodedToken.uid,
      },
      data: {
        name,
        organization,
        department,
      },
      select: {
        id: true,
        email: true,
        name: true,
        image: true,
        organization: true,
        department: true,
        role: true,
        createdAt: true,
        lastLoginAt: true,
      },
    });

    return NextResponse.json(updatedUser);
  } catch (error) {
    console.error("Error updating profile:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error.message },
      { status: 500 },
    );
  }
}
