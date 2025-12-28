import time
import m_data_responder_module as drm

pulse = time.monotonic()
last_time = time.monotonic()


while True:
    now = time.monotonic()
    change_time = time.monotonic()

    if change_time - last_time < 3:
        pulse = time.monotonic()

    if change_time - last_time > 3:
        pulse = time.monotonic() - 20
        last_time = change_time

    print(drm.mac_hb_checker(pulse, now, 5), pulse, now, change_time, last_time)

    time.sleep(0.5)


