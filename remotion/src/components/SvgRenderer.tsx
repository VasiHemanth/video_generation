import type {CSSProperties} from "react";

import {interpolate, useCurrentFrame, useVideoConfig} from "remotion";

import type {Element, Theme} from "../types";

// ── Built-in SVG icon library ──────────────────────────────────────────────
// Simple stroke-based icons for educational content (24x24 viewBox)

const ICON_LIBRARY: Record<string, string> = {
	checkmark:
		"M 5 12 L 10 17 L 20 7",
	arrow_right:
		"M 5 12 L 19 12 M 14 7 L 19 12 L 14 17",
	arrow_down:
		"M 12 5 L 12 19 M 7 14 L 12 19 L 17 14",
	document:
		"M 6 2 L 6 22 L 18 22 L 18 8 L 12 2 Z M 12 2 L 12 8 L 18 8",
	calendar:
		"M 4 6 L 4 20 L 20 20 L 20 6 Z M 4 10 L 20 10 M 8 2 L 8 6 M 16 2 L 16 6",
	folder:
		"M 2 6 L 2 18 L 22 18 L 22 8 L 12 8 L 10 6 Z",
	link:
		"M 10 14 L 14 10 M 8 16 A 4 4 0 0 1 6 10 L 10 6 A 4 4 0 0 1 16 6 M 14 8 A 4 4 0 0 1 18 14 L 14 18 A 4 4 0 0 1 8 18",
	code:
		"M 8 5 L 3 12 L 8 19 M 16 5 L 21 12 L 16 19",
	star:
		"M 12 2 L 15 9 L 22 9 L 16 14 L 18 21 L 12 17 L 6 21 L 8 14 L 2 9 L 9 9 Z",
	gear:
		"M 12 8 A 4 4 0 1 0 12 16 A 4 4 0 1 0 12 8 M 12 2 L 12 5 M 12 19 L 12 22 M 2 12 L 5 12 M 19 12 L 22 12 M 4.93 4.93 L 7.05 7.05 M 16.95 16.95 L 19.07 19.07 M 4.93 19.07 L 7.05 16.95 M 16.95 7.05 L 19.07 4.93",
	lightning:
		"M 13 2 L 6 13 L 11 13 L 10 22 L 18 10 L 13 10 Z",
	chart_bar:
		"M 4 20 L 4 12 M 9 20 L 9 8 M 14 20 L 14 14 M 19 20 L 19 4",
};

// ── Resolve color from theme token or raw hex ──────────────────────────────

const resolveColor = (value: unknown, theme: Theme): string => {
	if (typeof value !== "string") {
		return theme.colors.fg_primary;
	}

	return (theme.colors[value as keyof typeof theme.colors] as string | undefined) ?? value;
};

// ── SVG Path Draw-On ───────────────────────────────────────────────────────
// Animates a path from invisible to fully drawn using stroke-dashoffset.
// Uses manual calculation instead of @remotion/paths for zero-dep simplicity.

export const renderSvgPath = ({
	element,
	theme,
	frame,
	fps,
}: {
	element: Element;
	theme: Theme;
	frame: number;
	fps: number;
}) => {
	const pathData = element.props.path_data as string;
	const drawDuration = (element.props.draw_duration as number) ?? 0.8;
	const drawDelay = (element.props.draw_delay as number) ?? 0;
	const delayFrames = Math.round(drawDelay * fps);
	const durationFrames = Math.max(1, Math.round(drawDuration * fps));

	const progress = interpolate(
		frame - delayFrames,
		[0, durationFrames],
		[0, 1],
		{extrapolateLeft: "clamp", extrapolateRight: "clamp"},
	);

	const strokeColor = resolveColor(element.props.stroke_color, theme);
	const strokeWidth = (element.props.stroke_width as number) ?? 3;
	const strokeDash = element.props.stroke_dash as string | undefined;

	// Approximate path length for dashoffset (generous overestimate works fine)
	const estimatedLength = 3000;
	const dashArray = strokeDash ?? `${estimatedLength}`;
	const dashOffset = estimatedLength * (1 - progress);

	return (
		<svg
			width="100%"
			height="100%"
			viewBox="0 0 1080 1920"
			style={{position: "absolute", top: 0, left: 0}}
		>
			<path
				d={pathData}
				stroke={strokeColor}
				strokeWidth={strokeWidth}
				strokeDasharray={dashArray}
				strokeDashoffset={dashOffset}
				fill={typeof element.props.fill === "string" ? resolveColor(element.props.fill, theme) : "none"}
				strokeLinecap="round"
				strokeLinejoin="round"
			/>
		</svg>
	);
};

// ── SVG Icon from built-in library ─────────────────────────────────────────

export const renderSvgIcon = ({
	element,
	theme,
}: {
	element: Element;
	theme: Theme;
}) => {
	const iconName = (element.props.icon_name as string) ?? "document";
	const pathData = ICON_LIBRARY[iconName] ?? ICON_LIBRARY.document;
	const color = resolveColor(element.props.color, theme);
	const size = (element.props.size as number) ?? 32;
	const strokeWidth = (element.props.stroke_width as number) ?? 2;

	return (
		<svg
			width={size}
			height={size}
			viewBox="0 0 24 24"
			style={{display: "block"}}
		>
			<path
				d={pathData}
				stroke={color}
				strokeWidth={strokeWidth}
				fill="none"
				strokeLinecap="round"
				strokeLinejoin="round"
			/>
		</svg>
	);
};
