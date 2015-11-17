# TODO: build temp dir based on TEMPO_FACTOR
# don't delete things until it's definitely created
# don't regenerate things if they're already there.
# downside: leaves huge folders around
# upside: faster processing on failures

#!/usr/local/bin/python
from subprocess import call
from uuid import uuid1

# seconds
TEMPO_FACTOR = 16
CUT_DURATION = .2 / TEMPO_FACTOR
TARGET_DURATION = 15
TOTAL_CUTS = TARGET_DURATION / CUT_DURATION

film_length = 605

INTERVAL_LENGTH = film_length / TOTAL_CUTS 

# ffmpeg -ss 00:00:00.000 -i input_file.mp4 -t 00:00:00.000 000001.mp4
duration = CUT_DURATION
filename = "VIDEO0030.mp4"
start_time = 0
clip = 0
ffmpeg_format = "ffmpeg -ss %.3f -i %s -t %.3f %s"

# create tmp directory for clips
temp_dir_name = str(uuid1())
print temp_dir_name
call("mkdir %s" % temp_dir_name, shell=True)

# create the temp video files
clip_names = []
while start_time < film_length:
  # create the clip filename and collect all names in a list for use later
  clip_name = "%05d.mp4" % clip
  clip_names.append(clip_name)

  clip_dest = "%s/%s" % (temp_dir_name, clip_name)
  
  cmd = ffmpeg_format % (start_time, filename, duration, clip_dest)
  call(cmd, shell=True)

  clip += 1
  start_time += INTERVAL_LENGTH

# create the txt file for ffmpeg concatenation
filename = temp_dir_name + "/concat.txt"
call("touch %s" % filename, shell=True)
concat = open(filename, "w")

# write each clip name to that file
for clip in clip_names:
  line = "file '%s'" % clip
  concat.write(line + "\n")
concat.close()

# execute ffmpeg concat
out = TEMPO_FACTOR
cmd = "ffmpeg -f concat -i %s -c copy x%s.mp4" % (filename, out)
status = call(cmd, shell=True)

print status
if status == 0:
  # clean up temp dir
  call("rm -rf %s" % temp_dir_name, shell=True)
