---
title: My Agent Had Four Chances to Look. It Took One.
published: false
tags: ai, agents, buildinpublic, hackathon
cover_image:
canonical_url:
series:
---

I am sitting at a hackathon table with a terminal open, running `python reason.py`, reading the output line by line. This is new. I do not write code. I direct, agents generate, I validate and decide. Usually validating means looking at a rendered thing and saying yes or no. Today it meant staring at raw output from an agent I had spent the night specifying, and figuring out whether it was any good.

It ran. First try, no errors, two findings, zero dropped. By every check I had written down the night before, it passed.

It was also vague as hell.

## What the agent said, and why it bothered me

The tool I am building is called Observator Clew. I have 62 repositories on GitHub. Creating them was cheap. Knowing which ones still need me is not. So the thing watches all 62 of them, decides what deserves my attention, and sends it to me in Telegram without being asked.

The architecture has a deterministic layer that flags candidates, then an agent that investigates only those, requests the files it wants to read, and recommends surface or suppress with a reason either way. A separate piece of plain code, not the model, decides whether that recommendation reaches me at all.

Here is what it produced on one repo:

> The README describes an April Fools challenge project, links to a Vercel-hosted demo, and documents a Gemini API dependency. The quiet period may reflect its event-specific purpose, but the API-backed demo makes its intended ongoing operation worth checking.

Read that as the person who owns the repo. What am I supposed to do with "worth checking"? I already knew it was quiet. That is why it surfaced. The finding handed the decision back to me with a shrug.

Nothing was broken. The loop worked, the schema validated, the fetch hit live GitHub. It was working correctly and saying nothing.

## The tell was in a number I had set myself

I had capped the agent at four tool turns. A bound on the loop, so a chatty model cannot keep asking for files until the API bill stops it.

It used one. It asked for the README and judged.

That is the whole diagnosis. Not a wrong architecture, not a bad prompt in the abstract. The agent was starving and I had built the kitchen.

Claude read the code and found it in about a minute, which I want to be honest about because I did not find it myself. The function that assembles the candidate facts passed exactly four things to the model: the repo name, its bucket, whether deployment evidence existed, and a one-line reason. No file list.

So the model had no idea a `vercel.json` existed. Or a `package.json`. It guessed README.md because every repo has one. It was not being lazy. It was reaching for the only door it could see.

Four facts in, one file read, a hedge out. That chain is tidy in retrospect and was invisible from the output alone.

## Taking a field away from the model

While we were in there, a second thing surfaced that I liked more than the fix.

The agent had been reporting its own `what_checked` field. "README.md (received truncated contents)." That is the model telling me what it looked at.

But my own architecture says file presence is a fact, and facts belong to code. Code knows exactly which files it fetched, because code fetched them. So we took the field away from the model entirely. Now the loop records every executed fetch, marks whether it was live or a labeled fallback, and overwrites whatever the model claimed.

This is a lesson I paid for on an earlier build called Porch Light, where a required field taught a model what a valid answer looked like and it obligingly produced them. A model asked to self-report its own evidence will eventually get it wrong, and "WHAT I CHECKED" is the first line a judge reads. Better to make it unfalsifiable than to trust it.

After the change, the same repo came back with `['README.md (live)', 'vercel.json (live)', 'package.json (live)']` and a finding that named `api/divine.js`, a 256 MB memory limit, and a 30-second timeout.

Specific. Checkable. Mine to act on.

## Access to the folder is not the same as reading the folder

Both of those fixes came out of reading the actual code. That sounds obvious. It was not what happened the first time.

When I said the findings were too vague, Claude gave me a diagnosis: the candidate facts probably do not include the file list, so the model cannot know what it is allowed to ask for. That turned out to be correct. It was also produced without opening the file.

I said look at the code we have now. Reading it found the same root cause plus three more things inference had not reached. The loop exits when it hits the four-turn cap, but if the model requested a file on that last turn, those requests are never answered and the next call chains onto a conversation with a dangling question. The `what_checked` field was model-reported, which is the Porch Light problem again. And repo-name validation accepted a bare name as well as the full owner/name, which would have quietly become the wrong key when the decision store started fingerprinting on it.

