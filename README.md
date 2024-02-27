# LLM bot for Discord
 This project aims to put together the guts of a discord bot that is primarily powered by a LLM. The goal is to make a bot that can run an interactive and thematically relevant trivia session for a board gaming, and answer questions for a cosplay & general nerd culture special interest group. The first goal is to get trivia working, where working is defined by the bot running on-demand trivia sessions as well as running a trivia session at a set interval. Responses should be gathered by the bot and then assessed for correctness, cleverness/creativity, and humour, then this shoud be posted as a scoreboard. The second goal is to make the bot function as an on-demand rules lawyer for board games to cut down on pesky rule book scanning but also to help people pick up new games. Most established board games have their rules included in the trianing data for many current LLM's, but for some niche games this would then also mean we need to be able to scan PDF's and retrieve relevant information. Inital delovpment is being done in termux, using nano, on my phone. With everything running off the phone, I'll need to use the openAI API initially, but when this matures the end goal is to make local models easy to integrate instead.

Initial development is happning largly on my phone in termux using nano during commutes, so it'll be a bit rough and will make use of the openAI API but with time I'd like to transition this to using a local LLM, likely through gpt4all.

# Tasks
- [X] Run Trivia on Demand
- [ ] Run timed trivia in dedicated channel
- [ ] Persistent score board
- [X] Save historical questions to prevent repretition
- [X] Allow general QA style answers, especially for rules for board games
- [ ] Allow users to specify timeout for on demand trivia