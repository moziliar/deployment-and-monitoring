import os

logDir = "log"

infoLogPath = f'{logDir}/info.log'
warnLogPath = f'{logDir}/warn.log'
errorLogPath = f'{logDir}/error.log'

sshLogPath = f'{logDir}/ssh.log'

sshKeyPath = os.path.join(os.environ["HOME"], ".ssh", "id_rsa")

nodesToMonitor = []
