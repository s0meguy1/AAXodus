#!/usr/bin/env python
# stolen from https://github.com/inAudible-NG/audible-activator
import os
import sys
import time
import base64
import common
import hashlib
import binascii
import requests
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from optparse import OptionParser

# Import webdriver-manager to automatically manage the Chrome driver
from webdriver_manager.chrome import ChromeDriverManager

PY3 = sys.version_info[0] == 3

if PY3:
    from urllib.parse import urlencode, urlparse, parse_qsl
else:
    from urllib import urlencode
    from urlparse import urlparse, parse_qsl


def fetch_activation_bytes(username, password, options):
    base_url = 'https://www.audible.com/'
    base_url_license = 'https://www.audible.com/'
    lang = options.lang

    # Step 0: Setup Chrome options
    opts = webdriver.ChromeOptions()
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko")
    # opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')

    # Step 1: Build the login URL based on username and language
    if '@' in username:  # Amazon login using email address
        login_url = "https://www.amazon.com/ap/signin?"
    else:  # Audible member login using username (untested)
        login_url = "https://www.audible.com/sign-in/ref=ap_to_private?forcePrivateSignIn=true&rdPath=https%3A%2F%2Fwww.audible.com%2F%3F"
    if lang == "uk":
        login_url = login_url.replace('.com', ".co.uk")
        base_url = base_url.replace('.com', ".co.uk")
    elif lang == "jp":
        login_url = login_url.replace('.com', ".co.jp")
        base_url = base_url.replace('.com', ".co.jp")
    elif lang == "au":
        login_url = login_url.replace('.com', ".com.au")
        base_url = base_url.replace('.com', ".com.au")
    elif lang == "in":
        login_url = login_url.replace('.com', ".in")
        base_url = base_url.replace('.com', ".in")
    elif lang != "us":  # For other languages
        login_url = login_url.replace('.com', "." + lang)
        base_url = base_url.replace('.com', "." + lang)

    # Create a player ID (kept constant to avoid hogging activation slots)
    if PY3:
        player_id = base64.encodebytes(hashlib.sha1(b"").digest()).rstrip()
        player_id = player_id.decode("ascii")
    else:
        player_id = base64.encodestring(hashlib.sha1(b"").digest()).rstrip()
    if options.player_id:
        player_id = base64.encodestring(binascii.unhexlify(options.player_id)).rstrip()
    print("[*] Player ID is %s" % player_id)

    payload = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.mode': 'logout',
        'openid.assoc_handle': 'amzn_audible_' + lang,
        'openid.return_to': base_url + 'player-auth-token?playerType=software&playerId=%s=&bp_ua=y&playerModel=Desktop&playerManufacturer=Audible' % (player_id)
    }

    # Initialize the browser
    if options.firefox:
        driver = webdriver.Firefox()
    else:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)

    # Build the login URL with the query string payload
    query_string = urlencode(payload)
    url = login_url + query_string

    # Navigate to the initial URLs
    driver.get(base_url + '?ipRedirectOverride=true')
    driver.get(url)

    if os.getenv("DEBUG") or options.debug:
        print("[!] Running in DEBUG mode. You will need to login manually (for example to handle 2FA/CAPTCHA).")
        time.sleep(32)
    else:
        # Use explicit waits for the login flow
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(driver, 20)

        # Wait for and fill in the email field
        email_box = wait.until(EC.presence_of_element_located((By.ID, "ap_email")))
        email_box.send_keys(username)

        # Click the "continue" button if it exists (Amazon's two-step login)
        try:
            continue_button = wait.until(EC.element_to_be_clickable((By.ID, "continue")))
            continue_button.click()
        except Exception as e:
            print("No continue button found; perhaps the password field is already visible.")

        # Wait for and fill in the password field
        password_box = wait.until(EC.presence_of_element_located((By.ID, "ap_password")))
        password_box.send_keys(password)

        # Click the sign-in button if available; otherwise, submit the form
        try:
            sign_in_button = wait.until(EC.element_to_be_clickable((By.ID, "signInSubmit")))
            sign_in_button.click()
        except Exception as e:
            password_box.submit()

        time.sleep(2)  # Give the page some time to load

    # Allow user to manually enter one-time password if needed
    msg = "\nATTENTION: Now you may have to enter a one-time password manually. Once you are done, press enter to continue...\n Just press enter if you are not prompted to enter one..."
    if PY3:
        input(msg)
    else:
        raw_input(msg)

    # Step 2: Get the player auth token
    driver.get(base_url + 'player-auth-token?playerType=software&bp_ua=y&playerModel=Desktop&playerId=%s&playerManufacturer=Audible&serial=' % (player_id))
    current_url = driver.current_url
    o = urlparse(current_url)
    data = dict(parse_qsl(o.query))

    # Step 2.5: Switch the User-Agent for the next requests
    headers = {
        'User-Agent': "Audible Download Manager",
    }
    cookies = driver.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])

    # Step 3: De-register to free activation slots
    durl = base_url_license + 'license/licenseForCustomerToken?' \
           + 'customer_token=' + data["playerToken"] + "&action=de-register"
    s.get(durl, headers=headers)

    # Step 4: Retrieve the activation blob
    url = base_url_license + 'license/licenseForCustomerToken?' \
          + 'customer_token=' + data["playerToken"]
    response = s.get(url, headers=headers)

    with open("activation.blob", "wb") as f:
        f.write(response.content)
    activation_bytes, _ = common.extract_activation_bytes(response.content)
    print("activation_bytes: " + activation_bytes)

    # Step 5: De-register again to stop filling activation slots
    s.get(durl, headers=headers)

    time.sleep(8)
    driver.quit()


if __name__ == "__main__":
    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 0.2")
    parser.add_option("-d", "--debug",
                      action="store_true",
                      dest="debug",
                      default=False,
                      help="run program in debug mode (for example to handle 2FA or CAPTCHA)")
    parser.add_option("-f", "--firefox",
                      action="store_true",
                      dest="firefox",
                      default=False,
                      help="use Firefox instead of Chrome")
    parser.add_option("-l", "--lang",
                      action="store",
                      dest="lang",
                      default="us",
                      help="us (default) / au / in / de / fr / jp / uk (untested)")
    parser.add_option("-p",
                      action="store",
                      dest="player_id",
                      default=None,
                      help="Player ID in hex (for debugging, not for end users)")
    parser.add_option("--username",
                      action="store",
                      dest="username",
                      default=False,
                      help="Audible username (use with --password)")
    parser.add_option("--password",
                      action="store",
                      dest="password",
                      default=False,
                      help="Audible password")
    (options, args) = parser.parse_args()

    if options.username and options.password:
        username = options.username
        password = options.password
    else:
        if PY3:
            username = input("Username: ")
        else:
            username = raw_input("Username: ")
        password = getpass("Password: ")

    fetch_activation_bytes(username, password, options)
