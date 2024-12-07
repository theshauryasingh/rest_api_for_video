import cv2

def trim_video(input_path, output_path, start_time, end_time):
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {input_path}")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    current_frame = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if start_frame <= current_frame <= end_frame:
            out.write(frame)
        current_frame += 1

        if current_frame > end_frame:
            break

    cap.release()
    out.release()

def merge_videos(video_paths, output_path):
    caps = [cv2.VideoCapture(path) for path in video_paths]
    fps = int(caps[0].get(cv2.CAP_PROP_FPS))
    width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))

    for cap in caps:
        if (int(cap.get(cv2.CAP_PROP_FPS)) != fps or
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) != width or
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) != height):
            raise ValueError("All videos must have the same resolution and frame rate.")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for cap in caps:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        cap.release()

    out.release()
