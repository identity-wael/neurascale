import { render as rtlRender, RenderOptions } from "@testing-library/react";
import { ReactElement, ReactNode } from "react";
import "@testing-library/jest-dom";

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, "wrapper"> {
  wrapper?: ({ children }: { children: ReactNode }) => ReactElement;
}

export function render(ui: ReactElement, options: CustomRenderOptions = {}) {
  const { wrapper: Wrapper, ...renderOptions } = options;

  const AllTheProviders = ({ children }: { children: ReactNode }) => {
    if (Wrapper) {
      return <Wrapper>{children}</Wrapper>;
    }
    return <>{children}</>;
  };

  return rtlRender(ui, { wrapper: AllTheProviders, ...renderOptions });
}

// Mock helpers
export const mockConsole = {
  error: jest.fn(),
  warn: jest.fn(),
  log: jest.fn(),
};

// Test utilities
export function createMockRouter(overrides = {}) {
  return {
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
    ...overrides,
  };
}

// Re-export testing library utilities
export * from "@testing-library/react";
export * from "@testing-library/user-event";
export { expect, describe, it, beforeEach, afterEach, vi } from "vitest";
