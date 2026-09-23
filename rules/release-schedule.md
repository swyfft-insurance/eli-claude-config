# Release Schedule

Beta is cut from `development` every Tuesday. Beta goes to prod every Friday. Hotfixes are the only exception.

So when code reached prod is simple arithmetic from its `development` merge date:

- merged Wednesday through the following Tuesday morning → beta that Tuesday → prod that Friday

Example: #22779 merged to `development` Monday 9/14, went to beta Tuesday 9/15, and reached prod Friday 9/18.
