Community Port information
======

This is the "Community Port" for Kia and Hyundai.

The port was started by Andrew Frahn of Emmertex.  
@ku7 on commaai Slack, and ku7 tech on youtube
https://www.youtube.com/channel/UCXmUBvIuFLjLRuJ0mX298Ng
Please support the port, and if you can, please help support me!



What is special about this port?
------

It's unfettered awesome with no corporate fears!
Where non standard features were made by someone other than me @ku7, they are credited with there Slack Username

Based on OpenPilot 0.5.7 from comma.ai

- Do not disable when Accelerator is depressed (MAD button*)
- Disable auto-steering on blinker, but leave OP engaged
- - Disabled on first blink, and stays disabled until 1 second of no blinking.
- Sounds! (Thanks @Sid and @BogGyver and #Tesla in general) (SND button*)
- Tesla UI (Thanks everyone in #Tesla)
- - 3 Switch positions change the display, you probably want it far left.*
- Advanced Lane Change Assist (Thanks @BogGyver) (ALCA button*)*
- - And with Blind Spot Detection for any Kia/Hyundai with it
- Panda auto-detects Camera Pinout
- - And now so does OP!  LKAS on CAN 2 or CAN 3, it doesn't matter!
- No need for giraffe switches, If no EON, then forwards stock camera (Thanks @JamesT)
- Dashcam Recorder (Thanks @pjlao307)
- Full Time Stock LKAS passthrough*
- - Including High Beam Assist and Automatic Emergency Braking, Blind Spot, Traffic Sign Detection, and more.
- - This includes Land Departure Warning, but stock LKAS must be enabled for this.
- Optional Dynamic Stock and OP Steering.  The moment OP isn't steering, it switched back to Stock (LKAS button*)*
- ** Temporarily removed ** CLI Based Real Time Tuning (Thanks @JamesT)
- Unsupported cars default to Kia Sorento.  This should work for most cars.
- Cruise Setpoint set from OSM Speed Limit*
- Probably other things I have forgotten

* Has known issues

Known issues
------

- ALCA (Advanced Lane Change Assist) is not properly tuned.  Use with caution
- CAM (Stock LKAS Forwarding) occasionally silenetly faults, turning off stock LKAS
- Auto Speed Setpoint Control is irregular, the button spamming works perfect some times, not at all others
- Tri-State Switch is currently broken in NEOS, NEOS fix is needed
- Touch Events don't work properly in the new NEOS, changes are needed
- Panda Safety doesn't really exist


A note on visiond
------

There are mixed opinions about which visiond is best.
Until 0.5.4 wiggly, every new version was always undeniably better.


But then 0.5.4 Wiggle dropped, and this incredible visiond could drive down roads
never before possible.  Take corners never before possible.  But is was a little crazy for some.
A quick release 0.5.4 non wiggle was released.   It was like its predecessors, but better.


since then, debate has ensued.
so, choose your version, v0.5.7 is default.



Contributing
------

We welcome both pull requests and issues on
[github](http://github.com/commaai/openpilot). Bug fixes and new car ports encouraged.

Want to get paid to work on openpilot? [comma.ai is hiring](https://comma.ai/jobs/)

Licensing
------

openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.

Any user of this software shall indemnify and hold harmless Comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.

**THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
NO WARRANTY EXPRESSED OR IMPLIED.**

---

<img src="https://d1qb2nb5cznatu.cloudfront.net/startups/i/1061157-bc7e9bf3b246ece7322e6ffe653f6af8-medium_jpg.jpg?buster=1458363130" width="75"></img> <img src="https://cdn-images-1.medium.com/max/1600/1*C87EjxGeMPrkTuVRVWVg4w.png" width="225"></img>
