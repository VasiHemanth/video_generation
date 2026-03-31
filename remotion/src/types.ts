import {z} from "zod";

export const springConfigSchema = z.object({
	mass: z.number().default(1),
	damping: z.number().default(12),
	stiffness: z.number().default(200),
});

export const typographyTokenSchema = z.object({
	family: z.string(),
	weight: z.number(),
	size: z.number(),
	lineHeight: z.number(),
});

export const themeSchema = z.object({
	name: z.string().default("default"),
	colors: z.object({
		bg_primary: z.string(),
		bg_secondary: z.string(),
		fg_primary: z.string(),
		fg_secondary: z.string(),
		accent_1: z.string(),
		accent_2: z.string(),
		accent_3: z.string(),
		gradient_start: z.string(),
		gradient_end: z.string(),
		surface: z.string(),
		border: z.string(),
	}),
	typography: z.record(z.string(), typographyTokenSchema),
	motion: z.object({
		duration_fast: z.number(),
		duration_normal: z.number(),
		duration_slow: z.number(),
		duration_very_slow: z.number(),
		easing_default: z.string(),
		easing_enter: z.string(),
		easing_exit: z.string(),
		easing_bounce: z.string(),
		easing_spring: springConfigSchema,
		stagger_delay: z.number(),
	}),
	layout: z.object({
		padding: z.number(),
		gap: z.number(),
		card_radius: z.number(),
		safe_area_x: z.number(),
		safe_area_y: z.number(),
	}),
});

export const positionSchema = z.object({
	x: z.union([z.number(), z.string()]),
	y: z.union([z.number(), z.string()]),
});

export const sizeSchema = z.object({
	width: z.union([z.number(), z.string()]).nullable().optional(),
	height: z.union([z.number(), z.string()]).nullable().optional(),
});

export const transitionConfigSchema = z.object({
	type: z.string(),
	duration: z.number(),
	easing: z.string().nullable().optional(),
});

export const backgroundSchema = z.object({
	type: z.string(),
	colors: z.array(z.string()).min(1),
	angle: z.number().nullable().optional(),
	animate: z.boolean().nullable().optional(),
	animation_speed: z.number().nullable().optional(),
});

export const animationSchema = z.object({
	type: z.string(),
	duration: z.number(),
	easing: z.string().nullable().optional(),
	delay: z.number().nullable().optional(),
	spring_config: springConfigSchema.nullable().optional(),
	distance: z.number().nullable().optional(),
});

export const keyframeSchema = z.object({
	time: z.number(),
	property: z.string(),
	value: z.number(),
	easing: z.string().nullable().optional(),
});

export const elementTypeSchema = z.enum([
	"text",
	"shape",
	"group",
	"progress",
	"counter",
	"code-block",
	"icon",
	"particle-field",
	"divider",
	"image",
	"device",
	"svg-path",
	"svg-icon",
]);

export const flexLayoutSchema = z.object({
	display: z.enum(["flex", "grid"]).default("flex"),
	flexDirection: z.enum([
		"row", "column", "row-reverse", "column-reverse"
	]).default("column"),
	alignItems: z.enum([
		"flex-start", "center", "flex-end", "stretch"
	]).default("flex-start"),
	justifyContent: z.enum([
		"flex-start", "center", "flex-end", "space-between", "space-around"
	]).default("flex-start"),
	gap: z.number().default(0),
	padding: z.union([z.number(), z.string()]).nullable().optional(),
	flexWrap: z.enum(["nowrap", "wrap"]).default("nowrap"),
});

// Default MUST be "absolute" for backward compatibility with all existing IRs
export const positioningSchema = z.enum(["flow", "absolute"]).default("absolute");

export type Element = {
	id: string;
	type: z.infer<typeof elementTypeSchema>;
	props: Record<string, unknown>;
	position?: { x?: number | string; y?: number | string } | null;
	size?: { width?: number | string | null; height?: number | string | null } | null;
	positioning: "flow" | "absolute";
	layout?: z.infer<typeof flexLayoutSchema> | null;
	children?: Element[] | null;
	anchor?: string | null;
	layer: number;
	opacity: number;
	rotation: number;
	scale: number;
	enter?: z.infer<typeof animationSchema> | null;
	exit?: z.infer<typeof animationSchema> | null;
	emphasis?: z.infer<typeof animationSchema> | null;
	keyframes: z.infer<typeof keyframeSchema>[];
	delay?: number | null;
	parallax_factor?: number | null;
	ambient?: Record<string, unknown> | null;
	stagger_index?: number | null;
	stagger_delay?: number | null;
	word_animation?: string | null;
	word_stagger?: number | null;
};

