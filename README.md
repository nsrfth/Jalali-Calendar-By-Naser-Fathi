<!--
  - SPDX-FileCopyrightText: 2026 Naser Fathi
  - SPDX-License-Identifier: AGPL-3.0-or-later
-->
# Jalali Calendar for Nextcloud

‏**تقویم جلالی برای نکست‌کلاد**

Shows the calendars you already have in Nextcloud on a Persian (Jalali/Shamsi)
month grid — correct Shamsi month and weekday names, a Saturday-first week,
Persian numerals and an RTL layout.

Your data is never converted or copied. The app reads the same CalDAV
calendars as the official Calendar app, so everything stays interoperable with
your phone, Thunderbird, Outlook and any other CalDAV client. **Jalali is purely
a display layer; events are always stored as Gregorian/UTC.**

## Status

**v0.6.0 — read-only Jalali calendar, with Nextcloud 30–35 support.**

- [x] Jalali month view of **everything the Calendar app shows**: your own
      calendars, webcal subscriptions, the birthday calendar, and
      app-generated calendars such as **Deck** boards
- [x] Tasks (`VTODO`) shown on their due date, completed ones struck through
- [x] Persian month/weekday names, Saturday-first week, Persian numerals
- [x] Per-calendar colours and show/hide toggles (remembered per browser)
- [x] Recurring events expanded within the visible window, including
      `EXDATE` and modified/detached occurrences
- [x] Day panel with event details (time, location, calendar, description)
- [x] RTL layout, Farsi translation
- [x] Warns when the device timezone differs from your calendar timezone
- [x] **Administration page**: week start, off-days, and import
- [x] **Off-days** shown on the grid, with the occasion's name
- [x] **Day, Week, Month, Year and List views**
- [x] **Working hours** shaded in the day and week views
- [x] **Personal settings**: tasks, event cap, weekends, week numbers, time
      increments, CalDAV addresses
- [ ] Creating, editing and deleting events — planned for v0.2

Events are created and edited in the official Calendar app; this app coexists
with it rather than replacing it.

### Known limitations

Event times are rendered in the **browser's** timezone rather than the timezone
configured for your calendars. When the two differ the app says so, but the
displayed clock times will not match the Calendar app until v0.2 handles
timezones properly.

Recurring **tasks** are shown only at their first due date; recurring *events*
expand normally.

## Personal settings

**Settings → Personal → Jalali Calendar**, per user: show tasks, cap events in
the month view, show or hide weekends, show Jalali week numbers, choose the
time increments the day and week grids are ruled at, and copy the CalDAV
addresses for a phone or desktop client.

## Administration

**Settings → Administration → Jalali Calendar** (admin only):

**Working hours.** A start and end time, plus which weekdays count as working
days (default 09:00-17:00, Saturday to Wednesday). Hours outside them are
shaded in the day and week views, which open scrolled to the working day.

‏**Week start.** Saturday (شنبه, the Iranian default) or Sunday (یک‌شنبه).
Applies to everyone on the server: the grid, its column headers and the
weekend column all move together. Friday stays the weekend either way.

**Off-days.** Official holidays live on the server and are shown to every
user — the occasion's name appears on the day and the date takes the weekend
colour. Admins can add and remove entries by hand, or import a whole Jalali
year.

Imports are keyed by source, so re-importing replaces only what that same
source wrote before; anything added by hand always survives.

### Official Iranian holidays

Importing tries two routes in order:

1. **Live from time.ir** — `https://www.time.ir/event-year` is server-rendered
   and lists a whole Jalali year of occasions, each flagged as a holiday. Dates
   *and* names match time.ir exactly. It only ever serves the **current** Jalali
   year (`?year=` is accepted but ignored), so it is used for that year only.
