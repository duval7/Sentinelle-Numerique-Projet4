"use strict";
const { Pool } = require("pg");

const pool = new Pool({
  host:     process.env.PG_HOST     || "localhost",
  port:     process.env.PG_PORT     || 5432,
  user:     process.env.PG_USER     || "postgres",
  password: process.env.PG_PASSWORD || "yourpassword",
  database: process.env.PG_DATABASE || "sentinelle_articles",
});

async function initTable() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS articles (
      id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      job_id       UUID NOT NULL UNIQUE,
      source_url   TEXT,
      raw_text     TEXT,
      submitted_at TIMESTAMPTZ DEFAULT NOW(),
      status       VARCHAR(20) DEFAULT 'PENDING'
    );
  `);
  console.log("[Article] Table ready.");
}

async function create({ jobId, sourceUrl, rawText }) {
  const res = await pool.query(
    `INSERT INTO articles (job_id, source_url, raw_text)
     VALUES ($1, $2, $3) RETURNING *`,
    [jobId, sourceUrl || null, rawText || null]
  );
  return res.rows[0];
}

async function updateStatus(jobId, status) {
  const res = await pool.query(
    `UPDATE articles SET status = $1 WHERE job_id = $2 RETURNING *`,
    [status, jobId]
  );
  return res.rows[0];
}

async function findByJobId(jobId) {
  const res = await pool.query(
    `SELECT * FROM articles WHERE job_id = $1`,
    [jobId]
  );
  return res.rows[0] || null;
}

module.exports = { initTable, create, updateStatus, findByJobId };