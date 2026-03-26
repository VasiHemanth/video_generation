import type {CSSProperties} from "react";

import {
	AbsoluteFill,
	interpolate,
	useCurrentFrame,
	useVideoConfig,
} from "remotion";

import {getAnimationStyle, keyframedValue, mergeAnimationStyles} from "../lib/animations";
import {positionStyle, resolvePixelValue} from "../lib/geometry";
import {renderSvgIcon, renderSvgPath} from "./SvgRenderer";
import type {Element, Theme} from "../types";

const resolveColor = (value: unknown, theme: Theme): string => {
	if (typeof value !== "string") {
		return theme.colors.fg_primary;
	}

	return (theme.colors[value as keyof typeof theme.colors] as string | undefined) ?? value;
};

const renderShape = (element: Element, theme: Theme) => {
	const fill = resolveColor(element.props.fill, theme);
	const stroke = element.props.stroke ? resolveColor(element.props.stroke, theme) : "transparent";
	const strokeWidth =
		typeof element.props.stroke_width === "number" ? element.props.stroke_width : 0;

	const borderRadius =
		element.props.shape === "circle"
			? "999px"
			: typeof element.props.corner_radius === "number"
				? `${element.props.corner_radius}px`
				: "20px";

	const triangleClip =
		element.props.shape === "triangle" ? "polygon(50% 0%, 0% 100%, 100% 100%)" : undefined;

	return (
		<div
			style={{
				width: "100%",
				height: "100%",
				background: fill,
				borderRadius,
				border: `${strokeWidth}px solid ${stroke}`,
				clipPath: triangleClip,
				boxShadow: `0 0 60px ${fill}33`,
			}}
		/>
	);
};

const renderText = ({
	element,
	theme,
	frame,
	fps,
}: {
	element: Element;
	theme: Theme;
	frame: number;
	fps: number;
}) => {
	const tokenName =
		typeof element.props.style_token === "string" ? element.props.style_token : "body_md";
	const token = theme.typography[tokenName] ?? theme.typography.body_md;
	const text = typeof element.props.content === "string" ? element.props.content : "";
	const align = typeof element.props.align === "string" ? element.props.align : "left";
	const wordAnimation = (element.word_animation || element.props.word_animation) as string | undefined;
	const wordStagger = typeof element.word_stagger === "number"
		? element.word_stagger
		: (typeof element.props.word_stagger === "number" ? element.props.word_stagger : 0.05);
	const maxWidth =
		typeof element.props.max_width === "number" ? element.props.max_width : undefined;

	if (wordAnimation !== "word-by-word") {
		return (
			<div
				style={{
					color: resolveColor(element.props.color, theme),
					fontFamily: `${token.family}, system-ui, sans-serif`,
					fontWeight: token.weight,
					fontSize: token.size,
					lineHeight: token.lineHeight,
					textAlign: align as CSSProperties["textAlign"],
					maxWidth,
				}}
			>
				{text}
			</div>
		);
	}

	const words = text.split(" ");
	const staggerFrames = Math.max(1, Math.round(wordStagger * fps));

	return (
		<div
			style={{
				color: resolveColor(element.props.color, theme),
				fontFamily: `${token.family}, system-ui, sans-serif`,
				fontWeight: token.weight,
				fontSize: token.size,
				lineHeight: token.lineHeight,
				textAlign: align as CSSProperties["textAlign"],
				maxWidth,
			}}
		>
			{words.map((word, index) => {
				const localFrame = Math.max(0, frame - index * staggerFrames);
				const opacity = interpolate(localFrame, [0, 10], [0, 1], {
					extrapolateLeft: "clamp",
					extrapolateRight: "clamp",
				});
				const translateY = interpolate(localFrame, [0, 10], [18, 0], {
					extrapolateLeft: "clamp",
					extrapolateRight: "clamp",
				});

				return (
					<span
						key={`${element.id}-${word}-${index}`}
						style={{
							display: "inline-block",
							marginRight: "0.3em",
							opacity,
							transform: `translateY(${translateY}px)`,
						}}
					>
						{word}
					</span>
				);
			})}
		</div>
	);
};

