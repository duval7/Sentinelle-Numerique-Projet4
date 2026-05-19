"use strict";
const { aggregate, getVerdict } = require("../src/engine/aggregator");

describe("getVerdict", () => {
  test("returns HIGH for score >= 70",  () => expect(getVerdict(70)).toBe("HIGH"));
  test("returns MEDIUM for score >= 40",() => expect(getVerdict(50)).toBe("MEDIUM"));
  test("returns LOW for score < 40",    () => expect(getVerdict(20)).toBe("LOW"));
});

describe("aggregate", () => {
  test("returns UNKNOWN when no claims", () => {
    const r = aggregate("job-1", []);
    expect(r.verdict).toBe("UNKNOWN");
    expect(r.confidenceScore).toBe(0);
  });

  test("returns 100% for perfect scores", () => {
    const claims = [{ text: "test", entities: [], numericalValue: null,
      wikiScore: 1, newsScore: 1, wikiSources: [], newsSources: [] }];
    const r = aggregate("job-2", claims);
    expect(r.confidenceScore).toBe(100);
    expect(r.verdict).toBe("HIGH");
  });

  test("averages multiple claims correctly", () => {
    const claims = [
      { text: "A", entities: [], numericalValue: null, wikiScore: 1, newsScore: 1, wikiSources: [], newsSources: [] },
      { text: "B", entities: [], numericalValue: null, wikiScore: 0, newsScore: 0, wikiSources: [], newsSources: [] },
    ];
    const r = aggregate("job-3", claims);
    expect(r.confidenceScore).toBe(50);
    expect(r.verdict).toBe("MEDIUM");
  });
});