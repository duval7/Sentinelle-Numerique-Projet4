"use strict";
const { search } = require("../src/services/wikipedia.service");

jest.mock("../src/cache/redis.client", () => ({
  get: jest.fn().mockResolvedValue(null),
  set: jest.fn().mockResolvedValue(null),
}));

jest.mock("axios", () => ({
  get: jest.fn(),
}));

const axios = require("axios");

describe("WikipediaService", () => {

  test("returns score 0 when no pages found", async () => {
    axios.get.mockResolvedValueOnce({ data: { pages: [] } });
    const result = await search("unknownxyz123");
    expect(result.score).toBe(0);
    expect(result.sources).toHaveLength(0);
  });

  test("returns a score and source when page found", async () => {
    axios.get
      .mockResolvedValueOnce({ data: { pages: [{ key: "Cameroon" }] } })
      .mockResolvedValueOnce({ data: { extract: "Cameroon is a country in Central Africa." } });

    const result = await search("Cameroon Africa");
    expect(result.score).toBeGreaterThan(0);
    expect(result.sources[0]).toContain("wikipedia.org");
  });

  test("returns score 0 on API error", async () => {
    axios.get.mockRejectedValueOnce(new Error("Network error"));
    const result = await search("test");
    expect(result.score).toBe(0);
  });

});