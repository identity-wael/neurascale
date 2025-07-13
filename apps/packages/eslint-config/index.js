module.exports = {
  extends: [
    "next/core-web-vitals"
  ],
  env: {
    browser: true,
    node: true,
    es2022: true
  },
  rules: {
    // General rules to keep code clean
    "no-console": "warn",
    "prefer-const": "error",
    "no-var": "error"
  },
  settings: {
    react: {
      version: "detect"
    }
  }
};