const renderProgress = ({
	element,
	theme,
	frame,
	fps,
}: {
	element: Element;
	theme: Theme;
	frame: number;
	fps: number;
}) => {
	const value = typeof element.props.value === "number" ? element.props.value : 0;
	const max = typeof element.props.max === "number" ? element.props.max : 100;
	const progress = interpolate(frame, [0, fps], [0, value / max], {
		extrapolateLeft: "clamp",
		extrapolateRight: "clamp",
	});
	const color = resolveColor(element.props.color, theme);
	const trackColor = resolveColor(element.props.track_color, theme);
	const thickness =
		typeof element.props.thickness === "number" ? element.props.thickness : 12;

	return (
		<div style={{width: "100%"}}>
			<div
				style={{
					height: thickness,
					width: "100%",
					background: trackColor,
					borderRadius: 999,
					overflow: "hidden",
				}}
			>
				<div
					style={{
						height: "100%",
						width: `${progress * 100}%`,
						background: `linear-gradient(90deg, ${color}, ${theme.colors.accent_3})`,
						borderRadius: 999,
					}}
				/>
			</div>
			{typeof element.props.label === "string" ? (
				<div
					style={{
						marginTop: 14,
						color: theme.colors.fg_secondary,
						fontFamily: `${theme.typography.body_md.family}, system-ui, sans-serif`,
						fontSize: theme.typography.body_md.size,
						textAlign: "right",
					}}
				>
					{element.props.label}
				</div>
			) : null}
		</div>
	);
};

const renderCounter = ({
	element,
	theme,
	frame,
	fps,
}: {
	element: Element;
	theme: Theme;
	frame: number;
	fps: number;
}) => {
	const start = typeof element.props.from === "number" ? element.props.from : 0;
	const end = typeof element.props.to === "number" ? element.props.to : 100;
	const tokenName =
		typeof element.props.style_token === "string" ? element.props.style_token : "display_sm";
	const token = theme.typography[tokenName] ?? theme.typography.display_sm;
	const value = Math.round(
		interpolate(frame, [0, fps], [start, end], {
			extrapolateLeft: "clamp",
			extrapolateRight: "clamp",
		}),
	);

	return (
		<div
			style={{
				color: resolveColor(element.props.color, theme),
				fontFamily: `${token.family}, system-ui, sans-serif`,
				fontWeight: token.weight,
				fontSize: token.size,
				lineHeight: token.lineHeight,
				textAlign: "center",
			}}
		>
			{`${typeof element.props.prefix === "string" ? element.props.prefix : ""}${value.toLocaleString()}${typeof element.props.suffix === "string" ? element.props.suffix : ""}`}
		</div>
	);
};

const seeded = (seed: string, offset: number) => {
	let hash = 0;
	const source = `${seed}:${offset}`;
	for (let index = 0; index < source.length; index += 1) {
		hash = (hash * 31 + source.charCodeAt(index)) % 1000000;
	}
	return (Math.sin(hash) + 1) / 2;
};

const renderParticles = ({
	element,
	theme,
	frame,
	width,
	height,
}: {
	element: Element;
	theme: Theme;
	frame: number;
	width: number;
	height: number;
}) => {
	const count = typeof element.props.count === "number" ? element.props.count : 30;
	const color = resolveColor(element.props.color, theme);
	const speed = typeof element.props.speed === "number" ? element.props.speed : 0.4;
	const sizeRange = Array.isArray(element.props.size_range)
		? element.props.size_range
		: [2, 6];
	const opacity =
		typeof element.props.opacity === "number" ? element.props.opacity : 0.25;

	return (
		<AbsoluteFill>
			{Array.from({length: count}).map((_, index) => {
				const x = seeded(element.id, index) * width;
				const y = seeded(element.id, index + 100) * height;
				const size =
					sizeRange[0] + seeded(element.id, index + 200) * (sizeRange[1] - sizeRange[0]);
				const drift = ((frame * speed) % 120) - 60;

				return (
					<div
						key={`${element.id}-particle-${index}`}
						style={{
							position: "absolute",
							left: x,
							top: y + drift,
							width: size,
							height: size,
							borderRadius: 999,
							background: color,
							opacity,
							filter: "blur(0.5px)",
						}}
					/>
				);
			})}
		</AbsoluteFill>
	);
};

