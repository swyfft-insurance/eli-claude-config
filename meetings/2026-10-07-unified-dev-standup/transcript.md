# Unified Dev Standup (2026-10-07)

Transcript 2026-10-07T16:46:25.5360766Z to 2026-10-07T17:28:02.5035152Z (UTC).
Times are offsets into the transcript. Speaker labels are Teams' attribution and can be wrong.

[00:14:15] **Ken Smith:** Good morning. Let's go ahead and get started. And Alex, you're up.

[00:14:21] **Alex Good:** Yep, so yesterday picked up where Ryan left off on the ticket that was supposed to monitor the prod deploys and kind of put those statuses out in Slack. So I added the slot swap to the reporting and hopefully now it's going to show in the right. Slack channel also ported another group of PowerShell tests that we had over to Pester and this morning. So... Homeowner doc validation was the only, or sorry, homeowner deck pages were the only bank group that wasn't writing its results to the EF. Policy validation table, so filled in that gap. And then this afternoon, I'm going to look at a log monitor ticket that I have in my name. That's it.

[00:15:20] **Ken Smith:** All right, thank you very much, Alex. Andrew.

[00:15:24] **Andrew Parkins:** Morning, yep. So, yesterday in the morning I was working on improving diagnostics output for tracking down issues when request fail. Had a meeting with Verisk about their 360 value API, and from there they pointed me how to how their docs work, which is a little weird, but... Anyway, I got the username and password, so I started working, kicking the tires on that guy. I'll be kicking the tires some more today and then sending out some technical questions. And that's probably it for me.

[00:15:56] **Ken Smith:** Thank you, Andrew. Research it.

[00:16:00] **Chris Harrington:** Hi everybody, good morning. So yesterday we had a meeting to go over some of the commercial statement of value stuff, and this is kind of a spiral a bit. So I've been looking at modifying how the landing page for the commercial landing page works a little bit, removing some fields, adding some fields, that kind of thing. So put together a Marc for what I think they should look like, and I'm going to bring that up with the front end sync in just a little bit here. And then the rest of my time has been spent on some bug fixes that I have with the new purchase page. There's a couple that are outstanding. And then I still have this pull request open for requiring an agent to opt in for before his cox high value referral gets created in Zendesk. We've got a pull request open for that. I'd love to get merged in as soon as possible so everybody has some free eyes. And then for the rest of the day, I think it's going to be making sure that that statement of value is Mark is pretty good spot. And then I did get a ticket from Drew earlier for updating the, making a fix or something to the purchase moratorium page. So this feels like a pretty good time to modernize that page. So I'll be looking at that today too. That's it, no blockers.

[00:17:09] **Ken Smith:** Thank you, Chris. For Schenk.

[00:17:13] **Chris Schenk:** Morning. Yesterday I worked on the accept reject plan and got finished up and began working on a PRD for the new soft decline workflow changes that were requested by Roman on Monday. Today I'm coding out that accept reject stuff and I'm hopefully going to finish the soft decline. The clients that PRD work and log down.

[00:17:35] **Ken Smith:** Thank you, Chris. Dan.

[00:17:40] **Dan Melson:** Let's see, yesterday, yesterday I was working on the, I had to redo some of the stuff for the risk selection decline logging. It was logging as, it's logging as warning and it's dumping the exception and the stack trace and all that information. One of the tickets was to cut some of those down. My initial one, I cut all the risk selections down and made them debug and And not, or I didn't make them debug. I made them not not display all that, but Justin brought up the point that sometimes we really want the stack trace. So I rewrote that so that it only does specific ones that we know for state closed, county closed, things like that. They now log as debug. with just a limited message and stuff, the information that was requested on the ticket. So I got that wrapped up and that's merging today. And now I'm working on the full sprinkler systems for QBE South Carolina commercial. It's not showing up in the drawer and it needs to be full sprinklers required for a frame type or 4 plus stories. So that's what I'm doing now and that's about it.

[00:18:50] **Ken Smith:** Thank you, Dan. Darius.

