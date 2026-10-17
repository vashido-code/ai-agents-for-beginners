"""Settings you are expected to edit: marketplace specs, video prompts, costs and prices."""

import os

# Marketplace output formats. These follow the public seller requirements as of 2026
# (WB video cover: 9:16, 6-30 s). Re-check them in the seller dashboards before launch,
# the platforms change them without much notice.
MARKETPLACES = {
    "wb": {
        "label": "Wildberries",
        "photo_size": (900, 1200),  # 3:4
        "video_size": (1080, 1920),  # 9:16
        "video_min_s": 6,
        "video_max_s": 30,
    },
    "ozon": {
        "label": "Ozon",
        "photo_size": (900, 1200),  # 3:4
        "video_size": (1080, 1080),  # 1:1 (16:9 is also accepted)
        "video_min_s": 6,
        "video_max_s": 30,
    },
}

CATEGORIES = ("top", "bottom", "dress", "outerwear")

# Image-to-video prompts per garment category. The goal is a product video, so the motion is
# slow and the garment stays in frame. Write prompts in English: video models follow it best.
VIDEO_PROMPTS = {
    "top": "The model slowly turns from a three-quarter view to face the camera, adjusts the sleeve, "
           "soft studio light, static camera, the garment fabric and fit clearly visible.",
    "bottom": "The model takes two slow steps towards the camera and stops, full body in frame, "
              "soft studio light, static camera, the trousers drape naturally.",
    "dress": "The model makes a slow half turn so the dress swings gently, full body in frame, "
             "soft studio light, static camera, the silhouette and fabric clearly visible.",
    "outerwear": "The model slowly opens the jacket with one hand and turns slightly to the side, "
                 "soft studio light, static camera, the cut and lining clearly visible.",
}
VIDEO_NEGATIVE = (
    "blurry, distorted body, extra limbs, warped hands, changing clothes, garment changes colour, "
    "text, watermark, logo, fast motion, camera shake"
)
VIDEO_SECONDS = 5

# Cost of one generation in roubles, used for the margin report in the manifest.
# ESTIMATES: replace them with your real tariff (aggregator price list or GPU rent / throughput).
COSTS_RUB = {
    "mock": {"try_on": 0, "video_per_s": 0},
    "kling": {"try_on": 10, "video_per_s": 14},
    "comfyui": {"try_on": 2, "video_per_s": 4},
}

# What the client pays for one look (photos + video for every marketplace). A hypothesis to test.
PRICE_PER_LOOK_RUB = int(os.getenv("STUDIO_PRICE_PER_LOOK_RUB", "2000"))
