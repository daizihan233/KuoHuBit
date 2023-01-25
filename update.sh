# 呃…… 为什么要写这个 shell 脚本呢？因为这样更新起来快一点（大概）
kill $(cat bot.pid)
git pull
nohup poetry run python main.py &
