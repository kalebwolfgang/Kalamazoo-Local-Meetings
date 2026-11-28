# Kalamazoo Local Meetings

A public archive of Kalamazoo County local government meetings, starting with the Kalamazoo City Commission: transcripts with YouTube timestamps, agendas, minutes, and full agenda packets, stored as plain text and spreadsheet data so they can be searched and compared over time.

Everything here comes from public records. Records are copied, not reworded. The exceptions are labeled: topic tags are assigned by AI, and short notes written by AI while processing (in `info.txt` and the notes columns of the spreadsheets) explain choices, gaps and problems. A file that summarizes says so in its name (for example `digest`).

## How the repo is organized

```
kalamazoo-city/                     <- one folder per government
  city-commission/                  <- one folder per board
    2026/                           <- one folder per year
      2026-01-05-business/          <- one folder per meeting (date first, then type)
        info.txt                    <- date, type, links to video and original documents
        transcript.txt              <- cleaned YouTube transcript with [h:mm:ss] timestamps
        agenda.txt                  <- full text of the agenda
        minutes.txt                 <- full text of the minutes (info.txt says if they are approved, a draft, or a copy from a later packet)
        public-comment.csv          <- one row per public comment speaker
        public-comment-topics.csv   <- one row per topic each speaker mentioned, with time and quote
        agenda-items.csv            <- one row per agenda item: outcome, vote, video times, pages
        packet/
          index.csv                 <- every agenda item, its attachments, and original page numbers
          corrections.txt           <- pages typed in or numbers fixed by hand where software could not read them
          G01-short-item-name--01-agenda-report.txt   <- each attachment as its own text file
          G01-short-item-name--02-resolution.txt
          H01-short-item-name--03-fee-schedule.csv    <- tables saved as spreadsheets
rosters/
  kalamazoo-city-commission.csv     <- official names, when each person served, and common transcript misspellings
topics.csv                          <- the shared topic list used to tag every government's meetings
audit.csv                           <- problems found in the official records, one row per problem
```

Future governments go next to `kalamazoo-city/`, for example `kalamazoo-county/`, `portage/`, `oshtemo-township/`.

## Naming rules

- Meeting folders: `YYYY-MM-DD-type`, where type is `business`, `committee-of-the-whole`, `special`, `work-session`, or `retreat`.
- If two meetings of the same type happen on one day, add `-2`.
- Packet files all sit in one `packet` folder. Each name starts with the agenda letter and number, like `G01` or `H02`, then a short item name, then `--` and the attachment. They sort in agenda order.
- All names are lowercase with dashes, no spaces.

## What each file contains

**transcript.txt**
Taken from YouTube's automatic captions. Cleaned for format only:
- The text is split into short blocks. Each block starts with a line like `--- 1:46:13 | https://www.youtube.com/watch?v=VIDEO_ID&t=6373s` that links to that moment in the video.
- Every sentence is marked with the time it starts, like `[1:46:15]`. Times are accurate to within a few seconds, because YouTube only marks when each caption line begins.
- Broken lines are joined into full sentences.
- Names are corrected only when a title comes before them (for example "Clerk Bowling" becomes "Clerk Borling"), using the roster file.
- Sounds like `[snorts]` are removed.
- Words are never reworded. Automatic captions contain errors, so always check the video before quoting.

**agenda.txt and minutes.txt**
Full text. Minutes are often scanned, so the text was read by software and checked by hand for names, numbers, and votes. The minutes are the official record. Some posted minutes are unsigned drafts, and some were found only inside a later meeting's packet; the top of `minutes.txt` and the meeting's `info.txt` say which. When no minutes have been posted, there is no `minutes.txt`.