It happened again a block later. I asked for the next set of build instructions and got them written from memory of the design rather than from the code. I asked whether the disk had been checked. It had not. Reading it killed one requirement that was unnecessary and surfaced a real bug nobody had noticed: the second run overwrites the saved run file, so tapping a button on an older message would record a decision against the wrong repository. My demo runs twice. That one was going to happen on camera.

My build agent did the same thing in the other direction, three separate times, insisting a file still held old content it had read earlier. Once it told me my API key was still a placeholder. It was not, and had not been for hours.

The mistake I had been making is assuming that because an agent has access to the folder, it is looking at the folder. It is not, unless you say so. Both of mine were working from a remembered version of a repository that had changed under them, and neither noticed, because nothing about working from memory feels different from the inside.

I think the fix is just the instruction. Read the disk first, every time, and say so when you have not. That is now a standing line in both of my agent setups.

## The spec got the architecture right and caught nothing that made it usable

I wrote a lot before build day. Requirements in EARS notation, a design document, a task list, an architecture card, a file-by-file map with a pass check on every block. That work paid for itself. The loop shape was verified the night before, the model's limits were known, the guards were specified before any code existed.

None of it caught a single thing that made the tool unusable.

Telegram attaches inline buttons to the message, not to positions inside it. So three findings produced six buttons in one block with nothing saying which pair belonged to which repository. On camera I would have tapped No action and not known what I declined. I found that by opening Telegram and trying to tap one.

The briefing was a wall. Findings ran together with no separation, and the fields that carry the reasoning are long by design. Also found by reading it on a phone-sized window.

The suppressed line, which is the entire point of the product, sat at the bottom of the message underneath three findings. On a second run it is the headline, not a footnote. Found by running twice and scrolling.

None of those are in the spec. None of them would have failed a pass check. Every one of them made the thing worse to use than it was to describe.

I do not think this argues against writing the spec. The spec is why the architecture held up when I started pulling on it at one in the afternoon. But I notice that everything that survived contact with the plan was structural, and everything the plan missed was about what it is like to hold the thing in your hand.

## The thing I decided not to build

Then I pushed again, because the findings still felt incomplete. Most of these repos have a deployed site. There is usually a link right there in the README. Should the agent check whether the site is still up?

I wanted to. It is the obvious next move and it would look great on camera.

I am not doing it, and the reason is the whole point of the tool. An HTTP 200 does not mean an app works. A static shell returns 200 with a dead API key behind it. Parked domains answer. Broken deployments still serve pages. And a 404 does not prove abandonment. A liveness check would produce a green checkmark I could not defend, which is exactly the kind of confident wrongness this thing exists to avoid.

So the agent names the URL and says plainly that it cannot verify whether it is live. That is the honest maximum. I think a named target with a stated unknown is worth more than a checkmark that means nothing, though I will admit it is the less impressive demo.

Every finding carries a field called `what_cant_know` and it is required, not optional. If the model cannot name something it is unable to establish, that is a signal it overclaimed somewhere else.

## Where this leaves me

Three blocks left: the Telegram push, the decision buttons that let me tell it "no action" and have it remember, and the page that shows the full reasoning for every finding. Code freeze is in a few hours.

What I keep thinking about is the terminal. I have shipped a lot of things by directing agents and validating what came back. Today the validating part could not be delegated, because the output was correct and unhelpful at the same time, and no test I could write would have caught that. A passing check and a useful answer are different things, and only one of them shows up in a terminal as green.

Quick context if you are new here. I work in the California courts, running court operations for the county. I started building with AI in July 2025 and I have been learning in public ever since. I do not write the code. I direct, the agents generate, I validate and decide. I build the Clew Suite, a set of civic tech tools for making complex systems easier to inspect, at https://earlgreyhot1701d.github.io/Clew-Labs/. That is the lens I am writing from.

AI Assisted. Human Approved. Powered by NLP.