[00:18:56] **Darius Carrick:** Hey there. So yesterday worked on a bunch of e-signature PRs. I have two features left for that for the binding requirements UI that I'm wrapping up today. I also reviewed a PR from Konstantin that fixed an issue with the underwriting notes sync. I got that approved and through. And then I also... SOV stuff that Chris was talking about and we both kind of have Um... similar but slightly different options for the landing page changes. And I've got that up as like a little prototype so we can look at both of those and see which ones we want to demo to business or if we want to show them both. But I think kind of the key thing there is the way the landing page changes. takes in the number of buildings and then the way that we fill out the schedule. So there's some interesting ways to do that. And then today, I had an e-signature demo with business. And as a result of that, they asked me also to create them a a reference guide that underwriting and customer support can use in case they get calls from agents or need to support something. So I'm going to work on that as well. And also there's some new binding requirement changes for commercial. So I scheduled a meeting with Jennifer. Alexis to go over those tomorrow. Um... And then yeah, I have several meetings after that today. And just continuing on the e-signature stuff. One other thing to note with that is the bold sign sandbox has an API limit of 50 requests per hour. So that was filling up my. my requests pretty quick with TeamCity web UI acceptance tests. It actually blocked me from doing my demo completely this morning. So I put a PR through to shut the e-signature off for those web UI acceptance tests on TeamCity. That's it for me.

[00:21:11] **Ken Smith:** Alright, thank you, Darius. Eli.

[00:21:17] **Eli Koslofsky:** Yeah, today and yesterday I've been working on some Vave commercial underwriting guideline tickets, had some feedback from Konstantin that I addressed, and I've got the first four of them queued to merge, and then I'm going to work on the next three. And then I'm also just working on a log monitor bug for Laurel. Or not log monitor, one of the, you know, a test that failed. And that's it.

[00:21:54] **Ken Smith:** All right, thank you very much. Let's see, Eric.

[00:22:00] **Eric Chen:** Hey everyone. Yesterday did a handful of things, but the main thing was for Hadron commercial on rewrites or reprices. I fixed the deductible is not showing up, and that's the first part of the of getting my work out for. form rewrite bugs. The second part will be covering the additional coverage section. And before I proceed with that, I'll probably have to check with a handful of people, mostly Jay. I'll probably ask you about some work you did last year, so I know that's terrifying. Other than that, Once I finish that up, I think I promised Drew a little bit of NFIP work, at least some progress. But those two things should take up the rest of my day.

[00:22:50] **Ken Smith:** Great. Thank you, Eric. James.

[00:22:59] **James Whitfield:** Hello, everybody. Yesterday, I spent the bulk of the day on... Production testing, various tickets, mainly focused on some of the changes and, excuse me, the advisor space and claims. Also today, working on beta. Picking things out to see what I can grab and test. Also added some tickets on QB Commercial. Remainder dates will be on QBE Commercial post-buying. I started testing that a little while ago. And I might jump back to beta for some testing high priority tickets ticket board. That's it.

[00:23:42] **Ken Smith:** All right, thanks, James.

[00:23:44] **James Whitfield:** Yep.

[00:23:45] **Ken Smith:** Gena.

[00:23:50] **Jannatul Mustafa:** Hello. So yesterday I had completed working on the reprice and endorsements as well as claims. And today I've been assigned to some tickets on U-Track. So just going through those and also questioning any concerns that I have with the assignee. That's all. Thank you.

[00:24:12] **Ken Smith:** Thanks, Ken. Jay.

[00:24:17] **Jay Kint:** Good morning. SPOL, still ongoing. I managed to get the seven PRs up, two of them are merged in. Number 3, Ron noticed a couple things. Thank you, Ron, for looking at that. And so I had, between me and Claude, got those resolved. I'm now working on just getting a merge that had some conflicts taken care of. Hopefully get that pushed and then it should be able to. I do need a second review on that. After that I got four more to go. So it's been much slower than I'd anticipated. I'd hoped that it would only take a little bit of time. maybe a day or two to get this through the seven PRs, but so still working on that. After that, I currently in, I think I've wrapped up most of the bugs I was working on, so I need to chair, I need to pull some for my queue, log monitor and some, I think it was a test failure too, it's still ongoing, I need to get those in. That Zendesk ticket turns out it was already fixed can in a previous log monitor bug, so that was kind of easy. That was nice, and yeah, I think I think that's probably it for me. Oh, we had we had a meeting yesterday with Phi Sigma.

