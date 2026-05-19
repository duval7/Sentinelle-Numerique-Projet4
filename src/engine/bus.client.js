"use strict";
require("dotenv").config();
const amqp = require("amqplib");

let connection = null;
let channel    = null;

async function connect(retries = 5, delay = 3000) {
  for (let i = 1; i <= retries; i++) {
    try {
      console.log(`[Bus] Connecting to RabbitMQ (attempt ${i})...`);
      connection = await amqp.connect(process.env.RABBITMQ_URL || "amqp://localhost");
      channel    = await connection.createChannel();
      console.log("[Bus] Connected successfully");
      connection.on("close", () => {
        connection = null;
        channel    = null;
        console.warn("[Bus] Connection lost. Reconnecting...");
        setTimeout(connect, delay);
      });
      return channel;
    } catch (err) {
      console.error(`[Bus] Attempt ${i} failed: ${err.message}`);
      if (i === retries) throw err;
      await new Promise(r => setTimeout(r, delay));
    }
  }
}

async function getChannel() {
  if (!channel) await connect();
  return channel;
}

async function publish(queue, payload) {
  const ch = await getChannel();
  await ch.assertQueue(queue, { durable: true });
  ch.sendToQueue(queue, Buffer.from(JSON.stringify(payload)), { persistent: true });
  console.log(`[Bus] Job ${payload.jobId} published to queue "${queue}"`);
}

async function consume(queue, handler) {
  const ch = await getChannel();
  await ch.assertQueue(queue, { durable: true });
  ch.prefetch(1);
  console.log(`[Bus] Listening on queue "${queue}"...`);
  ch.consume(queue, async (msg) => {
    if (!msg) return;
    try {
      await handler(JSON.parse(msg.content.toString()));
      ch.ack(msg);
    } catch (err) {
      console.error("[Bus] Handler error:", err.message);
      ch.nack(msg, false, false);
    }
  });
}

async function close() {
  if (channel)    await channel.close();
  if (connection) await connection.close();
  console.log("[Bus] Connection closed.");
}

module.exports = { connect, publish, consume, close };