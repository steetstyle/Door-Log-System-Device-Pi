
import os
import sys
from time import sleep

if not os.getegid() == 0:
    sys.exit('Script must be run as root')

from core.app import App

import os
if __name__ == "__main__":
    app = App()
    app.run()
