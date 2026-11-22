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
        packet/
          index.csv                 <- every agenda item, its attachments, and original page numbers
          G01-short-item-name/      <- one folder per agenda item
            01-agenda-report.txt    <- each attachment as its own text file
            02-resolution.txt
            03-fee-schedule.csv     <- tables saved as spreadsheets
rosters/
  kalamazoo-city-commission.csv     <- official names and their common transcript misspellings
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
- Timestamps are written as `[h:mm:ss]` and link to that moment in the video.
- Broken lines are joined into full sentences.
- Names are corrected only when a title comes before them (for example "Clerk Bowling" becomes "Clerk Borling"), using the roster file.
- Sounds like `[snorts]` are removed.
- Words are never reworded. Automatic captions contain errors, so always check the video before quoting.

**agenda.txt and minutes.txt**
Full text. Minutes are often scanned, so the text was read by software and checked by hand for names, numbers, and votes. The minutes are the official record.

**packet/**
The full agenda packet, split by agenda item. Nothing is left out except blank pages. Pages that were scanned images are marked `[scanned page, text read by software]` because they may contain small errors. Tables are saved as `.csv`.

**info.txt**
The meeting date, type, and links to the YouTube video and the original PDFs.

## Original PDFs

Original PDFs are not stored here because they are too large for GitHub. Each `info.txt` links to the city's copy and to a backup copy.

## Accuracy

The goal is under 1% chance of misinformation. Every fact should be traceable to a timestamp in the video or a page in an original document. If you find an error, open an Issue with the file name and what is wrong.
