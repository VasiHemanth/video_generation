import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from "remotion";

import {BackgroundFill} from "./BackgroundFill";
import {ElementRenderer} from "./ElementRenderer";
import type {Scene, Theme} from "../types";

const cl = (
	frame: number,
	range: [number, number],
	output: [number, number],
) =>
	interpolate(frame, range, output, {
		extrapolateLeft: "clamp",
		extrapolateRight: "clamp",
	});

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
	let translateY = 0;
	let scale = 1;
	let rotate = 0;
	let filter = "";

	// ── Enter transitions ──────────────────────────────────────────────────
	if (scene.transition_in) {
		const ef = Math.max(1, Math.round(scene.transition_in.duration * fps));
		const t = scene.transition_in.type;

		if (t === "fade") {
			opacity *= cl(frame, [0, ef], [0, 1]);
		} else if (t === "slide-left") {
			translateX += cl(frame, [0, ef], [90, 0]);
			opacity *= cl(frame, [0, ef], [0.3, 1]);
		} else if (t === "slide-up") {
			translateY += cl(frame, [0, ef], [60, 0]);
			opacity *= cl(frame, [0, ef], [0, 1]);
		} else if (t === "zoom") {
			scale *= cl(frame, [0, ef], [1.15, 1]);
			opacity *= cl(frame, [0, ef], [0, 1]);
		} else if (t === "blur-in") {
			const blur = cl(frame, [0, ef], [12, 0]);
			filter = `blur(${blur}px)`;
			opacity *= cl(frame, [0, ef], [0, 1]);
		} else if (t === "rotate") {
			rotate += cl(frame, [0, ef], [-4, 0]);
			scale *= cl(frame, [0, ef], [0.95, 1]);
			opacity *= cl(frame, [0, ef], [0, 1]);
		} else if (t === "cross-dissolve") {
			opacity *= cl(frame, [0, ef], [0, 1]);
			scale *= cl(frame, [0, ef], [1.03, 1]);
		}
	}

	// ── Exit transitions ───────────────────────────────────────────────────
	if (scene.transition_out) {
		const ef = Math.max(1, Math.round(scene.transition_out.duration * fps));
		const es = Math.max(0, durationInFrames - ef);
		const t = scene.transition_out.type;

		if (t === "fade") {
			opacity *= cl(frame, [es, durationInFrames], [1, 0]);
		} else if (t === "slide-left") {
			translateX += cl(frame, [es, durationInFrames], [0, -110]);
			opacity *= cl(frame, [es, durationInFrames], [1, 0.4]);
		} else if (t === "slide-up") {
			translateY += cl(frame, [es, durationInFrames], [0, -50]);
			opacity *= cl(frame, [es, durationInFrames], [1, 0]);
		} else if (t === "zoom") {
			scale *= cl(frame, [es, durationInFrames], [1, 0.88]);
			opacity *= cl(frame, [es, durationInFrames], [1, 0]);
		} else if (t === "blur-in") {
			const blur = cl(frame, [es, durationInFrames], [0, 14]);
			filter = `blur(${blur}px)`;
			opacity *= cl(frame, [es, durationInFrames], [1, 0]);
		} else if (t === "rotate") {
			rotate += cl(frame, [es, durationInFrames], [0, 3]);
			scale *= cl(frame, [es, durationInFrames], [1, 0.96]);
			opacity *= cl(frame, [es, durationInFrames], [1, 0]);
		} else if (t === "cross-dissolve") {
			opacity *= cl(frame, [es, durationInFrames], [1, 0]);
			scale *= cl(frame, [es, durationInFrames], [1, 1.04]);
		}
	}

	return {
		opacity,
		transform: `translateX(${translateX}px) translateY(${translateY}px) scale(${scale}) rotate(${rotate}deg)`,
		...(filter ? {filter} : {}),
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
