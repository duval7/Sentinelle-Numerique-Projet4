"use strict";
require("dotenv").config();
const express      = require("express");
const cors         = require("cors");
const helmet       = require("helmet");
const morgan       = require("morgan");
const rateLimit    = require("express-rate-limit");
const authMiddleware = require("./auth.middleware");
const router         = require("./router");

const app  = express();
const PORT = process.env.PORT_GATEWAY || 3000;

// ── Security ──────────────────────────────────────────────
app.use(helmet());
app.use(cors({
  origin: process.env.NODE_ENV === "production"
    ? "https://yourdomain.com"
    : ["http://localhost:3000", "http://localhost:5173"],
  methods: ["GET", "POST"],
}));

// ── Logging ───────────────────────────────────────────────
app.use(morgan("dev"));

// ── Body parsing ──────────────────────────────────────────
app.use(express.json({ limit: "1mb" }));

// ── Global rate limiter: 100 requests / 15 min per IP ────
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max:      100,
  message:  { error: "Too many requests. Please try again later." },
}));

// ── Public health check ───────────────────────────────────
app.get("/health", (req, res) => {
  res.json({
    status:  "ok",
    service: "api-gateway",
    uptime:  process.uptime(),
    time:    new Date().toISOString(),
  });
});

// ── Protected routes — require JWT ────────────────────────
app.use("/api", authMiddleware);

// ── Stricter limit on /api/analyze: 10 req / min ─────────
app.use("/api/analyze", rateLimit({
  windowMs: 60 * 1000,
  max:      10,
  message:  { error: "Analysis rate limit exceeded. Wait before submitting again." },
}));

app.use("/api", router);

// ── 404 ───────────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({
    error: `Route ${req.method} ${req.path} not found.`,
  });
});

// ── Global error handler ──────────────────────────────────
app.use((err, req, res, _next) => {
  console.error("[Gateway Error]", err.message);
  res.status(err.status || 500).json({
    error: err.message || "Internal server error.",
  });
});

// ── Start ─────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`[Gateway] Running on http://localhost:${PORT}`);
  console.log(`[Gateway] Environment: ${process.env.NODE_ENV || "development"}`);
});

module.exports = app;