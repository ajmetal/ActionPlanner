Our search approach involved a heuristic that would check each potential state against a collection of required
components to reach a given goal. If whatever the state was producing wasn't in the goal, or didn't
contribute a necessary component item in creating our goal, we gave it a distance of infinity so that it
would move to the back of the queue. We were going to implement a pruning routing that would eliminate certain
options from consideration, but were unable to get that far.

We found it incredibly difficult to generate a collection of a base components to the goal items. We
considered resorting to cheating by hardcoding some information, like the maximum number of each item
that could be required by any potential goal, or what items are treated as tools instead of consumables.
We opted to do things the correct way by gathering this information programmatically, so that the program
would run reliably regardless of the input data. After talking with other students I've yet to hear of someone
completing the assignment without resorting to hardcoding information they gleaned from the input we were given.

team members: Samuel Shin, Andrew Johannes Spaulding