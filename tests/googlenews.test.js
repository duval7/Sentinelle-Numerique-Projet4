"use strict";

jest.mock("../src/cache/redis.client", () => ({
  get: jest.fn().mockResolvedValue(null),
  set: jest.fn().mockResolvedValue(null),
}));

jest.mock("axios", () => ({
  get: jest.fn(),
}));

const axios  = require("axios");
const { search } = require("../src/services/googlenews.service");

describe("GoogleNewsService", () => {

  test("returns score 0 when no articles found", async () => {
    axios.get.mockResolvedValueOnce({ data: { articles: [] } });
    const result = await search("unknownxyz123");
    expect(result.score).toBe(0);
    expect(result.sources).toHaveLength(0);
  });

  test("returns sources when articles found", async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        articles: [
          { title: "Cameroon GDP grows", url: "https://news.com/1", publishedAt: new Date().toISOString() },
          { title: "Africa economy news", url: "https://news.com/2", publishedAt: new Date().toISOString() },
        ],
      },
    });
    const result = await search("Cameroon GDP");
    expect(result.sources.length).toBeGreaterThan(0);
  });

  test("returns score 0 on API error", async () => {
    axios.get.mockRejectedValueOnce(new Error("API error"));
    const result = await search("test");
    expect(result.score).toBe(0);
  });

});