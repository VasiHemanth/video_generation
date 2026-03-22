import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from "remotion";

import {BackgroundFill} from "./BackgroundFill";
import {ElementRenderer} from "./ElementRenderer";
import type {Scene, Theme} from "../types";

const sceneTransitionStyle = ({
	scene,
	frame,
	durationInFrames,
	fps,
}: {
	scene: Scene;
	frame: number;
	durationInFrames: number;
	fps: number;
}) => {
	let opacity = 1;
	let translateX = 0;

	if (scene.transition_in) {
		const enterFrames = Math.max(1, Math.round(scene.transition_in.duration * fps));
		if (scene.transition_in.type === "fade") {
			opacity *= interpolate(frame, [0, enterFrames], [0, 1], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			});
		}
		if (scene.transition_in.type === "slide-left") {
			translateX += interpolate(frame, [0, enterFrames], [90, 0], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			});
			opacity *= interpolate(frame, [0, enterFrames], [0.3, 1], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			});
		}
	}

	if (scene.transition_out) {
		const exitFrames = Math.max(1, Math.round(scene.transition_out.duration * fps));
		const exitStart = Math.max(0, durationInFrames - exitFrames);
		if (scene.transition_out.type === "fade") {
			opacity *= interpolate(frame, [exitStart, durationInFrames], [1, 0], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			});
		}
		if (scene.transition_out.type === "slide-left") {
			translateX += interpolate(frame, [exitStart, durationInFrames], [0, -110], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			});
			opacity *= interpolate(frame, [exitStart, durationInFrames], [1, 0.4], {
				extrapolateLeft: "clamp",
				extrapolateRight: "clamp",
			});
		}
	}

	return {
		opacity,
		transform: `translateX(${translateX}px)`,
	};
};

export const SceneRenderer = ({
	scene,
	theme,
}: {
	scene: Scene;
	theme: Theme;
}) => {
	const frame = useCurrentFrame();
	const {durationInFrames, fps} = useVideoConfig();
	const sceneStyle = sceneTransitionStyle({
		scene,
		frame,
		durationInFrames,
		fps,
	});

	return (
		<AbsoluteFill style={sceneStyle}>
			<BackgroundFill scene={scene} theme={theme} />
			{[...scene.elements]
				.sort((a, b) => a.layer - b.layer)
				.map((element) => {
					console.log(` - Scene ${scene.id} Element ${element.id} [${element.type}]`);
					return (
						<ElementRenderer key={element.id} element={element} theme={theme} />
					);
				})}
		</AbsoluteFill>
	);
};
