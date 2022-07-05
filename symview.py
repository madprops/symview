#!/usr/bin/env python

from sys import argv
from os import getenv, execvp
from pathlib import Path
from typing import List
from glob import glob
from mimetypes import guess_type
from subprocess import Popen, PIPE
import subprocess

# Max number of results
max_results: int = 100

# List of valid result types
result_types: List[str] = ["images", "videos", "audio", "media", "all"]

# The path were the symlinks are created
results_path: str = "/tmp/symview_results"

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# Get current working directory
def pwd() -> str:
  return clean_path(str(getenv("PWD")))

# Get input information using rofi
def get_input(prompt: str) -> str:
  proc = Popen(f"rofi -dmenu -p {prompt}", stdout=PIPE, stdin=PIPE, shell=True, text=True)
  return proc.communicate()[0].strip()

# Print how to use it
def print_help():
  s = ", ".join(result_types)
  print("Format: program [result_type] [filter]")
  print(f"Result types: {s}")


# Get arguments. Might exit here
def get_args():
  if (len(argv) < 2):
    print_help()
    exit(1)

  result_type = argv[1]

  if result_type not in result_types:
    print_help()
    exit(1)
  
  if len(argv) < 3:
    query = get_input("Input Seach Query")
  else:
    query = " ".join(argv[2:])

  if query == "":
    exit()

  return {"type": result_type, "query": query}

# Check if file is of a certain type
def is_type(t: str, f: str) -> bool:
  try:
    g = guess_type(f)[0]
    if g is None: return False
    return g.startswith(t)
  except:
    return False

# Get file matches
def get_results(args) -> List[str]:
  # Matches found
  results = []

  # Search query
  a = pwd()
  b = args["query"]
  sq = f"{a}/**/*{b}*"

  # Make results case insensitive
  def either(c: str) -> str:
    return "[%s%s]" % (c.lower(), c.upper()) if c.isalpha() else c

  # Search files recursively
  for f in glob("".join(map(either, sq)), recursive = True):
    p = Path(f)

    if p.is_dir() or p.is_symlink():
      continue

    include = False

    if args["type"] == "images":
      include = is_type("image", f)

    elif args["type"] == "videos":
      include = is_type("video", f)

    elif args["type"] == "audio":
      include = is_type("audio", f)

    elif args["type"] == "media":
      include = is_type("image", f) or \
                is_type("video", f) or \
                is_type("audio", f)

    elif args["type"] == "all":
      include = True
  
    if include:
        results.append(f)
        if len(results) >= max_results:
          break  
  
  return results

# Do operations with the matched files
def process_results(results: List[str]) -> None:
  rpath = clean_path(results_path)
  rp = Path(rpath)

  # Create results dir in /tmp
  rp.mkdir(exist_ok = True)
  
  # Remove previous results
  for f in glob(rpath + "/*"):
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
  subprocess.call(["xdg-open", rpath])

# Main function
def main() -> None:
  if not results_path.startswith("/tmp/"):
    exit("Make sure results_path is properly set.")

  results = get_results(get_args())
    
  if len(results) > 0:
    process_results(results)
  
# Program starts here
if __name__ == "__main__": main()