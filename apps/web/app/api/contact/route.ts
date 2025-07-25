import { NextRequest, NextResponse } from 'next/server';
import nodemailer from 'nodemailer';
import { rateLimit } from '@/lib/rate-limit';

const limiter = rateLimit({
  interval: 60 * 1000, // 60 seconds
  uniqueTokenPerInterval: 500, // Max 500 unique tokens per interval
});

// Function to escape HTML to prevent XSS attacks
function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export async function POST(request: NextRequest) {
  try {
    // Get IP address for rate limiting
    const ip =
      request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || 'unknown';

    // Apply rate limiting (5 requests per minute per IP)
    try {
      await limiter.check(new Response(), 5, ip);
    } catch {
      return NextResponse.json(
        { error: 'Too many requests. Please try again later.' },
        { status: 429 }
      );
    }

    const body = await request.json();
    const { name, email, organization, subject, message } = body;

    // Validate required fields
    if (!name || !email || !subject || !message) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Basic email validation - using a simpler, safer pattern
    // This avoids ReDoS vulnerability while still validating basic email format
    const emailParts = email.split('@');
    if (
      emailParts.length !== 2 ||
      emailParts[0].length === 0 ||
      emailParts[1].length === 0 ||
      !emailParts[1].includes('.') ||
      email.includes(' ')
    ) {
      return NextResponse.json({ error: 'Invalid email address' }, { status: 400 });
    }

    // Log contact form submission (useful for development)
    console.log('Contact form submission:', {
      name,
      email,
      organization,
      subject,
      message,
      timestamp: new Date().toISOString(),
    });

    // Check if email credentials are configured
    if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS) {
      console.warn('Email credentials not configured. Form submission logged but not sent.');
      // In development, you can still return success to test the form
      return NextResponse.json(
        { message: 'Form submission received (email not configured)' },
        { status: 200 }
      );
    }

    // Create transporter
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
      },
    });

    // Email content
    const mailOptions = {
      from: `"${name}" <${email}>`,
      to: 'identity@wael.ai',
      subject: `[NEURASCALE Contact] ${subject} - from ${name}`,
      html: `
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> ${escapeHtml(name)}</p>
        <p><strong>Email:</strong> ${escapeHtml(email)}</p>
        <p><strong>Organization:</strong> ${escapeHtml(organization || 'Not provided')}</p>
        <p><strong>Subject:</strong> ${escapeHtml(subject)}</p>
        <p><strong>Message:</strong></p>
        <p>${escapeHtml(message).replace(/\n/g, '<br>')}</p>
      `,
      text: `
        New Contact Form Submission

        Name: ${name}
        Email: ${email}
        Organization: ${organization || 'Not provided'}
        Subject: ${subject}

        Message:
        ${message}
      `,
    };

    // Send email
    await transporter.sendMail(mailOptions);

    return NextResponse.json({ message: 'Email sent successfully' }, { status: 200 });
  } catch (error) {
    console.error('Error sending email:', error);
    return NextResponse.json({ error: 'Failed to send email' }, { status: 500 });
  }
}
