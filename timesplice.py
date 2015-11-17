#!/usr/local/bin/python

import datetime
import argparse
from subprocess import call
from uuid import uuid1

now = datetime.datetime.now()
default_out_name = "timespliced_%d_%02d_%02d_%02d.mp4" % (now.year, now.hour, now.minute, now.second)
print default_out_name

parser = argparse.ArgumentParser(description="Converts a given video into a short clip of small splices from throughout the entire original video clip.")
parser.add_argument("in_file", type=str, help="Name of the input file.")
parser.add_argument("--out_file", type=str, default=default_out_name, help="Name of the output file to be created.")
parser.add_argument("--in_length", type=int, default=605, help="User-known length (in seconds) of the original video. Defaults to 605 seconds.")
parser.add_argument("--out_length", type=int, default=15, help="Length (in seocnds) of the output video.")
parser.add_argument("--splice_length", type=float, default=.2, help="Length of each splice. Defaults to .2 seconds. The final video will be the concatenation of .2 second splices evenly distributed from the original video.")
parser.add_argument("--scale", type=int, default=1, help="Divides the given splice_length by a whole number. Useful to toy with for finding a comfortable splice length. Equation: splice_length / scale. Defaults to 1.")

# TODO: build temp dir based on TEMPO_FACTOR
# don't delete things until it's definitely created
# don't regenerate things if they're already there.
# downside: leaves huge folders around
# upside: faster processing on failures

args = parser.parse_args()

# seconds
IN_LENGTH = args.in_length
OUT_LENGTH = args.out_length

IN_FILE = args.in_file
OUT_FILE = args.out_file

TEMPO_FACTOR = args.scale
SPLICE_DURATION = args.splice_length / TEMPO_FACTOR
TOTAL_CUTS = OUT_LENGTH / SPLICE_DURATION
INTERVAL_LENGTH = IN_LENGTH / TOTAL_CUTS 

# ffmpeg -ss 00:00:00.000 -i input_file.mp4 -t 00:00:00.000 000001.mp4
duration = SPLICE_DURATION
start_time = 0
clip = 0
ffmpeg_format = "ffmpeg -ss %.3f -i %s -t %.3f %s"

# create tmp directory for clips
temp_dir_name = OUT_FILE.split(".")[0]
print temp_dir_name
call("mkdir %s" % temp_dir_name, shell=True)

# create the temp video files
clip_names = []
while start_time < IN_LENGTH:
  # create the clip filename and collect all names in a list for use later
  clip_name = "%05d.mp4" % clip
  clip_names.append(clip_name)

  clip_dest = "%s/%s" % (temp_dir_name, clip_name)
  
  cmd = ffmpeg_format % (start_time, IN_FILE, duration, clip_dest)
  call(cmd, shell=True)

  clip += 1
  start_time += INTERVAL_LENGTH

# create the txt file for ffmpeg concatenation
concat_filename = temp_dir_name + "/concat.txt"
call("touch %s" % concat_filename, shell=True)
concat = open(concat_filename, "w")

# write each clip name to that file
for clip in clip_names:
  line = "file '%s'" % clip
  concat.write(line + "\n")
concat.close()

# execute ffmpeg concat
cmd = "ffmpeg -f concat -i %s -c copy %s" % (concat_filename, OUT_FILE)
status = call(cmd, shell=True)

print status
if status == 0:
  # clean up temp dir
  call("rm -rf %s" % temp_dir_name, shell=True)