const renderDevice = ({
	element,
	theme,
}: {
	element: Element;
	theme: Theme;
}) => {
	const variant = typeof element.props.variant === "string" ? element.props.variant : "browser";
	const color = resolveColor(element.props.color, theme);
	const surface = theme.colors.surface;

	if (variant === "phone") {
		return (
			<div
				style={{
					width: "100%",
					height: "100%",
					border: `8px solid ${color}`,
					borderRadius: 48,
					background: surface,
					position: "relative",
					overflow: "hidden",
				}}
			>
				<div
					style={{
						position: "absolute",
						top: 10,
						left: "50%",
						transform: "translateX(-50%)",
						width: 60,
						height: 18,
						background: color,
						borderRadius: 20,
					}}
				/>
			</div>
		);
	}

	return (
		<div
			style={{
				width: "100%",
				height: "100%",
				border: `2px solid ${color}`,
				borderRadius: 12,
				background: surface,
				position: "relative",
				overflow: "hidden",
			}}
		>
			<div
				style={{
					height: 32,
					width: "100%",
					background: `${color}22`,
					borderBottom: `1px solid ${color}44`,
					display: "flex",
					alignItems: "center",
					padding: "0 12px",
					gap: 6,
				}}
			>
				<div style={{width: 8, height: 8, borderRadius: 4, background: color}} />
				<div style={{width: 8, height: 8, borderRadius: 4, background: color}} />
				<div style={{width: 8, height: 8, borderRadius: 4, background: color}} />
			</div>
		</div>
	);
};

const renderUnsupported = (element: Element, theme: Theme) => {
	return (
		<div
			style={{
				padding: "14px 18px",
				borderRadius: 14,
				border: `1px dashed ${theme.colors.border}`,
				color: theme.colors.fg_secondary,
				fontFamily: `${theme.typography.body_md.family}, system-ui, sans-serif`,
				fontSize: theme.typography.body_md.size,
			}}
		>
			{`Unsupported element type: ${element.type}`}
		</div>
	);
};

