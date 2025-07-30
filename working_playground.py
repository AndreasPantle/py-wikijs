#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wikijs import WikiJSClient

client = WikiJSClient(
    base_url="https://wikijs.hotserv.cloud",
    auth="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjEsImdycCI6MSwiaWF0IjoxNTM4ODM1NTQ1LCJleHAiOjE3ODUzOTMxNDUsImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.d1fCZMqS-4gR5TfcMU4CLc_mD-uyYxlUxPbxbqqdIazruKKmBLACkVEumf-RFgEatsuCQjQiU0A6E_IfwFBgqFy1g5W_Ly9st7_5k6JOHfn4shGnCrRv3FBLHOtiRUexURcXNvHxh00oEJ8IPuhmTDSpc1g5ssVeNR9oHwz8V-CIvtmP_S5NIalTVEeOXmSSfyHXK4_sMx8zbBb8tCHNt1tbhZ8Z5N--pqvWZFC_ddYZ8-kMkQo-ni1rP48WLpEngWCij6mAPKhdqLjykmIkZF_hwnfvunG7iIZpFVoUJ3uIc09GkIVa5VdpcBHD4w1rnpouWZP8FuR9aHlAL7sB3Q"
)

print("✅ Client created")
print("✅ Connection:", client.test_connection())
pages = client.pages.list()
print(f"✅ Found {len(pages)} pages")
for i, page in enumerate(pages[:5], 1):
    print(f"  {i}. {page.title} (ID: {page.id})")
client.close()
print("✅ SDK working!")
