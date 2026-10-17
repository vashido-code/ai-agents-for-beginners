# ComfyUI workflows

Нужны только для провайдера `comfyui`. Положите сюда два графа, экспортированных из ComfyUI через *Settings → Dev mode → Save (API Format)*:

| Файл | Что делает | Пример моделей |
|---|---|---|
| `tryon_api.json` | фото модели + фото одежды → модель в этой одежде | CatVTON, IDM-VTON, FLUX Kontext |
| `i2v_api.json` | фото → короткое видео | Wan 2.x image-to-video, LTX-Video |

Затем откройте `studio/providers/comfyui.py` и поправьте `WORKFLOWS[...]["bind"]`: для каждого поля (`person`, `garment`, `image`, `prompt`, `negative`, `seed`, `frames`, `prefix`) укажите `(id узла, имя входа)` из вашего JSON. Сейчас там заглушки. Если id неверный, прототип остановится с ошибкой, а не сгенерирует не то.
