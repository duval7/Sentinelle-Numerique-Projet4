"use strict";
const express        = require("express");
const Joi            = require("joi");
const { v4: uuidv4 } = require("uuid");
const axios          = require("axios");
const bus            = require("../engine/bus.client");

const router     = express.Router();
const REPORT_URL = `http://localhost:${process.env.PORT_REPORT || 3002}`;

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
    const response = await axios.get(
      `${REPORT_URL}/report/${req.params.id}`,
      { timeout: 5000 }
    );
    res.json(response.data);
  } catch (err) {
    // Report not found yet — still processing
    if (err.response?.status === 404) {
      return res.json({
        jobId:   req.params.id,
        status:  "pending",
        message: "Analysis in progress. Try again in a few seconds.",
      });
    }
    next(err);
  }
});

module.exports = router;