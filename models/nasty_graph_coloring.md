# Radio Frequency Assignment

We've got 6 cell towers and 4 available frequency channels.
Adjacent towers can't use the same channel or they'll interfere.

Tower connections (interference pairs):
- Tower 1 connects to towers 2, 3, 5
- Tower 2 connects to towers 1, 3, 4
- Tower 3 connects to towers 1, 2, 4, 6
- Tower 4 connects to towers 2, 3, 5
- Tower 5 connects to towers 1, 4, 6
- Tower 6 connects to towers 3, 5

Each tower needs exactly one channel.
We want to minimize how many distinct channels we actually use
(cheaper to license fewer frequencies).

If a channel is assigned to at least one tower, it counts as "used".
A tower's channel assignment can only count if that channel is marked as used.
