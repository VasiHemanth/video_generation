import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from "remotion";

import type {Scene, Theme} from "../types";

const gradientForScene = (scene: Scene, theme: Theme): string => {
	const colors = scene.background.colors.map((color) => theme.colors[color as keyof typeof theme.colors] ?? color);
	const angle = scene.background.angle ?? 135;

	switch (scene.background.type) {
		case "radial-gradient":
			return `radial-gradient(circle at 50% 50%, ${colors.join(", ")})`;
		case "mesh":
			return `radial-gradient(circle at 20% 20%, ${colors[0]} 0%, transparent 45%), radial-gradient(circle at 80% 30%, ${colors[1] ?? colors[0]} 0%, transparent 40%), linear-gradient(${angle}deg, ${colors.join(", ")})`;
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
	const shift = scene.background.animate
		? interpolate(frame, [0, durationInFrames], [0, 18], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			})
		: 0;

	return (
		<AbsoluteFill
			style={{
				backgroundColor: theme.colors.bg_primary,
				backgroundImage,
				backgroundSize: scene.background.animate ? "140% 140%" : "cover",
				backgroundPosition: `${50 + shift}% ${50 - shift / 2}%`,
			}}
		/>
	);
};
