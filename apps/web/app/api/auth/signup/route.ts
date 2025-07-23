import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { email, password, name } = await request.json();

    // TODO: In production, implement proper user registration logic here
    // For now, this is a placeholder that simulates registration

    if (!email || !password) {
      return NextResponse.json({ error: 'Email and password are required' }, { status: 400 });
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: 'Password must be at least 8 characters long' },
        { status: 400 }
      );
    }

    // Simulate registration delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    // TODO: Check if user already exists
    // TODO: Hash password with bcrypt or similar
    // TODO: Store user in database
    // TODO: Send verification email
    // TODO: Generate secure session token

    // Return mock user data
    return NextResponse.json({
      user: {
        id: 'user_' + Math.random().toString(36).substr(2, 9),
        email,
        name: name || email.split('@')[0],
        role: 'user',
      },
      token: 'mock_session_token_' + Date.now(),
    });
  } catch (error) {
    console.error('Signup error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
