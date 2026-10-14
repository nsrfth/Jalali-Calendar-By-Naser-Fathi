<!--
  - SPDX-FileCopyrightText: 2026 Naser Fathi
  - SPDX-License-Identifier: AGPL-3.0-or-later
-->
# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-10-14

### Fixed

- Allow installation and activation on Nextcloud 35 by extending the
  `info.xml` support range from 30–34 to 30–35. Previously, Nextcloud 35
  rejected the app before it could run. The PHP range remains 8.1–8.5
  for older Nextcloud releases; Nextcloud 35 itself requires PHP 8.3–8.5.

### Added

- A Nextcloud 35.0.1 CI integration job that installs the built app without
  `--force` and checks authenticated pages, settings, frontend delivery,
  off-day CRUD, per-user preferences, administrator permissions and CalDAV
  discovery. Locally exercised with PHP 8.5.11 and SQLite. Browser rendering
  and integrations with external calendar clients are not covered by this test.

## [0.5.0] - 2026-07-31

### Added

- **A Shamsi date picker for date fields elsewhere in Nextcloud**, Deck due
  dates above all. Those fields are `<input type="datetime-local">`, drawn by
  the browser itself: they always render a Gregorian calendar, and no locale or
  stylesheet can change that. The picker therefore adds its own trigger and a
  badge showing the Shamsi equivalent beside the field, rather than trying to
  restyle it.

  The native input stays the source of truth. It is enhanced in place and never
  replaced — apps bind their models to that exact element, and a re-created
  input loses the binding on the next render, after which the field looks fine
  and quietly stops saving. Picked dates are written through
  `HTMLInputElement`'s own value setter and announced with bubbling `input` and
  `change` events, because a plain `input.value = …` assignment updates no
  model. The existing time of day is preserved; only the date changes.

- **A personal setting to turn the picker off** (Settings → Personal → Jalali
  Calendar), on by default. Turning it off stops the script being delivered at
  all rather than loading it and having it decline to run, so opting out of
  injected JavaScript on unrelated pages is a real opt-out.

- `npm run test:parity` holds `JalaliConverter.php` and jalaali-js to the same
  answers across 55,152 days (1925–2075) on `toJalali`, `toGregorian` and the
  round trip. The two are independent implementations, and the picker writes
  dates that the PHP side reads back, so a single day of drift would misplace
  off-days with nothing to trace it by. It runs as its own CI job: it needs PHP,
  and unlike the unit suite it is timezone-independent.

### Changed

- The picker ships as a separate ~11 kB entry point rather than riding on the
  calendar bundle. That bundle is ~395 kB, which is not something to put on
  every page in an instance, so the new one reaches for neither Vue nor
  `@nextcloud/vue`.

## [0.4.2] - 2026-07-31

### Changed

- **Supported Nextcloud versions widened to 30–34, and PHP to 8.1–8.5.**
  Nextcloud 34 ships PHP 8.5, and the declared range gates installation — an
  app that runs perfectly is still refused outright when the interpreter falls
  outside it, so the old 8.4 ceiling would have failed every install on 34.
  The gate only fires on install or enable, which is why an already-running
  instance never reveals it. Verified against 30.0.17, 31.0.14, 32.0.13,
  33.0.7 and 34.0.2.

### Fixed

- **Every month row silently dropped a day, and Saturday never appeared.** The
  grid declared a leading week-number track that collapsed to `0px` when the
  numbers were hidden, but the cells that fill it are behind a `v-if` — so grid
  auto-placement fed the track the first weekday header and one day per row,
  rendering them into a zero-width column. The remaining days were left shifted
  one column out of alignment with their weekday headers. The track is now
  added and removed rather than collapsed. Under `dir="rtl"` the swallowed
  track is the rightmost, which is why only a sliver of «شنبه» was visible.
- The week view's scrollbar overlaid the grid instead of reserving space,
  appearing as a stray bar floating beside the non-working hours.

## [0.4.1] - 2026-07-31

### Fixed

- **The Gregorian date range under the Persian title was misordered** in the
  day and week views: `25 July 2026 – 31 July 2026` rendered as
  `July 2026 – 31 July 2026 25`. Latin text inside the RTL toolbar has no bidi
  isolate, so a leading day number is reordered to the far end. Only those two
  views put a number first, which is why the month view was unaffected.
