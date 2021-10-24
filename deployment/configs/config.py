import os

logDir = "log"

infoLogPath = f'{logDir}/info.log'
warnLogPath = f'{logDir}/warn.log'

sshLogPath = f'{logDir}/ssh.log'

defaultSSHKeyPath = os.path.join(os.environ["HOME"], ".ssh", "id_rsa")

nodesToMonitor = []
