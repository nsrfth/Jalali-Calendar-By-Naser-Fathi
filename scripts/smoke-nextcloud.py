#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Jalali Calendar contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Exercise the app on a disposable Nextcloud instance, never production.

Requires two existing users: an administrator and an ordinary user. Passwords
and the instance URL are supplied through the environment (see test.yml).
Only test data is written, and the off-day created by the test is deleted.
"""

import base64
import html
import http.cookiejar
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


BASE = os.environ['NEXTCLOUD_TEST_URL'].rstrip('/')
PASSWORD = os.environ['NEXTCLOUD_TEST_PASSWORD']
API = '/ocs/v2.php/apps/jalali_calendar/api/v1'


def request(path, user, method='GET', data=None, expected=200):
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(
            f'{user}:{PASSWORD}'.encode()).decode(),
        'OCS-APIRequest': 'true',
        'Accept': 'application/json',
    }
    if data is not None:
        data = json.dumps(data).encode()
        headers['Content-Type'] = 'application/json'
    if method == 'PROPFIND':
        headers['Depth'] = '1'
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        body = response.read()
        if response.status != expected:
            raise AssertionError(f'{method} {path}: expected {expected}, got {response.status}: {body[:500]!r}')
    return body


def ocs(path, user, method='GET', data=None, expected=200):
    body = request(API + path + '?format=json', user, method, data, expected)
    payload = json.loads(body)['ocs']
    if expected < 400:
        assert payload['meta']['status'] == 'ok', payload['meta']
    return payload.get('data')


def check_pages(user, admin=False):
    browser = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    with browser.open(BASE + '/index.php/login', timeout=30) as response:
        page = response.read().decode()
    token = re.search(r'data-requesttoken="([^"]+)"', page)
    assert token, 'Login page did not supply a CSRF token'
    form = urllib.parse.urlencode({
        'user': user, 'password': PASSWORD,
        'requesttoken': html.unescape(token[1]),
    }).encode()
    login = urllib.request.Request(BASE + '/index.php/login', data=form, headers={'Origin': BASE})
    with browser.open(login, timeout=30) as response:
        assert '/login' not in response.url, f'Login failed for {user}'
    pages = [
        ('/index.php/apps/jalali_calendar/', 'id="jalali_calendar"', 'main'),
        ('/index.php/apps/jalali_calendar/1405/7', 'id="jalali_calendar"', 'main'),
        ('/index.php/settings/user/jalali_calendar', 'id="jalali_calendar_personal"', 'personal'),
    ]
    if admin:
        pages.append(('/index.php/settings/admin/jalali_calendar', 'id="jalali_calendar_admin"', 'admin'))
    for path, mount, entry in pages:
        with browser.open(BASE + path, timeout=30) as response:
            page = response.read().decode()
            assert mount in page, f'Missing mount point on {path}'
            assert f'jalali_calendar-{entry}.mjs' in page, f'Missing entry point on {path}'
        bundle = re.search(r'src="([^"]*jalali_calendar-' + entry + r'\.mjs[^"]*)"', page)
        assert bundle, f'Missing script URL on {path}'
        with browser.open(urllib.parse.urljoin(BASE, html.unescape(bundle[1])), timeout=30) as response:
            assert response.read(), f'Empty {entry} frontend bundle'
    print(f'PASS: {user} login, page, deep link, settings and frontend delivery')


status = json.loads(request('/status.php', 'admin'))
assert status['installed'] and status['versionstring'] == '35.0.1', status
check_pages('admin', admin=True)
check_pages('calendar-user')

# Fresh-install migration and database schema: create, query, count and delete.
created = ocs('/offdays', 'admin', 'POST', {
    'jy': 1405, 'jm': 1, 'jd': 1, 'title': 'Compatibility smoke test', 'isOff': True,
}, expected=201)
try:
    assert created['gdate'] == '2026-03-21', created
    # Keep the date query separate from the common format=json query.
    body = request(API + '/offdays?format=json&from=2026-03-01&to=2026-04-01', 'calendar-user')
    days = json.loads(body)['ocs']['data']
    assert any(day['id'] == created['id'] for day in days), days
    assert any(day['id'] == created['id'] for day in ocs('/offdays/year/1405', 'admin'))
    ocs('/config', 'calendar-user', expected=403)
    ocs('/offdays', 'calendar-user', 'POST', {
        'jy': 1405, 'jm': 1, 'jd': 2, 'title': 'Must not be written',
    }, expected=403)
    original = ocs('/preferences', 'calendar-user')
    try:
        changed = ocs('/preferences', 'calendar-user', 'PUT', {'globalPicker': False, 'slotDuration': 15})
        assert changed['globalPicker'] is False and changed['slotDuration'] == 15, changed
        assert ocs('/preferences', 'calendar-user')['slotDuration'] == 15
    finally:
        ocs('/preferences', 'calendar-user', 'PUT', original)
    original = ocs('/config', 'admin')
    try:
        changed = ocs('/config', 'admin', 'PUT', {'firstDayOfWeek': 'sunday'})
        assert changed['firstDayOfWeek'] == 'sunday', changed
    finally:
        ocs('/config', 'admin', 'PUT', original)
finally:
    ocs(f"/offdays/{created['id']}", 'admin', 'DELETE')
print('PASS: off-day CRUD, Gregorian conversion, preferences and administrator permissions')

# The app uses this server endpoint through its bundled CalDAV library.
dav = request('/remote.php/dav/calendars/calendar-user/', 'calendar-user', 'PROPFIND', expected=207)
assert b'multistatus' in dav, dav[:500]
print('PASS: authenticated CalDAV discovery on Nextcloud 35.0.1')