- Nextcloud floats its app-navigation toggle over the start of the app content,
  where it covered the first view button and clipped «List» to «st».

## [0.4.0] - 2026-07-30

### Added

- **Personal settings** (Settings → Personal → Jalali Calendar), mirroring the
  options the official Calendar app offers, minus everything that only means
  something once you can create events:
  - Show tasks in calendar
  - Limit the number of events displayed in the monthly view
  - Show weekends — hiding them drops the Friday column to a six-day grid
  - Show week numbers — the Jalali week of the year, per row
  - Time increments (15 / 30 / 60 minutes), ruling the day and week grids
  - Copy the primary and iOS/macOS CalDAV addresses
  - A link to Nextcloud's own availability settings
- `jalaliWeekNumber()`, counting the week containing Farvardin 1 as week one.

### Notes

Deliberately not carried over from the Calendar app's settings panel, because
this app is read-only: the simplified editor, default reminder and default
attachments location have nothing to configure without event creation, and
"Enable birthday calendar" is a `dav` setting owned by the Calendar app rather
than this one. A timezone override is not included either — rendering in a
zone other than the browser's needs the date handling reworked across every
view, so it is left for its own release rather than half-done.


## [0.3.0] - 2026-07-30

### Added

- **Five views**: Day, Week, Month, Year and List, switchable from the toolbar
  and remembered per browser. Navigation steps by whatever the view shows — a
  day, a week, a month or a year — and each fetches only the window it needs.
  - **Day / Week**: an hour grid with events positioned by clock time.
    Overlapping events share the column width, and a line marks the current
    time. All-day and multi-day events sit in a bar above the grid.
  - **Year**: twelve mini months, with a dot on days that have events. Click a
    month name to open it, or a day to drill into it.
  - **List**: an agenda of the month, showing only days with something on them.
- **Working hours** (Settings → Administration → Jalali Calendar): a start and
  end time plus which weekdays count as working days, defaulting to
  09:00-17:00, Saturday to Wednesday. Hours outside them are shaded in the day
  and week views, which also open scrolled to the start of the working day.

### Fixed

- Navigating refetched events twice, because the visible window's start and end
  were watched separately. Now one derived key, one fetch.


## [0.2.5] - 2026-07-30

### Changed

- The grid header now shows **full weekday names** (شنبه، یکشنبه، …) instead of
  single letters. Below 640px, where «چهارشنبه» no longer fits, it falls back to
  the letter — the full name stays in the accessibility tree either way.


## [0.2.4] - 2026-07-30

### Fixed

- **Deleting an off-day returned HTTP 500.** `OffDayService::delete()` called
  `OffDayMapper::find()`, which does not exist: `QBMapper` — unlike the
  deprecated `Mapper` it replaced — provides no find-by-id. Added one. Deleting
  a row that is already gone now returns 404 instead of a fatal error.


## [0.2.3] - 2026-07-30

### Fixed

- **Religious holidays landed a day early.** The bundled `shamsi-holidays`
  dataset computes lunar dates on Umm al-Qura reckoning, which runs a day
  behind Iran's official reckoning — Arbaeen 1405 came out as 12 Mordad
  instead of 13. Confirmed against `Intl` (`islamic-umalqura` → 2026-08-03,
  `islamic-tbla` → 2026-08-04); solar and weekly dates were never affected.
- Importing the **current** Jalali year now reads
  `https://www.time.ir/event-year` live. That page is server-rendered, covers a
  whole year, and carries each occasion's real name — so dates and titles match
  time.ir exactly, and generic «تعطیل رسمی» labels are gone. Other years still
  come from the bundled dataset.
- Two occasions falling on the same day are **merged** rather than one
  overwriting the other (1 Farvardin 1405 is both Nowruz and Eid al-Fitr).
- The month name «اَمرداد» that time.ir uses was not recognised, which silently
  dropped every Mordad holiday.


## [0.2.1] - 2026-07-30

### Changed

