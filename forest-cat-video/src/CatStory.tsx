import {
  AbsoluteFill,
  Img,
  Series,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const IMG_W = 819;
const IMG_H = 1024;
const CARD_W = 960;
const SCENE_FRAMES = 140;

type Scene = {
  src: string;
  // Region of the source photo to show, in source pixels.
  crop: { x: number; y: number; w: number; h: number };
  // Ken Burns focus point inside the card, 0-1.
  focus: { x: number; y: number };
  zoom: number;
  chapter: string;
  caption: string;
};

const SCENES: Scene[] = [
  {
    src: "cat1.jpg",
    crop: { x: 0, y: 0, w: IMG_W, h: IMG_H },
    focus: { x: 0.5, y: 0.5 },
    zoom: 1.12,
    chapter: "Chapter I",
    caption: "Meet Soot, the smallest cat in the bamboo forest.",
  },
  {
    src: "cat2.jpg",
    crop: { x: 0, y: 0, w: IMG_W, h: 512 },
    focus: { x: 0.48, y: 0.62 },
    zoom: 1.7,
    chapter: "Chapter II",
    caption: "Every morning, Soot walked the old path home alone.",
  },
  {
    src: "cat2.jpg",
    crop: { x: 0, y: 512, w: IMG_W, h: 512 },
    focus: { x: 0.66, y: 0.7 },
    zoom: 1.7,
    chapter: "Chapter III",
    caption: "Then, a rustle. Soot froze... and listened.",
  },
  {
    src: "cat3.jpg",
    crop: { x: 0, y: 0, w: IMG_W, h: 512 },
    focus: { x: 0.4, y: 0.5 },
    zoom: 1.5,
    chapter: "Chapter IV",
    caption: "Between the branches, two golden eyes watched the world.",
  },
  {
    src: "cat3.jpg",
    crop: { x: 0, y: 512, w: IMG_W, h: 512 },
    focus: { x: 0.65, y: 0.55 },
    zoom: 1.45,
    chapter: "Chapter V",
    caption: "Small. Fluffy. Fierce. Nothing could scare Soot.",
  },
  {
    src: "cat1.jpg",
    crop: { x: 0, y: 0, w: IMG_W, h: IMG_H },
    focus: { x: 0.5, y: 0.45 },
    zoom: 1.2,
    chapter: "The End",
    caption: "The forest was quiet again. It belonged to Soot.",
  },
];

export const TOTAL_FRAMES = SCENES.length * SCENE_FRAMES;

const Caption: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const words = text.split(" ");
  return (
    <div
      style={{
        fontFamily: "Georgia, 'Times New Roman', serif",
        fontSize: 68,
        lineHeight: 1.25,
        color: "#f4ead5",
        textAlign: "center",
        width: CARD_W,
        textShadow: "0 4px 24px rgba(0,0,0,0.7)",
      }}
    >
      {words.map((w, i) => {
        const start = 25 + i * 5;
        const opacity = interpolate(frame, [start, start + 12], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const y = interpolate(frame, [start, start + 12], [18, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity,
              transform: `translateY(${y}px)`,
              marginRight: 16,
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

const SceneView: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const { crop, focus } = scene;
  const scale = CARD_W / crop.w;
  const cardH = crop.h * scale;

  const fade = interpolate(
    frame,
    [0, 18, durationInFrames - 18, durationInFrames],
    [0, 1, 1, 0],
  );
  const zoom = interpolate(frame, [0, durationInFrames], [1, scene.zoom]);
  const bgZoom = interpolate(frame, [0, durationInFrames], [1.15, 1.3]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0d0a", opacity: fade }}>
      <AbsoluteFill
        style={{
          transform: `scale(${bgZoom})`,
        }}
      >
        <Img
          src={staticFile(scene.src)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: "blur(40px) brightness(0.35) saturate(1.2)",
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          gap: 56,
        }}
      >
        <div
          style={{
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontStyle: "italic",
            fontSize: 44,
            letterSpacing: 8,
            textTransform: "uppercase",
            color: "#d9b36c",
            opacity: interpolate(frame, [8, 28], [0, 1], {
              extrapolateRight: "clamp",
            }),
          }}
        >
          {scene.chapter}
        </div>

        <div
          style={{
            width: CARD_W,
            height: cardH,
            overflow: "hidden",
            borderRadius: 36,
            boxShadow: "0 30px 80px rgba(0,0,0,0.6)",
            border: "3px solid rgba(244,234,213,0.25)",
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              transform: `scale(${zoom})`,
              transformOrigin: `${focus.x * 100}% ${focus.y * 100}%`,
            }}
          >
            <Img
              src={staticFile(scene.src)}
              style={{
                position: "absolute",
                width: IMG_W * scale,
                height: IMG_H * scale,
                left: -crop.x * scale,
                top: -crop.y * scale,
              }}
            />
          </div>
        </div>

        <Caption text={scene.caption} />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.65) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

export const CatStory: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0d0a" }}>
      <Series>
        {SCENES.map((scene, i) => (
          <Series.Sequence key={i} durationInFrames={SCENE_FRAMES}>
            <SceneView scene={scene} />
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};
