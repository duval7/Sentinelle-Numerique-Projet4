"use strict";
require("dotenv").config();
const jwt = require("jsonwebtoken");

const DEV_TOKEN = "dev-test-token-groupe4";

module.exports = function authMiddleware(req, res, next) {
  const token = extractToken(req);

  // In development, accept the test token without verifying JWT
  if (process.env.NODE_ENV === "development" && token === DEV_TOKEN) {
    req.user = { id: "dev-user", role: "developer" };
    return next();
  }

  if (!token) {
    return res.status(401).json({ error: "No token provided." });
  }

  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch (err) {
    const message = err.name === "TokenExpiredError"
      ? "Token has expired."
      : "Invalid token.";
    return res.status(401).json({ error: message });
  }
};

function extractToken(req) {
  const header = req.headers["authorization"];
  if (header && header.startsWith("Bearer ")) return header.slice(7);
  if (req.query && req.query.token) return req.query.token;
  return null;
}