const baseElementSchema = z.object({
	id: z.string(),
	type: elementTypeSchema,
	props: z.record(z.string(), z.unknown()),
	position: positionSchema.nullable().optional(),
	size: sizeSchema.nullable().optional(),
	positioning: positioningSchema,
	layout: flexLayoutSchema.nullable().optional(),
	anchor: z.string().nullable().optional(),
	layer: z.number(),
	opacity: z.number().default(1),
	rotation: z.number().default(0),
	scale: z.number().default(1),
	enter: animationSchema.nullable().optional(),
	exit: animationSchema.nullable().optional(),
	emphasis: animationSchema.nullable().optional(),
	keyframes: z.array(keyframeSchema).default([]),
	delay: z.number().nullable().optional(),
	parallax_factor: z.number().nullable().optional(),
	ambient: z.record(z.string(), z.unknown()).nullable().optional(),
	stagger_index: z.number().nullable().optional(),
	stagger_delay: z.number().nullable().optional(),
	word_animation: z.string().nullable().optional(),
	word_stagger: z.number().nullable().optional(),
});

export const elementSchema: z.ZodType<Element> = baseElementSchema.extend({
	children: z.lazy(() => z.array(elementSchema)).nullable().optional(),
});

export const sceneSchema = z.object({
	id: z.string(),
	role: z.string(),
	title: z.string().nullable().optional(),
	start_time: z.number(),
	duration: z.number(),
	transition_in: transitionConfigSchema.nullable().optional(),
	transition_out: transitionConfigSchema.nullable().optional(),
	background: backgroundSchema,
	elements: z.array(elementSchema),
});

export const projectIrSchema = z.object({
	version: z.string(),
	meta: z.object({
		id: z.string(),
		title: z.string(),
		description: z.string().default(""),
		duration: z.number(),
		fps: z.number(),
		width: z.number(),
		height: z.number(),
		aspect_ratio: z.enum(["16:9", "9:16", "1:1"]),
		created_at: z.string(),
		status: z.enum(["draft", "generating", "rendered", "failed"]),
	}),
	theme: themeSchema,
	timeline: z.object({
		scenes: z.array(sceneSchema).min(1),
	}),
	audio: z.object({
		music: z
			.object({
				track_id: z.string(),
				volume: z.number(),
				fade_in: z.number(),
				fade_out: z.number(),
				start_offset: z.number().default(0),
			})
			.nullable()
			.optional(),
		voiceover: z.object({
			enabled: z.boolean().default(false),
			segments: z.array(z.object({
				id: z.string(),
				path: z.string(),
				duration_seconds: z.number().optional(),
			})).default([]),
		}),
		sfx: z
			.array(
				z.object({
					id: z.string(),
					asset_id: z.string(),
					start_time: z.number(),
					volume: z.number(),
					role: z.string(),
				}),
			)
			.default([]),
	}),
	assets: z.object({
		fonts: z.array(
			z.object({
				id: z.string(),
				family: z.string(),
				source: z.string(),
			}),
		),
		audio: z.array(z.record(z.string(), z.unknown())).default([]),
		svg: z.array(z.record(z.string(), z.unknown())).default([]),
		images: z.array(z.record(z.string(), z.unknown())).default([]),
	}),
	constraints: z.object({
		min_duration: z.number().default(30),
		max_duration: z.number().default(40),
		min_scenes: z.number().default(3),
		max_scenes: z.number().default(8),
		min_scene_duration: z.number().default(2),
		max_scene_duration: z.number().default(15),
		platform: z.string().default("youtube"),
		brand: z.string().nullable().optional(),
		content_safety: z.string().default("standard"),
	}),
});

export type ProjectIR = z.infer<typeof projectIrSchema>;
export type Scene = z.infer<typeof sceneSchema>;
// export type Element = z.infer<typeof elementSchema>; // Already declared above explicitly
export type Theme = z.infer<typeof themeSchema>;
export type Animation = z.infer<typeof animationSchema>;
export type TransitionConfig = z.infer<typeof transitionConfigSchema>;
export type FlexLayout = z.infer<typeof flexLayoutSchema>;
