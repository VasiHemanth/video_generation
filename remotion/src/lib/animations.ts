import {Easing, interpolate, spring} from "remotion";

import type {Animation} from "../types";

const clampInterpolate = (
	frame: number,
	range: [number, number],
	output: [number, number],
	easing?: ((input: number) => number) | undefined,
) => {
	return interpolate(frame, range, output, {
		easing,
		extrapolateLeft: "clamp",
		extrapolateRight: "clamp",
	});
};

const resolveEasing = (value: string | null | undefined) => {
	switch (value) {
		case "ease-in":
			return Easing.in(Easing.quad);
		case "ease-in-out":
			return Easing.inOut(Easing.quad);
		case "ease-out":
			return Easing.out(Easing.quad);
		case "ease-out-back":
			return Easing.out(Easing.back(1.5));
		case "ease-out-expo":
			return Easing.out(Easing.exp);
		case "ease-in-out-expo":
			return Easing.inOut(Easing.exp);
		case "ease-out-cubic":
			return Easing.out(Easing.cubic);
		default:
			return Easing.out(Easing.quad);
	}
};

type AnimatedStyleResult = {
	opacity: number;
	translateX: number;
	translateY: number;
	scale: number;
	rotate: number;
	clipProgress: number;
};

const defaultResult = (): AnimatedStyleResult => ({
	opacity: 1,
	translateX: 0,
	translateY: 0,
	scale: 1,
	rotate: 0,
	clipProgress: 1,
});

export const getAnimationStyle = ({
	animation,
	frame,
	fps,
	phase,
	totalDurationInFrames,
}: {
	animation: Animation | null | undefined;
	frame: number;
	fps: number;
	phase: "enter" | "exit" | "emphasis";
	totalDurationInFrames: number;
}): AnimatedStyleResult => {
	if (!animation) {
		return defaultResult();
	}

	const durationInFrames = Math.max(1, Math.round(animation.duration * fps));
	const delayInFrames = Math.max(0, Math.round((animation.delay ?? 0) * fps));
	// BUG FIX: Elements are often inside a Sequence.
	// totalDurationInFrames should ideally be the scene duration.
	// But since we don't have it, we must ensure that if frame is within
	// reasonable bounds, exit shouldn't be active.
	const exitStart = Math.max(0, totalDurationInFrames - durationInFrames - delayInFrames);
	const localFrame =
		phase === "exit"
			? (frame >= exitStart ? frame - exitStart : 0)
			: Math.max(0, frame - delayInFrames);

	// If we are in exit phase but haven't reached the start, return neutral.
	if (phase === "exit" && frame < exitStart) {
		return defaultResult();
	}
	const eased = resolveEasing(animation.easing);
	const distance = animation.distance ?? 60;

	const result = defaultResult();

	if (animation.type === "spring" || animation.type === "bounce") {
		const progress = spring({
			frame: localFrame,
			fps,
			durationInFrames,
			config: animation.spring_config ?? {
				damping: animation.type === "bounce" ? 10 : 16,
				mass: 1,
				stiffness: animation.type === "bounce" ? 160 : 220,
			},
		});

		if (phase === "exit") {
			result.opacity = localFrame > 0 ? 1 - progress : 1;
			result.scale = localFrame > 0 ? 1 - progress * 0.15 : 1;
		} else {
			result.opacity = progress;
			result.scale = phase === "emphasis" ? 1 + progress * 0.08 : 0.85 + progress * 0.15;
		}
		return result;
	}

	switch (animation.type) {
		case "fade":
		case "fade-in":
			result.opacity = clampInterpolate(localFrame, [0, durationInFrames], [0, 1], eased);
			return result;
		case "fade-out":
			result.opacity = clampInterpolate(localFrame, [0, durationInFrames], [1, 0], eased);
			return result;
		case "slide-up":
			result.opacity = clampInterpolate(localFrame, [0, durationInFrames], [0, 1], eased);
			result.translateY = clampInterpolate(localFrame, [0, durationInFrames], [distance, 0], eased);
			return result;
		case "slide-down":
			result.opacity = clampInterpolate(localFrame, [0, durationInFrames], [0, 1], eased);
			result.translateY = clampInterpolate(localFrame, [0, durationInFrames], [-distance, 0], eased);
			return result;
		case "slide-left":
			result.opacity = clampInterpolate(localFrame, [0, durationInFrames], [0, 1], eased);
			result.translateX = clampInterpolate(localFrame, [0, durationInFrames], [distance, 0], eased);
			return result;
		case "slide-right":
			result.opacity = clampInterpolate(localFrame, [0, durationInFrames], [0, 1], eased);
			result.translateX = clampInterpolate(localFrame, [0, durationInFrames], [-distance, 0], eased);
			return result;
		case "scale-in":
			result.opacity = clampInterpolate(localFrame, [0, durationInFrames], [0, 1], eased);
			result.scale = clampInterpolate(localFrame, [0, durationInFrames], [0.84, 1], eased);
			return result;
		case "scale-out":
			result.opacity = clampInterpolate(localFrame, [0, durationInFrames], [1, 0], eased);
			result.scale = clampInterpolate(localFrame, [0, durationInFrames], [1, 1.12], eased);
			return result;
		case "wipe":
			result.opacity = 1;
			result.clipProgress = clampInterpolate(localFrame, [0, durationInFrames], [0, 1], eased);
			return result;
		default:
			return result;
	}
};

export const mergeAnimationStyles = ({
	baseOpacity,
	baseScale,
	baseRotation,
	enter,
	exit,
	emphasis,
}: {
	baseOpacity: number;
	baseScale: number;
	baseRotation: number;
	enter: AnimatedStyleResult;
	exit: AnimatedStyleResult;
	emphasis: AnimatedStyleResult;
}) => {
	return {
		opacity: Math.max(0, Math.min(1, baseOpacity * enter.opacity * exit.opacity)),
		scale: baseScale * enter.scale * exit.scale * emphasis.scale,
		translateX: enter.translateX + exit.translateX + emphasis.translateX,
		translateY: enter.translateY + exit.translateY + emphasis.translateY,
		rotate: baseRotation + enter.rotate + exit.rotate + emphasis.rotate,
		clipProgress: Math.min(enter.clipProgress, exit.clipProgress, emphasis.clipProgress),
	};
};

export const keyframedValue = ({
	initial,
	keyframes,
	frame,
	fps,
}: {
	initial: number;
	keyframes: Array<{time: number; value: number}>;
	frame: number;
	fps: number;
}) => {
	if (keyframes.length === 0) {
		return initial;
	}

	const times = [0, ...keyframes.map((keyframe) => Math.round(keyframe.time * fps))];
	const values = [initial, ...keyframes.map((keyframe) => keyframe.value)];

	return interpolate(frame, times, values, {
		extrapolateLeft: "clamp",
		extrapolateRight: "clamp",
	});
};
