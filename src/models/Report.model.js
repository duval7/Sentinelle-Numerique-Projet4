"use strict";
const mongoose = require("mongoose");

const ReportSchema = new mongoose.Schema({
  jobId:           { type: String, required: true, unique: true, index: true },
  confidenceScore: { type: Number, min: 0, max: 100, default: null },
  verdict:         {
    type: String,
    enum: ["HIGH", "MEDIUM", "LOW", "UNKNOWN", "ERROR"],
  },
  claimBreakdown:  [mongoose.Schema.Types.Mixed],
  error:           { type: String, default: null },
  computedAt:      { type: Date, default: Date.now },
});

module.exports = mongoose.model("Report", ReportSchema);