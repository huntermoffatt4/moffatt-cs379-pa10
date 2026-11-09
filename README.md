# CS379 PA 10 Channels

**Instructor starter:** https://github.com/cwillpinto/cs379-pa10-channels  
**Due:** Wednesday, November 4, 2026 at 11:59 PM Central  
**Task:** [PA_10_Channels.md](PA_10_Channels.md)

This repository is an intentionally incomplete student starter. Read the task and complete the TODOs. Replace the included prior-stage TODO modules with your own verified PA 1–9 work before testing.

## Work in your own repository

Choose **Use this template** on the instructor repository and create a repository under your own GitHub account. Clone your repository, work there, and push to your `origin`. If you clone the instructor repository directly, create an empty repository in your account, then run:

```sh
git remote rename origin upstream
git remote add origin <your-repository-url>
git remote -v
git push -u origin <your-branch>
```

Check both URLs and your branch before pushing. Never push student work to the instructor starter.

## Check and submit

Run `python test_channels.py` from the repository root. The supplied starter must fail at unfinished TODOs; the success token is earned only after the implementation and harness pass. The token does not grade written reasoning.

Submit through Blackboard: `PA10_Theory.pdf` (or `.md`), `channels.py` with your working prior-stage files, and terminal output showing `CHANNEL_SYNC_VERIFIED`. Include your own repository URL and exact commit SHA as evidence. Confirm the Blackboard item and due setting before submitting.


## Your repository and Blackboard evidence

Use **Use this template** on the instructor repository to create a copy under
your own GitHub account. Clone your copy and work there. Do not push completed
work to the instructor repository.

For direct cloning, create an empty repository under your own account first:

```sh
git clone https://github.com/cwillpinto/cs379-pa10-channels
cd cs379-pa10-channels
git remote rename origin upstream
git remote add origin <your-student-owned-repository-url>
git remote -v
git branch --show-current
git push -u origin main
```

Replace the placeholder with your repository URL. Before pushing, verify that
`origin` points to your account and `upstream` points to `cwillpinto`. Use your
actual branch name if it is not `main`. Submit your repository URL and the
output of `git rev-parse HEAD` in Blackboard, alongside the required files and
execution evidence. Blackboard remains the official submission location.
