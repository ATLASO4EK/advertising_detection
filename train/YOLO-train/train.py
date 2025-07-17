from ultralytics import YOLO
# Load a model
if __name__ == '__main__':
    model = YOLO("yolo11n.pt")

    results = model.train(data='google_colab_config.yaml', epochs=100000, optimizer='Adam',
                          lr0=0.0001, device=0, patience=7, dropout=0.4,
                          save=True, save_period=5)