- **Official Iranian holidays now ship with the app** as
  `data/ir-holidays.json`, generated offline from the `shamsi-holidays` npm
  package (time.ir's official dates) by `npm run generate:holidays`. Covers
  Jalali years 1400-1406, 524 days.
- The import therefore needs **no API key and no network access**. The
  time.ir API client and the `timeIrApiKey` setting are gone.
- The upstream list marks every Friday as a holiday — 52 of a year's 75
  entries. Those are skipped on import: the grid already draws Friday as the
  weekend, and a generic label on every Friday cell buries the occasions that
  matter. A *named* holiday falling on a Friday is still imported.


## [0.2.0] - 2026-07-30

### Added

- **Administration page** (Settings → Administration → Jalali Calendar).
- **Week start** is now configurable instance-wide: Saturday (شنبه) or
  Sunday (یک‌شنبه). The grid, its column headers and the weekend column all
  follow the setting.
- **Off-days**: official holidays are stored server-side and shown to every
  user, with the occasion's name on the day and the date in the weekend colour.
- Admins can **add and remove off-days by hand**.
- **Import** off-days for a Jalali year, from either time.ir (needs an API key,
  see below) or any iCalendar (.ics) feed. Re-importing replaces only what the
  same source imported before, so manual entries always survive.
- A PHP Jalali converter, verified to agree with `jalaali-js` byte-for-byte
  across ~55,000 Jalali and ~50,000 Gregorian dates.
- Parity with the official Calendar app's calendar list: webcal
  **subscriptions**, the birthday calendar and **app-generated calendars such
  as Deck boards** now appear alongside personal calendars.
- **Tasks (`VTODO`) are rendered**, on their due date, exactly as the Calendar
  app does it — a task with no due date is not shown, and completed tasks
  (`STATUS:COMPLETED` or `PERCENT-COMPLETE:100`) are struck through.
- Webcal caching header (`X-NC-CalDAV-Webcal-Caching`), so subscriptions are
  not refetched from their remote source on every request.

### Changed

- Lowered the minimum Nextcloud version from 31 to **30**, after verifying the
  app installs, enables and serves correctly on 30.0.17.

### Fixed

- Subscriptions were missing entirely: `findAllCalendars()` filters them out,
  so `findAllCalDAVCollectionsGrouped()` is used instead.
- Deck boards were invisible. Deck advertises
  `supported-calendar-component-set = VTODO` only, so the previous
  VEVENT-only filter dropped every board, and a VEVENT query would have
  returned nothing regardless.
- Each collection is now queried only for the component types it advertises,
  instead of assuming `VEVENT`.
- The admin settings bundle shipped without its styles, because a single
  entry point received all injected CSS. Fixed with per-entry CSS injection.

### Notes

- time.ir publishes no free feed. Their website ignores year/month parameters
  server-side and renders only the current month, and `api.time.ir` requires a
  key, so the importer asks the administrator to supply one. The iCalendar
  importer needs no key and is the simpler route.

## [0.1.0] - 2026-07-30

First release — read-only Jalali month view.

### Added

- Jalali (Shamsi) month grid: six weeks, Saturday-first, Persian numerals,
  correct Shamsi month and weekday names, RTL layout.
- Reads the user's existing CalDAV calendars through
  `@nextcloud/cdav-library`, against the same `/remote.php/dav` endpoint the
  official Calendar app uses. Nothing is stored by this app.
- Per-calendar colours plus show/hide toggles, remembered in the browser.
  Calendars disabled in the Calendar app start hidden here too.
- Recurring events expanded within the visible window, honouring `EXDATE`,
  modified occurrences and detached occurrences whose master lives elsewhere.
- Day panel listing a day's events with time, location, calendar and
  description; multi-day events describe themselves relative to the day shown.
- Month navigation, a "today" button that also survives midnight, and
  `/apps/jalali_calendar/{jy}/{jm}` deep links.
- Farsi translation.
- Partial-failure handling: one unreachable or malformed calendar no longer
  blanks the whole month, it is reported instead.

### Known limitations

- Event times render in the browser's timezone, not the calendar's configured
  timezone. The app shows a notice when the two differ.
- Read-only; create/edit/delete happen in the official Calendar app.
- Month view only — no week or day view yet.
- No Iranian holidays overlay yet.

[Unreleased]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.6.0
[0.5.0]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.5.0
[0.4.2]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.4.2
[0.4.1]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.4.1
[0.4.0]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.4.0
[0.2.4]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.2.4
[0.2.3]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.2.3
[0.2.1]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.2.1
[0.2.0]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.2.0
[0.1.0]: https://github.com/nsrfth/Jalali-Calendar-By-Naser-Fathi/releases/tag/v0.1.0