[00:25:25] **Ken Smith:** Kay.

[00:25:36] **Jay Kint:** And that was very productive. They're going to send over a new document. Turns out that there are some incongruities between their documentation and their implementation. Who would have guessed? Yeah, well, and that's just, I was deathly afraid that maybe I had missed something. And so I was like, they're going to get into this meeting and say, oh, you just need to do this, this, and this. I'm like, oh, duh.

[00:25:47] **Ken Smith:** Really, I don't think we had noticed.

[00:25:58] **Jay Kint:** But turns out it really was their problem. So thankfully. So they have, I should be getting a document either later today or tomorrow with some updated instructions and samples. And I'll take it from there and start trying to put together a composed loop on a claim life cycle. It'll be very small, won't have all the things it needs, but it should hopefully have enough to just just kind of give us a very proof of concept of how the workflow might go. So yeah, that should be it for me.

[00:26:27] **Ken Smith:** Thank you, Jay. Jill.

[00:26:31] **Jill Ashley:** Hello, let's see. Yesterday I spent some time, I met with Maureen and Chrissy and spent some time figuring out how to properly warn the user when there's an inconsistency between agents and IMS producer contacts. All seems to come down to somebody adding a producer contact in IMS and giving them Swift login without adding them in Swift. And then we had a meeting about onboarding and I picked some of that work back up. And then today I will be primarily working on adding MEP to some South Carolina policy docs and notices. That's all.

[00:27:05] **Ken Smith:** Great. Thanks, Jill. Jill.

[00:27:08] **Joe Nichols:** Hello. So yesterday. was asking some questions about the tickets and also Just got a PR for a. Thing with invoice numbers, the make payment page was displaying an internal one that looks an awful lot like a... External invoice number, but it's not the same number, so... That's. That's in PR. Good. Yeah, more bugs. either one or two more with the address sync stuff. And yeah, that's it for now.

[00:28:05] **Ken Smith:** Thanks, Jill. Laurel.

[00:28:09] **Joe Nichols:** So, yesterday I was working on more of the more of the testing the functions that I just added to the mobile the non-failure list on the from the from the CS code to the Excel test. I noticed there was some of the. Cloud might be trying to figure out which have have a list of the excluded known failures. Now you can go to the Swyfft test three if you want to folder, let me know, and there is XML list you can know which keyword lead to which. Not an issue from the automation report, and on that yesterday start go back to track down the test failures. I have one test failure, test code failure, push out, PR push out, and today I'm going to continue working on that. I'm going through the failures, so I might...

[00:29:24] **Ken Smith:** All right, thank you, Laurel. Josh.

[00:29:30] **Joshua Spink:** Hey everyone, yesterday I was doing a little more work with partner API, knowledge base articles and whatnot, but then shifted over to Vave split allocation work and then chasing down a few other bugs. So yeah, doing split Vave allocations today and... other release testing in beta. That's it.

[00:29:52] **Ken Smith:** Thanks, Josh. Justin.

[00:29:57] **Justin Harris:** I've finished up my work on DP3, so I've switched back to refactoring to get rid of throw of no calls. And then I will be out next week and the week after that for PTO, no blockers.

[00:30:15] **Ken Smith:** All right. Thanks, Justin. Konstantin. Konstantin, if you're there, we're not hearing you. Muted. All right, we'll come back. Uh, Larry.

[00:30:39] **Larry Beall:** So I'm just finishing up a couple comments on a couple bug PRs, get those merged in, doing the same with one of the adjuster queue modifications PRs, get that merged in, and then we had a couple of new requests on the way they would like. The new gesture queue to work come in yesterday, so I am ticketed that and getting ready to start working on that as well. So a gesture queue for the foreseeable future, I guess.

