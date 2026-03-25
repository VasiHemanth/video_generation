import {AbsoluteFill, Audio, Sequence, staticFile} from "remotion";

import {SceneRenderer} from "./components/SceneRenderer";
import type {ProjectIR} from "./types";

export type VideoCompositionProps = {
	ir?: ProjectIR;
	irPath?: string;
};

const findAudioAsset = (ir: ProjectIR, assetId: string) => {
	return ir.assets.audio.find((a) => a.id === assetId);
};

const getAudioPath = (ir: ProjectIR, assetId: string) => {
	const asset = findAudioAsset(ir, assetId);
	if (!asset || typeof asset.path !== "string") {
		return null;
	}
	return staticFile(asset.path);
};

export const VideoComposition = ({ir}: VideoCompositionProps) => {
	if (!ir) {
		throw new Error("VideoComposition requires a resolved `ir` prop.");
	}

	const fps = ir.meta.fps;
	const {music, sfx, voiceover} = ir.audio;

	return (
		<AbsoluteFill
			style={{
				background: ir.theme.colors.bg_primary,
				color: ir.theme.colors.fg_primary,
			}}
		>
			{/* 1. Background Music */}
			{music && getAudioPath(ir, music.track_id) && (
				<Audio
					src={getAudioPath(ir, music.track_id)!}
					volume={music.volume}
					startFrom={Math.round(music.start_offset * fps)}
				/>
			)}

			{/* 2. Sound Effects */}
			{sfx.map((event) => {
				const src = getAudioPath(ir, event.asset_id);
				if (!src) return null;

				return (
					<Sequence key={event.id} from={Math.round(event.start_time * fps)}>
						<Audio
							src={src}
							volume={event.volume}
							startFrom={0}
						/>
					</Sequence>
				);
			})}

			{/* 3. Voiceover Segments — Mapped to scenes by ID */}
			{voiceover?.enabled &&
				voiceover.segments.map((segment) => {
					// Safely map voice segments to visual scenes by their real IDs
					const scene = ir.timeline.scenes.find((s) => s.id === segment.id);
					const startTime = scene ? scene.start_time : 0;

					return (
						<Sequence key={segment.id} from={Math.round(startTime * fps)}>
							<Audio
								src={staticFile(segment.path)}
								volume={1.0}
								startFrom={0}
							/>
						</Sequence>
					);
				})}

			{/* 4. Visual Timeline */}
			{ir.timeline.scenes.map((scene) => (
				<Sequence
					key={scene.id}
					from={Math.round(scene.start_time * fps)}
					durationInFrames={Math.max(1, Math.round(scene.duration * fps))}
					premountFor={fps}
				>
					<SceneRenderer scene={scene} theme={ir.theme} />
				</Sequence>
			))}
		</AbsoluteFill>
	);
};
