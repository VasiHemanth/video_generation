import type {CSSProperties} from "react";

export const resolveLength = (
	value: number | string | undefined,
	container: number,
): number | string | undefined => {
	if (value === undefined) {
		return undefined;
	}

	if (typeof value === "number") {
		return value;
	}

	if (value.endsWith("%")) {
		return `${value}`;
	}

	const parsed = Number(value);
	if (Number.isFinite(parsed)) {
		return parsed;
	}

	return value;
};

export const resolvePixelValue = (
	value: number | string,
	container: number,
): number => {
	if (typeof value === "number") {
		return value;
	}

	if (value.endsWith("%")) {
		return (Number(value.slice(0, -1)) / 100) * container;
	}

	return Number(value);
};

export const anchorTransform = (anchor: string | null | undefined): string => {
	switch (anchor) {
		case "top-left":
			return "translate(0, 0)";
		case "top-right":
			return "translate(-100%, 0)";
		case "bottom-left":
			return "translate(0, -100%)";
		case "bottom-right":
			return "translate(-100%, -100%)";
		case "top-center":
			return "translate(-50%, 0)";
		case "bottom-center":
			return "translate(-50%, -100%)";
		case "center-left":
			return "translate(0, -50%)";
		case "center-right":
			return "translate(-100%, -50%)";
		case "center":
		default:
			// Default to center if unspecified, as LLM typically uses 50% / 50% expects centering
			return "translate(-50%, -50%)";
	}
};

export const positionStyle = (
	position: {x: number | string; y: number | string},
	size: {width: number | string; height: number | string} | null | undefined,
	anchor: string | null | undefined,
	canvas: {width: number; height: number},
): CSSProperties => {
	return {
		left: resolveLength(position.x, canvas.width),
		top: resolveLength(position.y, canvas.height),
		width: size ? resolveLength(size.width, canvas.width) : undefined,
		height: size ? resolveLength(size.height, canvas.height) : undefined,
		transform: anchorTransform(anchor),
	};
};
