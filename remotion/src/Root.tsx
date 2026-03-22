import {Composition, Folder, type CalculateMetadataFunction} from "remotion";

import {sampleProjectIr} from "./fixtures/sample-ir";
import {loadCompositionProps} from "./lib/load-ir";
import {VideoComposition, type VideoCompositionProps} from "./Video";

const calculateMetadata: CalculateMetadataFunction<VideoCompositionProps> = async ({
	props,
}) => {
	console.log("calculateMetadata received props keys:", Object.keys(props));
	const resolved = await loadCompositionProps(props);
	const {ir} = resolved;
	console.log("calculateMetadata resolved IR ID:", ir.meta.id);

	return {
		props: resolved,
		durationInFrames: Math.ceil(ir.meta.duration * ir.meta.fps),
		fps: ir.meta.fps,
		width: ir.meta.width,
		height: ir.meta.height,
		defaultOutName: `${ir.meta.id}.mp4`,
	};
};

export const RemotionRoot = () => {
	return (
		<Folder name="IR">
			<Composition
				id="VideoFromIR"
				component={VideoComposition}
				durationInFrames={Math.ceil(sampleProjectIr.meta.duration * sampleProjectIr.meta.fps)}
				fps={sampleProjectIr.meta.fps}
				width={sampleProjectIr.meta.width}
				height={sampleProjectIr.meta.height}
				calculateMetadata={calculateMetadata}
			/>
		</Folder>
	);
};
