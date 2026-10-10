import { Composition } from "remotion";
import { CatStory, TOTAL_FRAMES } from "./CatStory";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CatStory"
      component={CatStory}
      durationInFrames={TOTAL_FRAMES}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