2. **Bundled dataset** — `data/ir-holidays.json`, generated offline from the
   [`shamsi-holidays`](https://www.npmjs.com/package/shamsi-holidays) package,
   covering Jalali **1400-1406**. Used for any other year, or if time.ir is
   unreachable. Regenerate with `npm run generate:holidays`.

**Know this about the bundled dataset:** it computes lunar (religious) holidays
on Umm al-Qura reckoning, which runs a day earlier than Iran's official
reckoning. Arbaeen 1405 is 12 Mordad there but 13 Mordad on time.ir. Solar
national days and weekly Fridays are unaffected. That is why the live route is
preferred for the current year.

The upstream dataset also marks every Friday as a holiday (52 of a year's 75
entries). Those are skipped — the grid already draws Friday as the weekend, so
importing them would only print a generic label on every Friday cell.

For a year neither route covers, or a non-Iranian holiday set, use the
**iCalendar (.ics)** importer — parsed with the sabre/vobject Nextcloud bundles.

## Where events come from

The app lists the same collections as the official Calendar app, via
`findAllCalDAVCollectionsGrouped()`:

| Source | Component | Notes |
|---|---|---|
| Personal / shared calendars | `VEVENT` + `VTODO` | |
| **Deck** boards | `VTODO` only | Named `Deck: <board>`; cards appear on their due date |
| webcal subscriptions | `VEVENT` (+ `VTODO`) | Honours the "strip todos" flag |
| Birthday calendar | `VEVENT` | |
| Tasks app lists | `VTODO` | Shown on the due date |

Two details are easy to get wrong and are covered by tests:

- `findAllCalendars()` **excludes subscriptions**, so it is deliberately not
  used — holiday and other webcal calendars would silently vanish.
- Deck advertises `supported-calendar-component-set = VTODO` **only**. Filtering
  calendars on `VEVENT`, or querying boards for `VEVENT`, hides every board.

Each collection is asked only for the component types it actually advertises,
so a Deck board costs exactly one CalDAV request.

## Requirements

- Nextcloud **30–35**. The UI is built on `@nextcloud/vue` 9, which
  officially targets 31+, but the app bundles its own Vue 3 runtime and uses
  only layout components and long-standing colour variables. Verified running
  on 30.0.17; on 30 some spacing/colour details may differ from 31+.
- PHP **8.1–8.5**, subject to the requirements of your Nextcloud version.
  Nextcloud 35 requires **PHP 8.3–8.5**.
- Node 20+ and npm (to build from source)

The Nextcloud 35 compatibility change was tested on **35.0.1 with PHP 8.5.11
and SQLite**: normal activation, authenticated HTTP pages and APIs passed.
The smoke test does not execute the frontend in a browser or validate an
existing production deployment.

## Install from source

```bash
git clone https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi.git
cd Jalali-Calendar-By-Naser-Fathi
npm ci
npm run build
```

Then place (or symlink) the directory into your server's app folder and enable it:

```bash
ln -s "$PWD" /path/to/nextcloud/custom_apps/jalali_calendar
occ app:enable jalali_calendar
```

The directory name **must** be `jalali_calendar` — Nextcloud resolves the app
namespace from it.

While working on the frontend, `npm run watch` rebuilds on change; reload the
browser to pick the bundle up.

## Tests

```bash
npm run test
```

The suite covers the Jalali conversion helpers (leap years, month boundaries,
Nowruz, grid construction) and the iCalendar parsing layer (recurrence
expansion, `EXDATE`, overridden occurrences, all-day `DTEND` exclusivity).

CI also installs the release package on a disposable **Nextcloud 35.0.1**
instance with SQLite and enables it without `--force`. The HTTP smoke test
checks login, the calendar page and deep links, administration and personal
settings, off-day CRUD, user preferences, administrator permissions, delivery
of the built frontend and authenticated CalDAV discovery.
`scripts/smoke-nextcloud.py` writes test data; run it only against a disposable
instance with the two test users configured as in `.github/workflows/test.yml`.

Dates are built from *local* calendar fields, so the tests are run under
several timezones in CI (`UTC`, `Asia/Tehran`, `America/New_York`). Run them
the same way locally if you touch date handling:

```bash
TZ=America/New_York npm run test
```

## How it works

```
Browser (Vue 3 SPA)
  ├─ src/utils/jalali.js   Gregorian ↔ Jalali, month grid construction
  ├─ src/utils/events.js   ical.js parsing + recurrence expansion
  ├─ src/utils/caldav.js   @nextcloud/cdav-library → /remote.php/dav
  └─ src/store/            shared reactive state
        ▲
        │ initial state (timezone, deep-linked month)
PHP backend
  ├─ Controller/PageController      page shell + initial state
  ├─ Controller/OffDayController    off-day CRUD + import (OCS)
  ├─ Controller/AdminConfigController
  ├─ Service/JalaliConverter        Jalali <-> Gregorian, server side
  ├─ Service/ImportService          time.ir API / .ics feeds
  └─ Db/OffDayMapper                table `jalali_offdays`
```

Calendar *events* never touch the backend — they go straight from the browser
to CalDAV, exactly as the official Calendar app does. Only the off-day list
and the instance settings are server-side.

`JalaliConverter` is a port of the `jalaali-js` algorithm the frontend uses.
The two are checked against each other by comparing SHA-256 digests over every
date in Jalali years 1300-1450 and Gregorian 1920-2070 — they agree exactly.

Rendering a Jalali month means fetching the *Gregorian* window that covers it.
`buildMonthGrid()` always returns six full weeks starting on a Saturday, and
its `rangeStart`/`rangeEnd` are handed to a CalDAV time-range `REPORT`.

### Deep links

`/apps/jalali_calendar/1405/5` opens Mordad 1405 directly.

## Publishing to the app store

0. Add at least one screenshot. `info.xml` points at
   `screenshots/month-view.png` in this repo's `main` branch; the URL must
   resolve before the store will accept the release.
1. Request a certificate for the app id `jalali_calendar` at
   [nextcloud/app-certificate-requests](https://github.com/nextcloud/app-certificate-requests).
2. Put the private key at `~/.nextcloud/certificates/jalali_calendar.key`.
3. `make appstore` — builds `build/artifacts/jalali_calendar.tar.gz` and, when
   the key is present, writes the matching `.sig`.
4. Tag and push (`git tag v0.1.0 && git push --tags`); the release workflow
   builds, signs and attaches both files. It needs the key in the
   `APP_SIGNING_KEY` repository secret.
5. Register the app at [apps.nextcloud.com](https://apps.nextcloud.com) and
   submit the release download URL plus the signature.

`info.xml` is validated against the official schema on every push.

## Licence

AGPL-3.0-or-later. See [LICENSE](LICENSE).
