from sys import argv
from os import getenv, execvp
from pathlib import Path
from typing import List
from glob import glob
from mimetypes import guess_type
from subprocess import Popen, PIPE
import subprocess

# Type of results
result_type: str

# Search query
query: str

# Current working directory
current_dir: str

# Max number of results
max_results: int = 100

# List of valid result types
result_types: List[str] = ["images", "videos", "audio", "media", "all"]

# The path were the symlinks are created
results_path: str = "/tmp/symview_results"

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# Get input information using rofi
def get_input(prompt: str) -> str:
  proc = Popen(f"rofi -dmenu -p {prompt}", stdout=PIPE, stdin=PIPE, shell=True, text=True)
  return proc.communicate()[0].strip()

# Get arguments. Might exit here
def get_args() -> None:
  global query
  global result_type
  global current_dir

  if (len(argv) < 2):
    exit()

  result_type = argv[1]

  if result_type not in result_types:
    s = " ".join(result_types)
    print(f"{result_type} is not a valid result type.\nValid result types are: {s}")
    exit()
  
  if len(argv) < 3:
    query = get_input("Input Seach Query")
  else:
    query = " ".join(argv[2:])

  if query == "":
    exit()

  current_dir = clean_path(str(getenv("PWD")))

# Check if file is of a certain type
def is_type(t, f):
  g = guess_type(f)[0]
  return g and g.startswith(t)

# Get file matches
def get_results() -> List[str]:
  # Matches found
  results = []

  # Search query
  sq = f"{current_dir}/**/*{query}*"

  # Make results case insensitive
  def either(c):
    return "[%s%s]" % (c.lower(), c.upper()) if c.isalpha() else c

  # Search files recursively
  for f in glob("".join(map(either, sq)), recursive = True):
    p = Path(f)

    if p.is_dir() or p.is_symlink():
      continue

    include = False

    if result_type == "images":
      include = is_type("image", f)

    elif result_type == "videos":
      include = is_type("video", f)

    elif result_type == "audio":
      include = is_type("audio", f)

    elif result_type in "media":
      include = is_type("image", f) or \
                is_type("video", f) or \
                is_type("audio", f)

    elif result_type == "all":
      include = True
  
    if include:
        results.append(f)
        if len(results) >= max_results:
          break  
  
  return results

# Do operations with the matched files
def process_results(results: List[str]) -> None:
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
      
      # Fill numbers to the left until name is unique
      for n in range(2, 22):
        link = rp / Path(str(n) + name)
        if not link.exists():
          break

    if link.exists():
      continue

    link.symlink_to(src)

  # Open the file manager
  subprocess.call(["xdg-open", results_path])

# Main function
def main() -> None:
  get_args()

  results = get_results()
    
  if len(results) > 0:
    process_results(results)
  
# Program starts here
if __name__ == "__main__": main()