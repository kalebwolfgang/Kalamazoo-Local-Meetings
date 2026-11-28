# Notes for Claude: how to process meetings in this repo

Read this before doing any work here. Add to it whenever you learn something new (a trick, a trap, a decision Kaleb made), so the next chat does not have to relearn it. Keep it short and practical.

## The goal

A public archive of City of Kalamazoo City Commission meetings, going back to January 2020. Current batch: January to September 2026 (not October yet). `checklist.md` shows what is done and what is left.

## How Kaleb wants to work

- You do everything: find the materials, process them, and commit straight to `main`. He does not upload files by hand anymore.
- Work one meeting date at a time (the Committee of the Whole and the Business Meeting on the same day count as one date), and commit each date on its own. By default, check in after each date and wait for him to say go on. If he asks for a batch (on Nov 28, 2026 he asked for all of June to August at once), check your own work after each date, keep committing date by date, and send one short check-in at the end.
- He likes judgment calls that are labeled and explained: make the call, write it down in the notes, and tell him about it in the check-in.
- Honest wording first (Nov 28, 2026): say exactly what the record shows and where it came from. Use counts, not "most" or "many" (for example "7 of 14 speakers were tagged Homelessness"), and say that topic tags are AI-assigned when a note is based on them. Every name in a meeting without minutes says where it came from in `time_note` (the captions, or an earlier meeting's minutes). Do not state a guess as a fact; label it as possible or leave it out.
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
- `meeting-list.csv` already has the IDs for January to September 2026. It does not have the CivicClerk event numbers that info.txt links need. Take those from `requests.csv` on the `raw-inputs` branch. Never guess them.

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

## Audit: mark every staff record issue

Kaleb treats this collection as an audit of the city's records (decided Nov 28, 2026). Staff sometimes forget or miss things, so mark every one you find.
- Only call something wrong if you can prove it from the records (for example two packet pages are the same image, a date that does not exist, a section number the City Attorney corrected on video). Start that line with `Staff record issue:`.
- If it only looks wrong (an address that does not seem to match, a caption that disagrees with the minutes, a publish date that may be a re-upload), start the line with `Possible staff record issue:` and say why it is only possible.
- Put each one at the top of the Notes in `info.txt`, add it to the `notes` column of the agenda item it belongs to, and add a row to `audit.csv` (repo root: meeting_date, meeting, folder, item, status confirmed/possible, category, issue, evidence, checked_on). In `meeting-list.csv` notes, say "See info.txt and audit.csv for staff record issues."
- State what the record shows, with dates and where you checked. Do not guess why it happened. Recheck anything that could have changed (posting status, publish dates) and update `checked_on`.

Things to look for:
- Minutes not posted on CivicClerk, or posted only as an unsigned DRAFT after the Commission approved them.
- Minutes never put on a later agenda for approval. Check each later Business Meeting agenda for "Approval of the minutes". Agenda text can be read in Chrome with `GetMeetingFileStream(fileId=ID,plainText=true)`.
- Packets posted on the day of the meeting or after it (use `publishOn` from the CivicClerk Events API; it may show a later replacement date, so say so).
- Packet mistakes: an address or subject that does not match the item, the same drawing used for two items, a wrong section reference, blank pages.
- Slides or documents the minutes say were "filed with the papers" but that are not in the packet or on CivicClerk.
- Minutes mistakes: a mover or seconder that differs from the video, a missing vote or document number, typos in document numbers.

## Rules and judgment calls already decided

- Minutes are the official record. When the video and the minutes disagree, follow the minutes and add a note. Do not guess who said something when the captions are unclear.
- Minutes are often inside a later meeting's packet ("Approval of the minutes from the City Commission meetings on ..."), even when CivicClerk never posted them. Search later packets before saying minutes do not exist. If you use a packet copy, say so in the minutes.txt header and info.txt, link the packet it came from, and mark it as a staff record issue. The approval date is the date of that later consent vote (per its minutes, or "on video" if those minutes are not posted).
- When there are no minutes: votes, movers, attendance and speaker names come from the video, and the notes say so. Residency is "City resident" only when the speaker says they live in the city or names a city neighborhood they live in; "a resident of Kalamazoo" is "not stated". For a speaker who appears in earlier 2026 minutes, use the minutes' spelling of the name, and their residency when they do not state it on video (say so in `time_note`). If they state a different residency on video, follow the video and note the difference.
- Names heard only in the captions: mark them in `time_note` as not confirmed. A speaker who gives no name is "Unnamed speaker (short description)". Do not guess gender.
- An item added during the meeting with no printed number is listed as "Added".
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
- Typed-in tables that the software could not read (for example a page printed sideways) start with `[scanned page printed sideways: ...]`; check that the totals add up and say so.
- Typed-in map or drawing pages start with `[map or picture page: the software text was not usable, so the readable labels were typed in by hand from the page image. ...]`. Fully blank-text slides use `[picture page: ...]`.
- CSV files use Windows line endings (CRLF), like the rest of the repo. `finish_tables.py` and `fix_agenda_row.py` already write them that way.

## Helper tools added Nov 28, 2026

- `tools/sheet.py PDF OUTPREFIX pages...` makes contact sheets (8 page images each) so you can look at many packet pages at once.
- `tools/typein.py PACKET_DIR PAGE TEXTFILE` replaces one packet page's text in whichever .txt file holds it. Log every use in `corrections.txt`.
- `tools/checkq.py MEETING_OUT_DIR` lists topic quotes that `finish_tables.py` will not find, so you can fix them first.
- `tools/minfmt.py minutes.pdf` drafts minutes.txt from a minutes PDF that has a text layer (margin headings in brackets). Still check it against the page images.
- `tools/rebookmark.py IN OUT` fixes packets whose bookmarks are flat ("Item: G1: Title" with no section or Agenda Report bookmarks; the June 1, 2026 packet). Split the fixed working copy, never change the original, and note it in corrections.txt.

## Other traps

- Speakers often hide inside another speaker's caption turn (the Mayor's "go ahead" and the new speaker's "my name is" on one line, or a new voice with no name). Read every speaker's full text with `speaker_text.py` and watch for a change of voice, a new name, or "next, please".
- `split_packet.py` can take more than 2 minutes on a big packet. Run it in the background with `nohup` and check its log.
- A browser_batch cannot go from YouTube to GitHub in one batch. Use one batch per site.
- To push from this workspace, the repo must be added with push access first.

- The repo moved to `kalebwolfgang/Kalamazoo-Local-Meetings` (capital letters). Use that URL.
- Commit as "Claude" and end the message with the session attribution lines.
- YouTube's new transcripts split into shorter lines, so expect about twice as many blocks as in January.
- If a tool call is blocked as unsafe, do not look for a way around it. Stop and ask Kaleb.

## Backlog work (2025 and earlier), added Nov 28, 2026

- Kaleb moved to the backlog on Nov 28, 2026, starting with October to December 2025, working back from December. 2025 folders go in `kalamazoo-city/city-commission/2025/`.
- CivicClerk goes back to July 2015 (City Commission). The city YouTube channel goes back to November 2015. Filter the Events API with `categoryName eq 'City Commission'` to catch special meetings whose names do not start with "City Commission".
- New meeting types (folder suffix, label in the tools): `special-committee-of-the-whole`, `special-business`, `oath-of-office` (Business Meeting and Oath of Office Ceremony), `budget-work-session`.
- `update_roster.py` now also moves `first_seen` back for older meetings. Patsy Moore was Interim City Manager in late 2025 (Hankins started 2026-01-05).
- Before a ctrl+v paste into GitHub, check the copy worked: on Nov 28 one paste held a different meeting left on the clipboard. After pasting, compare the file's first and last lines and line count with what the JavaScript reported.
- Many 2025 minutes were approved at early 2026 meetings; find the approval date in the 2026 `agenda-items.csv` files ("Approval of the minutes").
- Minutes PDFs from late 2025 have a text layer. `tools/min2txt.py minutes.pdf` drafts minutes.txt with paragraphs joined and margin headings in [brackets]. Check it against the page images: it sometimes joins two speakers or a "Commissioner Questions:" line into the paragraph before.
- Map pages: typing the title, legend and main place names is enough; say in the page note that small labels and sources are not typed in.
- Big packets: the raw-inputs download job now splits any PDF over 95 MB into parts with qpdf (`packet-part1-pages-1-268.pdf` and so on). Join the parts before splitting by bookmarks, and say in info.txt that the packet came in parts.
- A meeting can run over two days with two videos (Oct 15, 2025 continued Oct 17). Keep it as one folder, list both videos in info.txt, and note the second video in meeting-list.csv.
- Some 2025 minutes reuse page numbers from other meetings (Oct 6 and Oct 20, 2025). Log it as a possible staff record issue for each meeting.
- If a proclamation bookmark points at agenda page 1, `split_packet.py` treats the agenda pages as its attachment. Delete that file and make the first index.csv row the usual "Agenda (pages 1-N)" row.
- Appraisals and similar scanned reports: the software misses photo captions and loses table columns. Type in the captions and maps, and type tables as rows with `|` between columns (blank cells as -).

## Open items

- Sep 8, 2026 Business Meeting packet is over 100 MB. The download job now saves it in two parts on raw-inputs (pages 1-268 and 269-536); it still needs processing.
- Oct 20, 2025 Business: the appraisal attached to H2 (packet pages 297-366) is the same as the Oct 6 G20 appraisal, but its photo captions, maps and zoning table were not typed in. The Oct 6 typed pages could be copied over (page numbers are 232 higher).
- May 18, 2026: both sets of minutes were posted only as unsigned DRAFTs. Replace minutes.txt and the approval date when the approved version is posted. (The CoW had no packet because the whole meeting was a closed session.)
- Minutes stamped DRAFT: process them and say so in the minutes.txt header, info.txt and meeting-list.csv notes. If a later meeting approved them, the approval date is that meeting's date and the posted DRAFT is a staff record issue; otherwise write "not yet (the posted minutes are a DRAFT)".
- Minutes not posted yet (checked 2026-11-28): Jul 6, Aug 10 (both), Aug 17 (both), Sep 8 (both), Sep 21 Business. None of these has been on a Business Meeting agenda for approval through Nov 16, 2026.
- Jun 15 CoW minutes: never posted; the text comes from the July 6, 2026 packet (G19). Those pages are saved on `raw-inputs` as `inputs/2026-06-15-committee-of-the-whole/minutes-from-2026-07-06-packet.pdf`.
- Posted only as unsigned DRAFTs even though approved: May 18 (both, approved Jun 1), Jun 1 and Jun 15 Business (approved Jul 6), Jul 20 (both, approved Aug 10).
- January to August 2026 were all audited on Nov 28, 2026. September 2026 on still needs it as each meeting is processed.
- Mar 14, 2026 Planning Retreat: no minutes were ever posted. Video is on the Public Media Network channel. Names in it come from the video.
- Before 2026: no meeting list yet. Check how far back CivicClerk goes and where older records live.
