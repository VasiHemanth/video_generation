import { test, expect } from "vitest";
import { elementSchema } from "../types";

// Test 1: Recursive schema parses without cyclic error
test("recursive element schema round-trips correctly", () => {
  const mockGroup = {
    id: "card-root",
    type: "group",
    props: {},
    positioning: "flow",
    layout: {
      display: "flex",
      flexDirection: "column",
      alignItems: "flex-start",
      justifyContent: "flex-start",
      gap: 16,
      flexWrap: "nowrap",
    },
    layer: 1,
    opacity: 1,
    rotation: 0,
    scale: 1,
    keyframes: [],
    children: [
      {
        id: "card-title",
        type: "text",
        props: { content: "Hello World" },
        positioning: "flow",
        layer: 0,
        opacity: 1,
        rotation: 0,
        scale: 1,
        keyframes: [],
      },
    ],
  };
  const result = elementSchema.safeParse(mockGroup);
  expect(result.success).toBe(true);
  expect(result.data?.children).toHaveLength(1);
  expect(result.data?.children?.[0].id).toBe("card-title");
});

// Test 2: CRITICAL backward compat — existing IR element without positioning field
test("existing IR element without positioning field defaults to absolute", () => {
  const legacyElement = {
    id: "scene_001_headline",
    type: "text",
    props: { content: "Hello World" },
    position: { x: "50%", y: "32%" },   // has position, NO positioning field
    layer: 3,
    opacity: 1,
    rotation: 0,
    scale: 1,
    keyframes: [],
  };
  const result = elementSchema.safeParse(legacyElement);
  expect(result.success).toBe(true);
  // If this is "flow", every existing IR breaks — must be "absolute"
  expect(result.data?.positioning).toBe("absolute");
});

// Test 3: Flow element is valid without a position field
test("flow element parses correctly without position", () => {
  const flowElement = {
    id: "card-body",
    type: "text",
    props: { content: "Body text" },
    positioning: "flow",     // explicitly flow
    // no position field at all
    layer: 0,
    opacity: 1,
    rotation: 0,
    scale: 1,
    keyframes: [],
  };
  const result = elementSchema.safeParse(flowElement);
  expect(result.success).toBe(true);
  expect(result.data?.position).toBeUndefined();
});

// Test 4: Deeply nested children parse correctly
test("three levels of nesting parse correctly", () => {
  const deepGroup = {
    id: "root",
    type: "group",
    props: {},
    positioning: "absolute",
    position: { x: "10%", y: "20%" },
    layout: { display: "flex", flexDirection: "column", gap: 16, flexWrap: "nowrap",
              alignItems: "flex-start", justifyContent: "flex-start" },
    layer: 1,
    opacity: 1,
    rotation: 0,
    scale: 1,
    keyframes: [],
    children: [
      {
        id: "inner-group",
        type: "group",
        props: {},
        positioning: "flow",
        layout: { display: "flex", flexDirection: "row", gap: 8, flexWrap: "nowrap",
                  alignItems: "center", justifyContent: "flex-start" },
        layer: 0,
        opacity: 1,
        rotation: 0,
        scale: 1,
        keyframes: [],
        children: [
          {
            id: "leaf",
            type: "text",
            props: { content: "Deep leaf" },
            positioning: "flow",
            layer: 0,
            opacity: 1,
            rotation: 0,
            scale: 1,
            keyframes: [],
          },
        ],
      },
    ],
  };
  const result = elementSchema.safeParse(deepGroup);
  expect(result.success).toBe(true);
  expect(result.data?.children?.[0].children?.[0].id).toBe("leaf");
});
