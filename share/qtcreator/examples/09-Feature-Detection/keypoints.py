# Object tracking with keypoints example.
# Show the camera an object and then run the script. A set of keypoints will be extracted
# once and then tracked in the following frames. If you want a new set of keypoints re-run
# the script. NOTE: see the docs for arguments to tune find_keypoints and match_keypoints.
import sensor, time, image

# Reset sensor
sensor.reset()

# Sensor settings
sensor.set_contrast(1)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((240, 240))
sensor.set_pixformat(sensor.GRAYSCALE)

sensor.set_auto_gain(False, value=100)
sensor.skip_frames(30)

def draw_keypoints(img, kpts):
    print(kpts)
    img.draw_keypoints(kpts)
    img = sensor.snapshot()
    time.sleep(1000)

kpts1 = None
# NOTE: uncomment to load a keypoints descriptor from file
#kpts1 = image.load_descriptor("/desc.orb")
#img = sensor.snapshot()
#draw_keypoints(img, kpts1)

clock = time.clock()
while (True):
    clock.tick()
    img = sensor.snapshot()
    if (kpts1 == None):
        # NOTE: By default find_keypoints returns multi-scale keypoints extracted from an image pyramid.
        kpts1 = img.find_keypoints(max_keypoints=150, threshold=20, scale_factor=1.1)
        draw_keypoints(img, kpts1)
    else:
        # NOTE: When extracting keypoints to match the first descriptor, we use normalized=True to extract
        # keypoints from the first scale only, which will match one of the scales in the first descriptor.
        kpts2 = img.find_keypoints(max_keypoints=150, threshold=20, normalized=True)
        if (kpts2):
            c = image.match_descriptor(kpts1, kpts2, threshold=80)
            match = c[6] # C[6] contains the number of matches.
            if (match>5):
                img.draw_rectangle(c[2:6])
                img.draw_cross(c[0], c[1], size=10)

            print(kpts2, "matched:%d dt:%d"%(match, c[7]))
            # NOTE: uncomment if you want to draw the keypoints
            #img.draw_keypoints(kpts2, size=KEYPOINTS_SIZE, matched=True)

    # Draw FPS
    img.draw_string(0, 0, "FPS:%.2f"%(clock.fps()))
