/**
 * kano-idle-daemon.c
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * A simple daemon which executes idle-action.sh when the kit was idle for a fixed
 * amount of time.
 *
 * Build depends: libx11-dev, libxss-dev
 */


#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/scrnsaver.h>


// Constant parameters.
const int IDLE_TIME_SEC = 4 * 60 * 60;
const int SLEEP_TIME_SEC = 1 * 60 * 60 + 1;
const char const *SCRIPT = "/usr/share/kano-idle-daemon/scripts/idle-action.sh";

// Global vars.
int g_isScriptExecuted = 0;


int getIdleTime() {
    time_t idleTime;

    static XScreenSaverInfo *saverInfo;
    Display *display;
    int screen;

    // Set the display and screen.
    display = XOpenDisplay(NULL);
    if (display == NULL) {
        return -1;
    }
    screen = DefaultScreen(display);

    // Query the X screen saver lib and get the idle time in seconds.
    saverInfo = XScreenSaverAllocInfo();
    XScreenSaverQueryInfo(display, RootWindow(display, screen), saverInfo);
    idleTime = (saverInfo->idle) / 1000;

    // Clean up.
    XFree(saverInfo);
    XCloseDisplay(display);

    return idleTime;
}

int main(int argc, char *argv[]) {
    int idleTime;

    // Enter the daemon loop.
    while (1) {
        idleTime = getIdleTime();
        printf("%d\n", idleTime);

        // Execute the idle script if the idle time has passed and the script was
        // not previously executed, or failed by any chance.
        if (idleTime >= IDLE_TIME_SEC && !g_isScriptExecuted) {
            int rc = system(SCRIPT);
            if (!rc)
                g_isScriptExecuted = 1;
        }

        sleep(SLEEP_TIME_SEC);
    }

    return 0;
}
