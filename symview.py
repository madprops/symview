from sys import argv
from os import getenv, execvp
from pathlib import Path
from typing import List
from glob import glob
import subprocess

# Type of results
result_type: str

# Search keyword
keyword: str

# Current working directory
current_dir: str

# Max number of results
max_results: int = 100

# List of valid result types
result_types: List[str] = ["images", "videos", "audio", "media", "all"]

# List of valid image extensions
image_exts: List[str] = [".jpg", ".png", ".gif"]

# List of valid video extensions
video_exts: List[str] = [".mp4", ".webm", ".mkv"]

# List of valid audio extensions
audio_exts: List[str] = [".mp3", ".ogg", ".flac", ".wav", ".aiff", ".m4a"]

# The path were the symlinks are created
results_path: str = "/tmp/symview_results"

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# Get arguments. Might exit here
def get_args() -> None:
  global result_type
  global keyword
  global current_dir

  if (len(argv) < 3):
    exit()

  result_type = argv[1]

  if result_type not in result_types:
    s = " ".join(result_types)
    print(f"{result_type} is not a valid result type.\nValid result types are: {s}")
    exit()

  keyword = " ".join(argv[2:])
  current_dir = clean_path(str(getenv("PWD")))

# Main function
def main() -> None:
  get_args()

  # Search query
  query = f"{current_dir}/**/*{keyword}*"

  # Matches found
  results = []

  # Make results case insensitive
  def either(c):
    return "[%s%s]" % (c.lower(), c.upper()) if c.isalpha() else c

  # Search files recursively
  for f in glob("".join(map(either, query)), recursive = True):
    p = Path(f)

    include = False
    ext = p.suffix.lower()

    if result_type == "images":
      include = ext in image_exts
    elif result_type == "videos":
      include = ext in video_exts
    elif result_type == "audio":
      include = ext in audio_exts
    elif result_type in "media":
      include = (ext in image_exts) or (ext in video_exts) or (ext in audio_exts)
    elif result_type == "all":
      include = True
  
    if include:
      if p.is_file() and not p.is_symlink():
        if f not in results:
          results.append(f)
          if len(results) >= max_results:
            break
    
  if len(results) > 0:
    rp = Path(results_path)

    # Create results dir in /tmp
    rp.mkdir(exist_ok = True)
    
    # Remove previous results
    for f in glob(results_path + "/*"):
      Path(f).unlink()

    # Create the symlinks
    for f in results:
      src = Path(f)
      link = rp / Path(f).name
      
      if link.exists():
        name = "_" + Path(f).name
        
        for n in range(2, 22):
          link = rp / Path(str(n) + name)
          if not link.exists():
            break
      
      if link.exists():
        continue

      link.symlink_to(src)

    # Open the file manager
    subprocess.call(["xdg-open", results_path])
  
# Program starts here
if __name__ == "__main__": main()