export const ElementRenderer = ({
	element,
	theme,
}: {
	element: Element;
	theme: Theme;
}) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames, width, height} = useVideoConfig();

	// ── Stagger group: auto-offset entry delay based on stagger_index ──
	const staggerIndex = typeof element.stagger_index === "number" 
		? element.stagger_index 
		: (typeof element.props.stagger_index === "number" ? element.props.stagger_index : null);
	
	const staggerDelay = typeof element.stagger_delay === "number"
		? element.stagger_delay
		: (typeof element.props.stagger_delay === "number" ? element.props.stagger_delay : 0.1);

	const effectiveEnter = staggerIndex != null && element.enter
		? { ...element.enter, delay: (element.enter.delay ?? 0) + staggerIndex * staggerDelay }
		: element.enter;

	const enter = getAnimationStyle({
		animation: effectiveEnter,
		frame,
		fps,
		phase: "enter",
		totalDurationInFrames: durationInFrames,
	});
	const exit = getAnimationStyle({
		animation: element.exit,
		frame,
		fps,
		phase: "exit",
		totalDurationInFrames: durationInFrames,
	});
	const emphasis = getAnimationStyle({
		animation: element.emphasis,
		frame,
		fps,
		phase: "emphasis",
		totalDurationInFrames: durationInFrames,
	});

	const layoutStyle = positionStyle(element.position, element.size, element.anchor, {
		width,
		height,
	});

	const rotation = keyframedValue({
		initial: element.rotation ?? 0,
		keyframes: element.keyframes
			.filter((keyframe) => keyframe.property === "rotation")
			.map((keyframe) => ({time: keyframe.time, value: keyframe.value})),
		frame,
		fps,
	});

	const merged = mergeAnimationStyles({
		baseOpacity: element.opacity ?? 1,
		baseScale: element.scale ?? 1,
		baseRotation: rotation,
		enter,
		exit,
		emphasis,
	});

	const parallaxX = element.parallax_factor ? (frame - durationInFrames / 2) * element.parallax_factor : 0;
	const parallaxY = element.parallax_factor ? (frame - durationInFrames / 2) * (element.parallax_factor * 0.6) : 0;

	// ── Ambient float: continuous organic sine-wave drift ──
	const ambient = (element.ambient || element.props.ambient) as
		| {type: "float"; amplitude?: number; frequency?: number; phase?: number}
		| undefined;
	const hasAmbient = ambient?.type === "float";
	const ambientAmplitude = ambient?.amplitude ?? 4;
	const ambientFrequency = ambient?.frequency ?? 0.3;
	const ambientPhase = ambient?.phase ?? 0;
	const ambientY = hasAmbient
		? Math.sin(frame * ambientFrequency * 0.1 + ambientPhase) * ambientAmplitude
		: 0;
	const ambientX = hasAmbient
		? Math.cos(frame * ambientFrequency * 0.07 + ambientPhase) * ambientAmplitude * 0.5
		: 0;

	// ── 3D depth: perspective + subtle rotation ──
	const has3D = element.props.depth_3d === true;

	const totalTranslateX = merged.translateX + parallaxX + ambientX;
	const totalTranslateY = merged.translateY + parallaxY + ambientY;
	const rotateY3D = has3D ? " rotateY(2deg)" : "";

	const sharedStyle: CSSProperties = {
		position: "absolute",
		...layoutStyle,
		opacity: merged.opacity,
		perspective: has3D ? "1000px" : undefined,
		transform: `${layoutStyle.transform ?? ""} translate(${totalTranslateX}px, ${totalTranslateY}px) rotate(${merged.rotate}deg) scale(${merged.scale})${rotateY3D}`,
		transformOrigin: "center center",
		overflow: element.type === "progress" ? "hidden" : undefined,
		// Glassmorphism effect for elements with background
		backdropFilter: element.props.glassmorphism || element.props.fill === "surface" ? "blur(12px) saturate(150%)" : undefined,
		WebkitBackdropFilter: element.props.glassmorphism || element.props.fill === "surface" ? "blur(12px) saturate(150%)" : undefined,
		clipPath:
			merged.clipProgress < 1
				? `inset(0 ${100 - merged.clipProgress * 100}% 0 0)`
				: undefined,
	};

	if (element.type === "particle-field") {
		return (
			<div style={sharedStyle}>
				{renderParticles({element, theme, frame, width, height})}
			</div>
		);
	}

	if (element.type === "text") {
		return <div style={sharedStyle}>{renderText({element, theme, frame, fps})}</div>;
	}

	if (element.type === "shape") {
		return <div style={sharedStyle}>{renderShape(element, theme)}</div>;
	}

	if (element.type === "progress") {
		return <div style={sharedStyle}>{renderProgress({element, theme, frame, fps})}</div>;
	}

	if (element.type === "counter") {
		return <div style={sharedStyle}>{renderCounter({element, theme, frame, fps})}</div>;
	}

	if (element.type === "device") {
		return <div style={sharedStyle}>{renderDevice({element, theme})}</div>;
	}

	if (element.type === "divider") {
		const orientation =
			typeof element.props.orientation === "string" ? element.props.orientation : "horizontal";
		const thickness =
			typeof element.props.thickness === "number" ? element.props.thickness : 2;
		return (
			<div
				style={{
					...sharedStyle,
					background: resolveColor(element.props.color, theme),
					width:
						orientation === "horizontal"
							? sharedStyle.width ?? resolvePixelValue("100%", width)
							: thickness,
					height:
						orientation === "horizontal"
							? thickness
							: sharedStyle.height ?? resolvePixelValue("100%", height),
				}}
			/>
		);
	}

	if (element.type === "svg-path") {
		return <div style={sharedStyle}>{renderSvgPath({element, theme, frame, fps})}</div>;
	}

	if (element.type === "svg-icon") {
		return <div style={sharedStyle}>{renderSvgIcon({element, theme})}</div>;
	}

	return <div style={sharedStyle}>{renderUnsupported(element, theme)}</div>;
};
