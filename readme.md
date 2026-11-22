# Kalamazoo Local Meetings

A public archive of Kalamazoo County local government meetings: transcripts with YouTube timestamps, agendas, minutes, and full agenda packets, stored as plain text and spreadsheet data so they can be searched and compared over time.

Everything here comes from public records. Nothing is summarized or reworded unless a file says so in its name (for example `digest`).

## How the repo is organized

```
kalamazoo-city/                     <- one folder per government
  city-commission/                  <- one folder per board
    2026/                           <- one folder per year
      2026-01-05-business/          <- one folder per meeting (date first, then type)
        info.txt                    <- date, type, links to video and original documents
        transcript.txt              <- cleaned YouTube transcript with [h:mm:ss] timestamps
        agenda.txt                  <- full text of the agenda
        minutes.txt                 <- full text of the approved minutes
        public-comment.csv          <- one row per public comment speaker
        public-comment-topics.csv   <- one row per topic each speaker mentioned, with time and quote
        agenda-items.csv            <- one row per agenda item: outcome, vote, video times, pages
        packet/
          index.csv                 <- every agenda item, its attachments, and original page numbers
          corrections.txt           <- any numbers fixed by hand after software misread them
          G01-short-item-name--01-agenda-report.txt   <- each attachment as its own text file
          G01-short-item-name--02-resolution.txt
          H01-short-item-name--03-fee-schedule.csv    <- tables saved as spreadsheets
rosters/
  kalamazoo-city-commission.csv     <- official names and their common transcript misspellings
topics.csv                          <- the shared topic list used to tag every government's meetings
```

Future governments go next to `kalamazoo-city/`, for example `kalamazoo-county/`, `portage/`, `oshtemo-township/`.

## Naming rules

- Meeting folders: `YYYY-MM-DD-type`, where type is `business`, `committee-of-the-whole`, `special`, `work-session`, or `retreat`.
- If two meetings of the same type happen on one day, add `-2`.
- Agenda item folders start with the agenda letter and number, like `G01` or `H02`, so they sort in agenda order.
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
Full text. Minutes are often scanned, so the text was read by software and checked by hand for names, numbers, and votes. The minutes are the official record.

**packet/**
The full agenda packet, split by agenda item. Nothing is left out except blank pages. Pages that were scanned images are marked `[scanned page, text read by software]` because they may contain small errors. Tables are saved as `.csv`.

**public-comment.csv**
One row per speaker, in the order they spoke. The speaker's name, residency, affiliation, and what they spoke about are copied from the minutes, because the minutes are the official record. The video time comes from the transcript. `comment_period` says whether it was general public comment or comment on a specific agenda item.

**agenda-items.csv**
One row per agenda item: the outcome, the vote count, who voted no, who made and seconded the motion, the resolution number, the video time when the item was introduced and when the vote was taken, the minutes page, and the packet pages.

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

Tags are a judgment call made by AI, so they are labeled that way. Everything else in these spreadsheets is copied from the minutes, the agenda, or the transcript.

Counting rules:
- "How often did X come up at public comment" counts the speakers who mentioned X.
- "Most talked about" ranks topics by how many speakers mentioned them.
- Counts are of speakers or agenda items, not of every time a word was said.

**info.txt**
The meeting date, type, and links to the YouTube video and the original PDFs.

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

Original PDFs are not stored here because they are too large for GitHub. Each `info.txt` links to the city's copy and to a backup copy.

## Accuracy

The goal is under 1% chance of misinformation. Every fact should be traceable to a timestamp in the video or a page in an original document. If you find an error, open an Issue with the file name and what is wrong.
