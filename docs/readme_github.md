- [🚀 issue - branch - merge](#-issue---branch---merge)
  - [To merge to main](#to-merge-to-main)
- [🤖 github actions](#-github-actions)

# 🚀 issue - branch - merge

As much as possible I want to use this approach 👍

From https://github.com/castorfou/lmelp, 🔗

- create an issue 📝
- from issue create merge request (this auto creates the branch) 🔀
- work from this branch 💻
- when satisfied merge to main (then github actions will trigger) ✅


## To merge to main

from `Pull requests` tab, should automatically suggest `Compare & pull request`
![pull request](image.png)

then `View pull request` > `Merge pull request` > `Confirm merge` > `Delete branch`

# 🤖 github actions

configured in `.github/workflows/ci.yml` ⚙️