**packet/**
The full agenda packet, split into one file per attachment, all in one folder. Nothing is left out; blank pages are marked as blank. Pages that were scanned images are marked `[scanned page, text read by software]` because they may contain small errors. Pages the software could not read at all (maps, drawings, some tables) were typed in by hand, are marked at the top, and are listed in `corrections.txt`. Tables are saved as `.csv`.

**public-comment.csv**
One row per speaker, in the order they spoke. The speaker's name, residency, affiliation, and what they spoke about are copied from the minutes, because the minutes are the official record. When no minutes have been posted, names and residency come from the video instead, `spoke_about` says "(no minutes posted)", and `time_note` says where each name comes from (the captions, or an earlier meeting's minutes). Names heard only in the captions may be misspelled. Speakers who gave no name are listed as "Unnamed speaker" with a short description. The video time comes from the transcript. `comment_period` says whether it was general public comment or comment on a specific agenda item.

**agenda-items.csv**
One row per agenda item: the outcome, the vote count, who voted no, who made and seconded the motion, the resolution number, the video time when the item was introduced and when the vote was taken, the minutes page, and the packet pages. When no minutes have been posted, the outcome, vote and movers come from the video, and the meeting's `info.txt` says so.

**Topics and categories**
`topics.csv` is the one shared list used for every government, so meetings can be compared. Each topic belongs to a broader category (for example, Policing is in Public Safety and Justice). A few topics belong to two categories, like Streets and Traffic Safety, which is in both Transportation and Public Safety and Justice.

Tagging rules:
- **Every topic that was mentioned gets counted.** There is no limit and no "main" topic. If a speaker talks about 15 things, all 15 count.
- A topic counts when the speaker says something about it. Greetings, welcomes, and describing themselves do not count.
- Public comment topics come from what was actually said in the transcript, not only from the short summary in the minutes, because the minutes often leave topics out.
- `categories` is filled in automatically from the topics, so a row can fall under many categories.
- When a topic is Other, a note says what it is. Other is reviewed regularly. If the same kind keeps showing up, it becomes a new topic.

**public-comment-topics.csv**
One row per topic per speaker. Every row has the time the topic was first mentioned, a video link to that moment, and the exact words from the transcript as proof. This is the file to count from.

Tags are a judgment call made by AI, so they are labeled that way. The notes columns (`other_notes`, `time_note`, `notes`) and the descriptions of unnamed speakers are also written by AI while processing. Everything else in these spreadsheets is copied from the minutes, the agenda, the packet, the transcript, or the video.

Counting rules:
- "How often did X come up at public comment" counts the speakers who mentioned X.
- "Most talked about" ranks topics by how many speakers mentioned them.
- Counts are of speakers or agenda items, not of every time a word was said.

**info.txt**
The meeting date, type, and links to the YouTube video and the original PDFs, plus notes about anything unusual: absences, agenda changes, where the video and the minutes disagree, and staff record issues.

**audit.csv**
This archive also works as an audit of the city's records. Each row is one problem found while processing a meeting, such as minutes that were never posted or a packet page that belongs to a different item. `status` is "confirmed" when the records prove it, or "possible" when it only looks wrong; the `issue` text says why. The `evidence` column says where it was checked, and `checked_on` gives the date. The same problems are listed at the top of the notes in each meeting's `info.txt`.

## Rosters

Each board has a roster file listing officials and staff who appear in its meetings, spelled the way the minutes spell them.
- `first_seen` and `last_seen` are the first and last meeting dates in this archive where the person appears in that role. Name fixes only apply to meetings inside those dates, so people from different years are never mixed up.
- When someone's role changes (for example, Commissioner to Mayor), they get a new row instead of the old row being changed.
- Every new meeting is checked against the roster. New people are added, and missing people are flagged.
- Public commenters are not in the roster. Their names come from each meeting's minutes, or from the video when no minutes have been posted.

## How to cite

Every fact should point to the most specific place it came from. Use these formats:

| Source | Cite it as | Example |
|---|---|---|
| Transcript | Meeting, then the time with a video link | Business Meeting, Jan 5, 2026, [4:06:21](https://www.youtube.com/watch?v=upL1eEYIMCE&t=14781s) |
| Minutes | Meeting, then the page | Minutes, Jan 5, 2026 Business Meeting, p. 8 |
| Agenda | Meeting, then the agenda item | Agenda item H2, Jan 5, 2026 Business Meeting |
| Agenda packet | Meeting, then the packet pages | Jan 5, 2026 packet, pp. 153-154 (staff report, item H2) |
| Packet table | The packet page from the `packet_page` column | Jan 5, 2026 packet, p. 83 (2026 Expenditure Summary by Activity) |

Rules:
- Never cite a whole packet or a whole meeting when a page or a time is available.
- Packet page numbers match the "Page X of Y" printed on the original PDF, so readers can open the PDF and jump straight there.
- Each packet text file marks every page with `--- packet page N ---`. Minutes and agendas mark pages the same way, using the original page numbers.
- To turn a transcript time into a link, convert it to seconds and add `&t=SECONDSs` to the video link (1:02:03 = 3723 seconds).
- If something comes from a page marked `[scanned page, text read by software]`, check the original page before quoting numbers.

## Original PDFs

Original PDFs are not stored on the main branch because they are too large. Copies downloaded for processing are kept on this repo's `raw-inputs` branch, but they are working copies, not an official backup. Each `info.txt` links to the official copy on the city's CivicClerk portal, which is the source for every document.

## Accuracy

The goal is under 1% chance of misinformation. Every fact should be traceable to a timestamp in the video or a page in an original document. Automatic captions, software-read scans, and AI-assigned tags and notes can contain errors, so check the original before relying on a detail. If you find an error, open an Issue with the file name and what is wrong.
