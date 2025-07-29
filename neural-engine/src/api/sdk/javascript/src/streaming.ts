/**
 * Real-time streaming client for NeuraScale
 */

import WebSocket from "ws";
import { EventEmitter } from "events";
import { WebSocketConfig, StreamFrame } from "./types";
import { ConnectionError } from "./exceptions";

export class StreamClient extends EventEmitter {
  private ws?: WebSocket;
  private config: WebSocketConfig;
  private reconnectAttempts: number = 0;
  private reconnectTimer?: NodeJS.Timeout;

  constructor(config: WebSocketConfig) {
    super();
    this.config = {
      reconnect: true,
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      ...config,
    };
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const url = `${this.config.url}?token=${this.config.token}`;
        this.ws = new WebSocket(url);

        this.ws.on("open", () => {
          this.reconnectAttempts = 0;
          this.emit("connected");
          resolve();
        });

        this.ws.on("message", (data: WebSocket.Data) => {
          try {
            const frame = JSON.parse(data.toString());
            this.emit("data", frame);
          } catch (error) {
            this.emit("error", new Error("Failed to parse message"));
          }
        });

        this.ws.on("error", (error: Error) => {
          this.emit("error", error);
          reject(new ConnectionError(`WebSocket error: ${error.message}`));
        });

        this.ws.on("close", (code: number, reason: string) => {
          this.emit("disconnected", { code, reason });
          this.handleReconnect();
        });
      } catch (error: any) {
        reject(new ConnectionError(`Failed to connect: ${error.message}`));
      }
    });
  }

  private handleReconnect(): void {
    if (!this.config.reconnect) return;

    if (this.reconnectAttempts >= (this.config.maxReconnectAttempts || 10)) {
      this.emit("error", new Error("Max reconnection attempts reached"));
      return;
    }

    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => {
      this.emit("reconnecting", this.reconnectAttempts);
      this.connect().catch((error) => {
        this.emit("error", error);
      });
    }, this.config.reconnectInterval);
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
  }

  send(message: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new ConnectionError("WebSocket is not connected");
    }

    this.ws.send(JSON.stringify(message));
  }

  // Convenience method for subscribing to a session
  subscribeToSession(sessionId: string, channels?: number[]): void {
    this.send({
      type: "subscribe",
      sessionId,
      channels: channels || "all",
    });
  }

  unsubscribeFromSession(sessionId: string): void {
    this.send({
      type: "unsubscribe",
      sessionId,
    });
  }

  // Stream neural data with async iterator
  async *streamData(): AsyncGenerator<StreamFrame, void, unknown> {
    const frames: StreamFrame[] = [];
    let resolver: ((value: IteratorResult<StreamFrame>) => void) | null = null;

    const dataHandler = (frame: StreamFrame) => {
      if (resolver) {
        resolver({ value: frame, done: false });
        resolver = null;
      } else {
        frames.push(frame);
      }
    };

    this.on("data", dataHandler);

    try {
      while (true) {
        if (frames.length > 0) {
          yield frames.shift()!;
        } else {
          yield await new Promise<StreamFrame>((resolve) => {
            resolver = (result) => {
              if (!result.done) {
                resolve(result.value);
              }
            };
          });
        }
      }
    } finally {
      this.off("data", dataHandler);
    }
  }
}

// Browser-compatible version
export class BrowserStreamClient extends EventEmitter {
  private ws?: WebSocket;
  private config: WebSocketConfig;

  constructor(config: WebSocketConfig) {
    super();
    this.config = config;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const url = `${this.config.url}?token=${this.config.token}`;
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          this.emit("connected");
          resolve();
        };

        this.ws.onmessage = (event: MessageEvent) => {
          try {
            const frame = JSON.parse(event.data);
            this.emit("data", frame);
          } catch (error) {
            this.emit("error", new Error("Failed to parse message"));
          }
        };

        this.ws.onerror = (event: Event) => {
          const error = new ConnectionError("WebSocket error");
          this.emit("error", error);
          reject(error);
        };

        this.ws.onclose = (event: CloseEvent) => {
          this.emit("disconnected", {
            code: event.code,
            reason: event.reason,
          });
        };
      } catch (error: any) {
        reject(new ConnectionError(`Failed to connect: ${error.message}`));
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
  }

  send(message: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new ConnectionError("WebSocket is not connected");
    }

    this.ws.send(JSON.stringify(message));
  }
}
