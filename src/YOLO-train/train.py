from ultralytics import YOLO
# Load a model
model = YOLO("yolo11n.pt")

results = model.train(data='google_colab_config.yaml', epochs=5)

print('a')