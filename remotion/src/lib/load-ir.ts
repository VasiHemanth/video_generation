import {projectIrSchema, type ProjectIR} from "../types";

export type VideoCompositionProps = {
	ir?: ProjectIR;
	irPath?: string;
};

export const loadCompositionProps = async (
	props: VideoCompositionProps,
): Promise<{ir: ProjectIR}> => {
	if (props.ir) {
		try {
			return {
				ir: projectIrSchema.parse(props.ir),
			};
		} catch (error) {
			console.error("Zod Validation Error for ProjectIR:", error);
			throw error;
		}
	}

	if (props.irPath) {
		throw new Error(
			"`irPath` is not supported yet in the Remotion package. Pass inline `ir` props until backend-render integration copies IR into the Remotion render context.",
		);
	}

	throw new Error("VideoFromIR requires either `ir` or `irPath` props.");
};
