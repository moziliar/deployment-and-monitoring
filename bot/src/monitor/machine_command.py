read_cpu = "top -bn1 | head -n3"
read_ps = "ps -eo pid,user,group,time,tty,%cpu | grep pts | grep student | grep -v grep"
read_memory = "free -h | grep Mem:"
read_uname = "uname"
