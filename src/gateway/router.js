"use strict";
const express        = require("express");
const Joi            = require("joi");
const { v4: uuidv4 } = require("uuid");
const bus            = require("../engine/bus.client");

const router = express.Router();

// Validation: user must send either a URL or a text (minimum 50 characters)
const schema = Joi.object({
  url:  Joi.string().uri().optional(),
  text: Joi.string().min(50).max(10000).optional(),
}).or("url", "text").messages({
  "object.missing": "Provide either a URL or article text.",
});

// POST /api/analyze
router.post("/analyze", async (req, res, next) => {
  try {
    const { error, value } = schema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const jobId = uuidv4();

    await bus.publish(process.env.RABBITMQ_QUEUE || "analysis_queue", {
      jobId,
      userId:      req.user?.id || "anonymous",
      url:         value.url  || null,
      text:        value.text || null,
      submittedAt: new Date().toISOString(),
    });

    res.status(202).json({
      jobId,
      message: "Analysis started. Poll /api/result/:id to get the result.",
    });
  } catch (err) {
    next(err);
  }
});

// GET /api/result/:id
router.get("/result/:id", async (req, res, next) => {
  try {
    // TODO Sprint 3: query MongoDB for the report with this jobId
    res.json({
      jobId:   req.params.id,
      status:  "pending",
      message: "Result store coming in Sprint 3.",
    });
  } catch (err) {
    next(err);
  }
});

module.exports = router;