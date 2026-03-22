import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from "remotion";

import type {Scene, Theme} from "../types";

const gradientForScene = (scene: Scene, theme: Theme): string => {
	const colors = scene.background.colors.map((color) => theme.colors[color as keyof typeof theme.colors] ?? color);
	const angle = scene.background.angle ?? 135;

	switch (scene.background.type) {
		case "radial-gradient":
			return `radial-gradient(circle at 50% 50%, ${colors.join(", ")})`;
		case "mesh":
			return `radial-gradient(circle at 20% 20%, ${colors[0]} 0%, transparent 45%), radial-gradient(circle at 80% 30%, ${colors[1] ?? colors[0]} 0%, transparent 40%), radial-gradient(circle at 50% 80%, ${colors[2] ?? colors[0]} 0%, transparent 50%), linear-gradient(${angle}deg, ${colors.join(", ")})`;
		case "animated-gradient":
		case "gradient":
		default:
			return `linear-gradient(${angle}deg, ${colors.join(", ")})`;
	}
};

export const BackgroundFill = ({
	scene,
	theme,
}: {
	scene: Scene;
	theme: Theme;
}) => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const backgroundImage = gradientForScene(scene, theme);

	// Stronger animated gradient shift
	const shift = scene.background.animate
		? interpolate(frame, [0, durationInFrames], [0, 40], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			})
		: 0;

	// Subtle animated rotation for mesh backgrounds
	const meshRotate = scene.background.type === "mesh"
		? interpolate(frame, [0, durationInFrames], [0, 8], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			})
		: 0;

	return (
		<>
			<AbsoluteFill
				style={{
					backgroundColor: theme.colors.bg_primary,
					backgroundImage,
					backgroundSize: scene.background.animate ? "160% 160%" : "cover",
					backgroundPosition: `${50 + shift}% ${50 - shift / 2}%`,
					transform: meshRotate ? `rotate(${meshRotate}deg) scale(1.05)` : undefined,
				}}
			/>
			{/* Subtle noise grain overlay for depth */}
			<AbsoluteFill
				style={{
					background: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
					opacity: 0.03,
					mixBlendMode: "overlay",
				}}
			/>
		</>
	);
};

