"use strict";
require("dotenv").config();
const express  = require("express");
const mongoose = require("mongoose");
const Report   = require("../models/Report.model");

const app  = express();
const PORT = process.env.PORT_REPORT || 3002;

app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI || "mongodb://localhost:27017/sentinelle")
  .then(() => console.log("[Report] MongoDB connected"))
  .catch(err => console.error("[Report] MongoDB error:", err.message));

// Save a new report
app.post("/report", async (req, res) => {
  try {
    const { jobId, confidenceScore, verdict, claimBreakdown, error } = req.body;
    const report = await Report.findOneAndUpdate(
      { jobId },
      { jobId, confidenceScore, verdict, claimBreakdown, error },
      { upsert: true, new: true }
    );
    res.status(201).json(report);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get a report by jobId
app.get("/report/:jobId", async (req, res) => {
  try {
    const report = await Report.findOne({ jobId: req.params.jobId });
    if (!report) {
      return res.status(404).json({ status: "pending" });
    }
    res.json(report);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "report" });
});

app.listen(PORT, () => console.log(`[Report] Running on http://localhost:${PORT}`));

module.exports = app;