[00:31:11] **Ken Smith:** All right, thanks, Larry. Mahendra. Andrew, I'm not hearing you. All right, we'll come back. Let's see, Mary Kay.

[00:31:32] **Mary Kay Hurlburt:** Today, I'm working on re-adding the MEP form back to South Carolina lines of business and fixing any EV allocation issues that Josh finds them. That's it.

[00:31:45] **Ken Smith:** Alright, thanks, Mickey. Melissa.

[00:31:50] **Melissa Freeman:** Today I have several meetings and working on Zendesk tickets and one very difficult commercial renewal. That's it for me.

[00:32:04] **Ken Smith:** Sorry about that, Melissa. Uh, that is you.

[00:32:09] **Mevcun Alacakir:** Hey, morning. Yesterday, NP column classification. SSSTE step removal discussion. And today, weekly schema review. invoice cost analysis for September. SQL vulnerability assessment on the Azure side and working on the SQL audit log reports. That's all I have.

[00:32:38] **Ken Smith:** Thank you, Madam Jim. Nick.

[00:32:43] **Nick Fee:** Hi everyone. My day is mainly Zendesk and beta testing, and I have a meeting with Melissa this afternoon. That's it for me.

[00:32:51] **Ken Smith:** Thanks, Nick. Patti.

[00:32:56] **Patti Sundius:** Nick is always so fast. And I'm reading something else. So yesterday, QBE Commercial South Carolina post bind testing did some knowledge sharing with Gena. And then today on beta ticket testing and post bind testing for QBE Commercial South Carolina, and logging tickets as I find issues. And that's it for me. Thanks.

[00:33:26] **Ken Smith:** Thank you, Patti, Phil.

[00:33:30] **@1:** Hey everyone. So I got a couple pieces of my Ivan's outbound export fixes out there. I've been working to keep them manageable, which has added a little bit of extra turn, but I think it's worth it. I also got the change out for New Jersey Stamping Office. to make sure that they get their SLA transaction numbers generated. There was a corner case. This afternoon, I'll just be shepherding those, pulling off more items related to items as I can put them in and I have Some tickets to create and I gotta talk to Jeff, or not Jeff. I'm thinking about the Jeffs I used to work for, but speak with Greg about New York, Sam Bank, so... That's it.

[00:34:24] **Ken Smith:** Thanks, Phil. Good Jill.

[00:34:29] **Pi-Chun Wu:** Yeah, so work on the SSSSS package modification for another DB and also participate in a meeting to remove Tableau everything. from the SSL package. And I also going to identify some database table as a candidate for fabric free trial CDC data mirroring. That's it.

[00:34:56] **Ken Smith:** Thanks, Richard. Warren.

[00:35:01] **Warren Hirschbuehler:** Morning, everyone. Yesterday, fixed a bug. I think it was QA found it. So they put in a Connecticut address, which we don't have anything for. It basically gave an API error and the page just kind of sat there and looked at you and did nothing. I mean, surface that as a... Better error with a toast or an unsupported quote page if you're not logged in. Also fix some tests and policy purchase. There's some questions that were unanswered that blocked the purchase through. And this morning created a, just created a PR. Basically, premium errors would throw an invalid operation. I think it was Dave. Anyways, they rejected their they said no, so that premium error bubble up as an error instead of a UI, you know, unsupported or move on with the other quotes, so... Pick up up your grades and I have. Handful of more bugs and such, and I'll go ping Drew to see if he's got more NFIP stuff, and that's in it, if me.

[00:36:09] **Ken Smith:** Great. Thanks, Warren. Wendell.

