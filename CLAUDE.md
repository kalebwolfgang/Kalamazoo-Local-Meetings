# Notes for Claude: how to process meetings in this repo

Read this before doing any work here. Add to it whenever you learn something new (a trick, a trap, a decision Kaleb made), so the next chat does not have to relearn it. Keep it short and practical.

## The goal

A public archive of City of Kalamazoo City Commission meetings, going back to January 2020. Current batch: January to September 2026 (not October yet). `checklist.md` shows what is done and what is left.

## How Kaleb wants to work

- You do everything: find the materials, process them, and commit straight to `main`. He does not upload files by hand anymore.
- Work one meeting date at a time (the Committee of the Whole and the Business Meeting on the same day count as one date). After each date is on GitHub, check in with a short message and wait for him to say go on.
- Replies: short, plain language, no technical jargon unless he asks. Never use em dashes, in replies or in any file.
- Ask before changing anything he did not ask for (README rules, folder layout, tagging rules). Small fixes found along the way: mention them and ask.
- If a meeting has no minutes posted yet, process it anyway and say so in `info.txt`, `meeting-list.csv` and the checklist.

## Where things come from

Your workspace cannot reach CivicClerk or YouTube directly. Two side routes are set up:

**1. PDFs (agenda, packet, minutes): the `raw-inputs` branch.**
- That branch has a GitHub Actions job (`.github/workflows/fetch.yml`) that runs when `requests.csv` on that branch changes. It downloads each file from CivicClerk into `inputs/DATE-TYPE/` (agenda.pdf, packet.pdf, minutes.pdf) and commits them to the branch.
- `requests.csv` columns: `date,type,event,agenda,packet,minutes,video` (CivicClerk file IDs). To fetch more, add rows, commit, push the branch, wait about 2 minutes, then `git fetch origin raw-inputs`.
- Files over 95 MB are skipped and noted in `log.txt` (GitHub's limit is 100 MB). Known case: the Sep 8, 2026 Business Meeting packet (102 MB). Split it with `qpdf` or `pypdf` in the job, or fetch it in two halves.
- Never put PDFs on `main`. The README says originals are linked, not stored.
- Do not try to get YouTube captions from GitHub Actions or work around YouTube's bot check. It was blocked as unauthorized access. Captions come from Chrome only.

**2. Transcripts: Kaleb's Chrome (Claude in Chrome), pasted into the `raw-inputs` branch.**
Do not pull a whole transcript into the chat. It is far too big. Copy it in the browser and paste it into a GitHub file instead:
1. Open `https://www.youtube.com/watch?v=VIDEO_ID`.
2. With JavaScript: pause the video, click `#expand`, click the "Show transcript" button, wait for `transcript-segment-view-model` elements, and build the text as one line per segment: `innerText.split('\n')` gives `[time, spoken time, text]`, so each line is `p[0] + p[1] + p.slice(2).join(' ')`. That matches the format `clean_transcript.py` expects.
3. Put the text in a temporary `<textarea>`, focus it, select it, then press `ctrl+c` with the keyboard action. (`navigator.clipboard.writeText` hangs. Do not use it.)
4. Go to `https://github.com/kalebwolfgang/Kalamazoo-Local-Meetings/new/raw-inputs?filename=inputs/DATE-TYPE/transcript-paste.txt`, click in the editor, press `ctrl+v`, then commit. This JavaScript clicks both buttons (wait about 2 seconds after loading and after pasting first): find the button whose text starts with "Commit changes", click it, wait about 1 second, then click the `[role=dialog]` button whose text is exactly "Commit changes".
5. Check the file size on the branch afterwards.

**Finding the IDs**
- CivicClerk event list: open `https://kalamazoomi.portal.civicclerk.com/` in Chrome and fetch `https://kalamazoomi.api.civicclerk.com/v1/Events?$filter=startDateTime ge ... and startswith(eventName,'City Commission')&$orderby=startDateTime` with JavaScript. Follow `@odata.nextLink`. Each event's `publishedFiles` has the Agenda, Agenda Packet and Minutes file IDs.
- PDF link: `https://kalamazoomi.api.civicclerk.com/v1/Meetings/GetMeetingFileStream(fileId=ID,plainText=false)`. Portal link for info.txt: `https://kalamazoomi.portal.civicclerk.com/event/EVENT/files/agenda/FILE`.
- Videos: the city channel is `https://www.youtube.com/@KalamazooCityTV/streams`. Scroll with JavaScript, then read `aria-label` on `a[href*="watch?v="]` links. Titles look like "February 16, 2026 Committee of the Whole" or "Regular Business Meeting". Some Business Meetings are titled "Kalamazoo City Commission". Special meetings may only be on the Public Media Network channel (the Mar 14, 2026 retreat was).
- `meeting-list.csv` already has the IDs for January to September 2026.

## Steps for one meeting date

Work in a scratch folder (for example `/home/claude/w/DATE/TYPE/`) with `raw/` (copied from the branch) and `out/` (what gets committed).

1. **Minutes first.** `tools/prep_meeting.py` runs OCR on the minutes at 300 dpi. Read `minutes-ocr.txt`, then crop the page images and check every name, dollar amount, vote and the handwritten approval date. Write `minutes.txt` by hand in the same format as earlier meetings (`--- page N ---` with the printed page number, margin headings in [brackets]).
2. **Roster, before the transcript.** `tools/update_roster.py DATE "names present" '[new staff as JSON]'`. Name fixes only apply to meetings between `first_seen` and `last_seen`, so if you clean the transcript before moving `last_seen` forward, no names get fixed.
3. **Prep.** `tools/prep_meeting.py DIR DATE TYPE VIDEO` makes `agenda.txt` and cleans the transcript. Read the name-fix report for bad fixes.
4. **Packet.** `tools/agenda_titles.py` lists full item titles. `tools/make_slugs.py agenda.txt "G1=short-name,..." > slugs.csv`, then `tools/split_packet.py`. Then run `tools/fix_agenda_row.py out/packet`, because proclamation bookmarks point at page 1 and the splitter wrongly files the agenda pages under B4. Look at every scanned or picture page listed in `index.csv`, and also every page with fewer than about 60 words (`pdftotext -f N -l N`): survey drawings and maps often have a text layer with only a few labels. Type in maps, signature pages and picture pages by hand, and log each one in `packet/corrections.txt`. Delete `needs-review.txt`.
5. **Spreadsheets.** Find times by searching the transcript. Then:
   - `tools/write_public_comment.py` (pipe-separated rows on stdin). Names, residency and topics come from the minutes. The order follows the video. Add a `time_note` when a speaker starts partway through someone else's caption line, or when a speaker never says their name on video.
   - `tools/speaker_text.py` to read each comment in full, then `tools/write_topics.py` with exact short quotes.
   - `tools/write_agenda_items.py` takes exactly 16 fields per row and stops if a row has more or fewer. Build the rows with a short Python `row()` helper instead of typing pipes. (Title `*` takes the full agenda title, `*G11` borrows another item's title for an item moved to the regular agenda.)
   - `tools/finish_tables.py` must print `ok`. It checks every quote against the transcript.
6. **info.txt.** `tools/write_info.py` with a notes file. Notes cover absences, items moved or withdrawn, abstentions, and anything where the video and the minutes differ (the minutes win).
7. **Commit.** Copy `out/` into the meeting folder, add the date to `meeting-list.csv` if it is missing, run `tools/build_checklist.py`, commit, push, and check GitHub.

## Rules and judgment calls already decided

- Minutes are the official record. When the video and the minutes disagree, follow the minutes and add a note. Do not guess who said something when the captions are unclear.
- `vote_at` is the time of the first "yes" in the roll call. `introduced_at` is when the item is read or announced.
- Consent items share one vote. If someone abstained on some items, the vote is "5-0, 1 abstaining" with a note.
- Tagging: count every topic a speaker says something about. Greetings, thanks, congratulations and describing themselves do not count. If the captions are too garbled to tell the topic, leave it out. Other always needs a note.
- Keep names exactly as the minutes spell them, even when another meeting spells the same person differently. Mention it in the notes.
- The CoW packet is usually the agenda plus page footers. When it is, say "same as the agenda" in info.txt and do not make a packet folder.
- Residency labels: use only "City resident", "Non-resident" or "not stated". Never leave it blank, and never use lowercase "non-resident". If the minutes give something else (for example "unhoused"), copy it as written.
- A speaker with nothing to tag (only greetings or thanks, or unclear captions) gets no topic rows, a note in `other_notes` saying why, and a line in info.txt. `finish_tables.py` keeps that note and adds a default one if it is missing.
- Minutes often group general public comment speakers by topic. The table still follows the video order. If the minutes list one person twice but they spoke once, use one row and explain it in `time_note`.
- A meeting with no public comment still gets `public-comment.csv` and `public-comment-topics.csv`, with headers only.
- Actions taken after a closed session (for example a labor contract) get their own row, named like `N1a`, with a note.
- Typed-in map or drawing pages start with `[map or picture page: the software text was not usable, so the readable labels were typed in by hand from the page image. ...]`. Fully blank-text slides use `[picture page: ...]`.
- CSV files use Windows line endings (CRLF), like the rest of the repo. `finish_tables.py` and `fix_agenda_row.py` already write them that way.

## Other traps

- The repo moved to `kalebwolfgang/Kalamazoo-Local-Meetings` (capital letters). Use that URL.
- Commit as "Claude" and end the message with the session attribution lines.
- YouTube's new transcripts split into shorter lines, so expect about twice as many blocks as in January.
- If a tool call is blocked as unsafe, do not look for a way around it. Stop and ask Kaleb.

## Open items

- Sep 8, 2026 Business Meeting packet is over 100 MB.
- Minutes not posted yet (as of 2026-11-27): Jun 15 CoW, Jul 6, Aug 10 (both), Aug 17 (both), Sep 8 (both), Sep 21 Business.
- Mar 14, 2026 Planning Retreat: no minutes were ever posted. Video is on the Public Media Network channel. Names in it come from the video.
- Before 2026: no meeting list yet. Check how far back CivicClerk goes and where older records live.
