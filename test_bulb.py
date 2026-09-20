import time
from calex import CalexBulb


bulb = CalexBulb()


def pause(seconds=0.5):
    time.sleep(seconds)


def fade_colour(start, end, duration=2.0, steps=40):

    for i in range(steps + 1):
        t = i / steps

        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)

        bulb.rgb(r, g, b)

        time.sleep(duration / steps)


def fade_brightness(start, end, duration=2.0, steps=20):
    """Smoothly change brightness."""

    for i in range(steps + 1):
        t = i / steps
        value = start + (end - start) * t

        bulb.brightness(value)

        time.sleep(duration / steps)


print("CALEX RGB+CCT SHOW")
print("===================")

print("Starting...")

bulb.on()
bulb.brightness(10)
bulb.rgb(0, 0, 0)

pause(1)

print("Electric blue")

fade_colour(
    (0, 0, 0),
    (0, 80, 255),
    2
)

fade_brightness(10, 80, 1.5)

pause(1)

print("Siren mode")

for _ in range(4):

    bulb.brightness(100)
    bulb.rgb(255, 0, 0)
    pause(0.25)

    bulb.rgb(0, 0, 255)
    pause(0.25)


print("Purple")

fade_colour(
    (0, 0, 255),
    (180, 0, 255),
    2
)

pause(1)


print("Sunset")

fade_colour(
    (180, 0, 255),
    (255, 40, 0),
    3
)

fade_colour(
    (255, 40, 0),
    (255, 160, 20),
    3
)

fade_brightness(80, 35, 3)

pause(1)

print("Entering deep space")

fade_colour(
    (255, 160, 20),
    (40, 0, 100),
    4
)

fade_brightness(35, 15, 3)

pause(1)

print("Final flash")

bulb.rgb(255, 255, 255)
bulb.brightness(100)

pause(0.5)

bulb.brightness(50)

pause(0.5)

bulb.brightness(10)

pause(1)


print("Demo complete.")

bulb.off()
