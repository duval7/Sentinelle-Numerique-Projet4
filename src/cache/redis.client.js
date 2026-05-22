"use strict";
require("dotenv").config();
const Redis = require("ioredis");

const client = new Redis({
  host: process.env.REDIS_HOST || "localhost",
  port: process.env.REDIS_PORT || 6379,
});

client.on("connect", () => console.log("[Redis] Connected"));
client.on("error",   (err) => console.error("[Redis] Error:", err.message));

const TTL = 6 * 60 * 60; // 6 hours in seconds

async function get(key) {
  try {
    const value = await client.get(key);
    return value ? JSON.parse(value) : null;
  } catch (err) {
    console.error("[Redis] GET error:", err.message);
    return null;
  }
}

async function set(key, value, ttl = TTL) {
  try {
    await client.setex(key, ttl, JSON.stringify(value));
  } catch (err) {
    console.error("[Redis] SET error:", err.message);
  }
}

async function del(key) {
  try {
    await client.del(key);
  } catch (err) {
    console.error("[Redis] DEL error:", err.message);
  }
}

module.exports = { client, get, set, del };