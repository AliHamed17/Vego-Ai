"""
Transcribe Hebrew MP4 videos using OpenAI Whisper.
Outputs transcript as .txt and .srt (with timestamps).
"""
import os
import sys
import glob
import io

# Fix Windows console encoding for Hebrew output
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import whisper

# Add imageio-ffmpeg binary directory to PATH so whisper can find ffmpeg
try:
    import imageio_ffmpeg
    ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
    print(f"[INFO] Using ffmpeg from: {ffmpeg_dir}")
except ImportError:
    print("[WARN] imageio-ffmpeg not found, hoping ffmpeg is on PATH")

def transcribe_video(video_path, model, output_dir=None):
    """Transcribe a single video file and save results."""
    if output_dir is None:
        output_dir = os.path.dirname(video_path)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    txt_path = os.path.join(output_dir, f"{base_name}_transcript.txt")
    srt_path = os.path.join(output_dir, f"{base_name}_transcript.srt")

    print(f"\n{'='*60}")
    print(f"Transcribing: {video_path}")
    print(f"{'='*60}")

    # Transcribe with Hebrew language
    result = model.transcribe(
        video_path,
        language="he",        # Hebrew
        task="transcribe",    # Keep in Hebrew (use "translate" for English)
        verbose=False
    )

    # Save plain text transcript
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result["text"])
    print(f"\n[OK] Plain text saved: {txt_path}")

    # Save SRT with timestamps
    segments = result.get("segments", [])
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp_srt(seg["start"])
            end = format_timestamp_srt(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    print(f"[OK] SRT subtitles saved: {srt_path}")

    return txt_path, srt_path, result["text"]

def format_timestamp_srt(seconds):
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def main():
    # Find all MP4 files in the presentations directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mp4_files = glob.glob(os.path.join(script_dir, "*.mp4"))

    if not mp4_files:
        print("No MP4 files found in presentations directory.")
        sys.exit(1)

    print(f"Found {len(mp4_files)} MP4 file(s):")
    for f in mp4_files:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  - {os.path.basename(f)} ({size_mb:.1f} MB)")

    # Load Whisper model - "base" is a good balance of speed/accuracy
    # Use "small" or "medium" for better accuracy (slower)
    print("\nLoading Whisper model ('base')...")
    print("(First run will download the model, ~140 MB)")
    model = whisper.load_model("base")
    print("[OK] Model loaded.")

    # Transcribe each MP4
    results = []
    for mp4_path in mp4_files:
        txt_path, srt_path, text = transcribe_video(mp4_path, model)
        results.append((mp4_path, txt_path, srt_path, text))

    # Summary
    print(f"\n{'='*60}")
    print("TRANSCRIPTION COMPLETE")
    print(f"{'='*60}")
    for mp4_path, txt_path, srt_path, text in results:
        print(f"\nVideo: {os.path.basename(mp4_path)}")
        print(f"  Text: {txt_path}")
        print(f"  SRT:  {srt_path}")
        print(f"  Preview: {text[:200]}...")

if __name__ == "__main__":
    main()
