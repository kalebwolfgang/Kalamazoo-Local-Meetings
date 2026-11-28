# Tools

The scripts used to turn a meeting's raw materials into the files in this repo. They are kept here so every meeting is processed the same way, even if the work is picked up later or by someone else.

They need Python 3 with `pypdf` and `pdfplumber`, plus the `pdftotext`, `pdftoppm` (Poppler) and `tesseract` programs.

## What goes in

For each meeting:
- The YouTube video link
- The transcript, copied from YouTube's "Show transcript" panel
- The agenda, agenda packet, and minutes PDFs

## Steps for one meeting

**1. Transcript**
`clean_transcript.py` cleans the copied transcript: removes the doubled timestamps, joins lines into sentences, timestamps every sentence, starts each block with a video link, and fixes names from the roster (only when a title comes first and the meeting date is inside that person's roster dates). It never rewords anything. Its report lists every name fix so they can be checked.

**2. Agenda**
Text taken straight from the agenda PDF, with page markers.

**3. Minutes**
Minutes are usually scanned, so the text is read with `tesseract` at 300 dpi, then checked by hand against the page images for every name, number, and vote. Margin headings go in [brackets]. Page markers match the original.

**4. Agenda packet**
`split_packet.py` splits the packet into one text file per attachment using the PDF's own bookmarks, marks every page, reads scanned pages with software, and saves budget and fee tables as CSV. Budget tables are read twice and their totals are checked, and anything that disagrees goes into `needs-review.txt`.

Each line in `needs-review.txt` is checked against the page image. Confirmed errors are listed in a fixes file and applied with `apply_corrections.py`, which also writes `corrections.txt`. Fee table CSVs that do not line up cleanly are fixed by hand or removed. `needs-review.txt` is deleted before uploading.

**5. Roster check**
Names in the minutes' roll call and staff list are compared with the roster. New people are added, `last_seen` is moved forward, and new misspellings found in the transcript are added.

**6. Spreadsheets**
- `agenda-items.csv` is written from the minutes (outcomes, votes, movers) and the transcript (times). When no minutes have been posted, outcomes, votes and movers come from the video, and the notes say so.
- `public-comment.csv` is written from the minutes (names, residency, what they spoke about) and the transcript (start times). When no minutes have been posted, names and residency come from the video, and `time_note` says where each name comes from.
- `speaker_text.py` prints each speaker's full comment, so every topic they mention can be tagged in `public-comment-topics.csv` with an exact quote.
- `finish_tables.py` then checks everything: every topic is in `topics.csv`, every quote appears word for word in the transcript, and all times, links, and categories are filled in. It stops with an error if anything fails.

**7. info.txt and upload**
`info.txt` lists the meeting details, links, and files. The meeting files go in the meeting folder, and the packet files go in its `packet` folder.

## Judgment calls

These steps involve judgment and are labeled as AI-assigned where they appear:
- Topic tags. A topic counts when a speaker says something about it. Greetings and welcomes do not count.
- Speaker start times, when a caption line holds the end of one speaker and the start of the next.

## Helper scripts (added November 2026)

Smaller scripts that make each step faster. `CLAUDE.md` in the repo root explains the full order of work.
- `prep_meeting.py`: makes agenda.txt, cleans the transcript, and reads the minutes with tesseract
- `update_roster.py`: moves `last_seen` forward for people at a meeting and adds new people
- `agenda_titles.py` and `make_slugs.py`: full agenda item titles and the item list for `split_packet.py`
- `fix_agenda_row.py`: fixes the packet index when bookmarks put the agenda pages under an opening item
- `write_public_comment.py`, `write_topics.py`, `write_agenda_items.py`: write the three spreadsheets from simple lists
- `write_info.py`: writes info.txt
- `build_checklist.py`: rebuilds checklist.md from meeting-list.csv

## Helper scripts

- `sheet.py PDF OUTPREFIX pages...`: contact sheets of page images, 8 per sheet, for checking many packet pages at once.
- `typein.py PACKET_DIR PAGE TEXTFILE`: replaces one packet page's text with text typed in by hand.
- `checkq.py MEETING_DIR`: lists topic quotes that are not found in the transcript.
- `minfmt.py minutes.pdf`: drafts minutes text from a minutes PDF that has a text layer.
- `rebookmark.py IN OUT`: rewrites flat "Item: G1: Title" packet bookmarks into the usual layout so `split_packet.py` can split the packet.
