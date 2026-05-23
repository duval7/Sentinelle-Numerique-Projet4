"use strict";
const mongoose = require("mongoose");

const ClaimSchema = new mongoose.Schema({
  jobId:          { type: String, required: true, index: true },
  text:           { type: String, required: true },
  entities:       [String],
  numericalValue: { type: Number, default: null },
  wikiScore:      { type: Number, default: 0, min: 0, max: 1 },
  newsScore:      { type: Number, default: 0, min: 0, max: 1 },
  claimScore:     { type: Number, default: 0, min: 0, max: 1 },
  verdict:        {
    type: String,
    enum: ["HIGH", "MEDIUM", "LOW", "UNKNOWN"],
    default: "UNKNOWN"
  },
  wikiSources:    [String],
  newsSources:    [String],
  createdAt:      { type: Date, default: Date.now },
});

module.exports = mongoose.model("Claim", ClaimSchema);