import sys
import argparse
import time

# Simulate GPIO ports
import fake_rpi
sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO

from gsmHat import GSMHat, SMS, GPS

import logging
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main(args):
    hat = GSMHat(args.serial_port, args.serial_port_speed)
    hat.SetGPRSconnection(args.gprs_apn, args.gprs_apn_user, args.gprs_apn_password)

    logging.info("Call url")
    hat.CallUrl(args.url)

    logging.info("start pooling for http response")
    while True:
        if hat.UrlResponse_available() > 0:
            resp = hat.UrlResponse_read()
            logger.info(f"HTTP response: {resp}")
            break

        time.sleep(1)

    logging.info("end")

def parse_args(argv):
    p = argparse.ArgumentParser(description='Test GSMHat.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, help='verbose output. specify twice for debug-level output.')
    p.add_argument("--serial-port", action="store", help="Path of the serial port with the GPRS/GNSS hat.", default="/dev/ttyS0")
    p.add_argument("--serial-port-speed", action="store", help="Serial port speed.", default=115200)
    p.add_argument("--gprs-apn", action="store", help="GPRS APN.", default="TM")
    p.add_argument("--gprs-apn-user", action="store", help="GPRS APN user.", default="")
    p.add_argument("--gprs-apn-password", action="store", help="GPRS APN password.", default="")
    p.add_argument("--url", action="store", help="URL called.", default="http://eth0.me")

    args = p.parse_args(argv)

    return args


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif args.verbose > 0:
        logger.setLevel(logging.INFO)

    main(args)
