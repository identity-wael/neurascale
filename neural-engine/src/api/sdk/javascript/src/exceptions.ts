/**
 * NeuraScale SDK Exceptions
 */

export class NeuraScaleError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any,
  ) {
    super(message);
    this.name = "NeuraScaleError";
  }
}

export class AuthenticationError extends NeuraScaleError {
  constructor(message: string = "Authentication failed") {
    super(message, 401);
    this.name = "AuthenticationError";
  }
}

export class AuthorizationError extends NeuraScaleError {
  constructor(message: string = "Insufficient permissions") {
    super(message, 403);
    this.name = "AuthorizationError";
  }
}

export class NotFoundError extends NeuraScaleError {
  constructor(message: string = "Resource not found") {
    super(message, 404);
    this.name = "NotFoundError";
  }
}

export class ValidationError extends NeuraScaleError {
  constructor(
    message: string,
    public details?: any,
  ) {
    super(message, 422);
    this.name = "ValidationError";
  }
}

export class RateLimitError extends NeuraScaleError {
  constructor(
    message: string = "Rate limit exceeded",
    public retryAfter: number = 60,
  ) {
    super(message, 429);
    this.name = "RateLimitError";
  }
}

export class ServerError extends NeuraScaleError {
  constructor(message: string = "Internal server error") {
    super(message, 500);
    this.name = "ServerError";
  }
}

export class ConnectionError extends NeuraScaleError {
  constructor(message: string = "Connection failed") {
    super(message);
    this.name = "ConnectionError";
  }
}

export class TimeoutError extends NeuraScaleError {
  constructor(message: string = "Request timeout") {
    super(message);
    this.name = "TimeoutError";
  }
}
