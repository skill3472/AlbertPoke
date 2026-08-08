"""
Generates a new VAPID keypair for Web Push (see push/service.py).

Run with: uv run python src/scripts/generate_vapid_keys.py

Prints VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY in the raw urlsafe-base64 form that
config.py and push/service.py expect - paste them straight into .env locally or
into GitHub secrets for deployment. Rotating these invalidates every existing
browser push subscription, since they're signed against the old public key.
"""

import base64

from py_vapid import Vapid02


def generate_vapid_keys() -> tuple[str, str]:
    vapid = Vapid02()
    vapid.generate_keys()

    private_value = vapid.private_key.private_numbers().private_value
    private_raw = private_value.to_bytes(32, "big")
    private_key = base64.urlsafe_b64encode(private_raw).rstrip(b"=").decode()

    public_numbers = vapid.public_key.public_numbers()
    x = public_numbers.x.to_bytes(32, "big")
    y = public_numbers.y.to_bytes(32, "big")
    public_raw = b"\x04" + x + y
    public_key = base64.urlsafe_b64encode(public_raw).rstrip(b"=").decode()

    return public_key, private_key


if __name__ == "__main__":
    public_key, private_key = generate_vapid_keys()
    print(f"VAPID_PUBLIC_KEY={public_key}")
    print(f"VAPID_PRIVATE_KEY={private_key}")