[00:36:18] **Wendell Joost:** Good morning. I'm thinking about using the cat for Princess Donut and going as Dungeon Crawl, Crawler Carl for Halloween. I got, I couldn't sleep last night, so I went through a bunch of the log monitor tickets and did some triage and turned Claude loose on some. Fixes for that, I've also got a hefty PR there that I'm going to be talking to the front-end team about in 7 minutes that adds a one-time code for validation when an insured requests. a cancel policy. And that's to spoke with Michael Manzi and Gena about this. And that replaces the old give us the policy number and the zip code. And that's good enough for us to do whatever. As we are removing humans from the loop. and automating this stuff, we need better, more secure checks. And let's face it, the humans weren't really checking anyway. So. That's in the pipeline. And then Ken's Claude was flagging my PRs with changes requested and then lagging review for, and Ken, if you've got some way that I can poke Claude rather than poke you to make those happen, that would be.

[00:37:47] **Ken Smith:** I uh, I did a re I had a couple more reviews at 7:46 A.m.

[00:37:47] **Wendell Joost:** A... Okay, and I think Mike Ludwig got back on those. So we may be, this may be me poking you for one more. So.

[00:38:03] **Ken Smith:** I, once more, got it. OK.

[00:38:05] **Wendell Joost:** Yes. So once more on to the breach, dear friends, as they say. So, and then I've got school this afternoon, but I'll be on Slack and Claude will be grinding out code. And that's it for me.

[00:38:22] **Ken Smith:** Okay, thanks Wendell. All right, back to, let's see, Konstantin, are you there?

[00:38:30] **Konstantin Konstantinov:** Yeah, sorry, my teams just died right at that moment, or about that moment. So, on my side, I've merged this big PR related to roller architecture, and Darius, I guess, picked up whatever slacks is left after that. I hope, at least I hope so. More things. I'm working on two, one log monitor ticket is submitted as a pair that's claim times related, another one is related to phone numbers. The pair is coming shortly, and yesterday I submitted the pair related to changes to renewal notes. I believe Darius mentioned that he's already approved that. I think that's it. Once I'm done with the... Work monitor ticket, I'll take a look at my pipeline. That's it for now.

[00:39:15] **Ken Smith:** Great. Thank you, Konstantin. And Mahendra, if you're there.

[00:39:19] **Mahendra Kaushal:** Yeah, yesterday was testing the release and verifying tickets. The same as today, today, that's all I have.

[00:39:31] **Ken Smith:** Thank you, Mahendra. Let's see, Ehren.

[00:39:35] **Ehren Weerheim:** Just the usual yesterday meetings, most of the day, and then ticket and clog. Today will be more meetings, more ticket and o'clock. That's it for me.

[00:39:46] **Ken Smith:** Okay. Thanks, Ehren. Wayne.

[00:39:50] **Wayne Allen:** Yep, Arnold, trivia for the week is this week in 1969, Monty Python's Flying Circus was first episode. Surprisingly enough, it lasted for one year. That's it. For the impact. that Monty Python has had, it was only there for a year. Kind of crazy. Anyway, for myself, yesterday was... I worked on a feature for Greg to allow him to do policy doc downloads without rewarding, deserting to going to Swyfft test 2. So that is done and merged this morning. And also kind of working on the DP3 IMS configs, going back and forth with Mary Kay. Today is meeting day, so that's going to be the look of the day between... There's probably some bugs stumped, and I did get a message back from Inspection Depot about my questions, so I'll look at that. That's it.

[00:40:54] **Ken Smith:** Great. Thank you, Wayne. On my side, continuing to, I think I've dealt with all of the feedback that I've gotten on my big, let's completely change how we print policy deck PRs and going to need for some QA help on that. Beyond that, oh, and waiting for a full QA pass on that and a couple of, for full Deep City pass on that and a couple of other PRs. Other than that, meetings and emails and such. Thanks, everyone.

[00:41:30] **Chris Harrington:** Thanks.

[00:41:30] **Jill Ashley:** Thank you. Thank you. Merci.

[00:41:31] **Andrew Parkins:** Thanks, Darius. Thanks. Have a good day.

[00:41:31] **Mahendra Kaushal:** Bye. Thanks. Thanks. Bye. Thanks. Bye.

[00:41:32] **Patti Sundius:** Thanks. Thank you.
