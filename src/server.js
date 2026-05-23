"use strict";
require("dotenv").config();
const express    = require("express");
const wikiRouter = require("./services/wikipedia.service");
const newsRouter = require("./services/googlenews.service");

const app  = express();
const PORT = process.env.PORT_ENGINE || 3001;

app.use(express.json());

// Mount Boris's service routes
app.use("/wiki", wikiRouter);
app.use("/news", newsRouter);

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "engine-server" });
});

app.listen(PORT, () => {
  console.log(`[Server] Running on http://localhost:${PORT}`);
});

module.exports = app;