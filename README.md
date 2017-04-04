# kano-init

**kano-init** is a script to initialize a fresh installation of the Kanux OS
on a Kano kit. It is based mostly on the [raspi-config](https://github.com/asb/raspi-config)
tool from Alex Bradbury.

**kano-init** needs a Debian Jessie system running `systemd`.

## Onboarding UI

As of kano-init 3.3, there is a new version which uses a QML based graphical UI called Overture.
It is bound to the system via systemd - the commands below summarize the available workflow options.

 * `kano-init schedule add-user` will disable the Dashbhoard and start the Overture app with no Xserver on next reboot.
 * `kano-init finalise -f` will mark the onboarding as complete, the next reboot will go to either Dashboard or Greeter.
 * `kano-init create-temp-user [-x]` creates a temporary kano user which is returned through `stdout`, `[-x]` starts an empty XServer.
 * `kano-init rename-user <current> <new>` renames the user account, group name, home folder, and its inner permissions.
 * `kano-init xserver-start <username>` starts the Xserver in the background, logs in as username.
 * `kano-init status` will return `disabled` when normal Dashboard mode, `add-user` when Overture is running or scheduled for next reboot.

At the systemd level, `systemctl set-default multi-user.target` will enable the Overture app through systemd,
leaving the Xserver and Dashboard disabled. You can still `systemctl start ligthdm` without disrupting the Overture app.

Conversely, `systemctl set-default graphical.target` will switch back to taking the user to the Dashboard or Greeter on next reboot.

Note that the Overture app will run as root. Use `create-temp-user` along with `su` to impersonate regular and X11 apps.

## Automation

Kano Init is capable of going through the initial setup process unattended, create the user account
and take you directly to the graphical desktop.

To automate these steps, do the following:

 * edit `/var/cache/kano-init/status.json` to look like this

 `{"username": "myusername", "stage": "username-stage"}`

 * edit `/boot/init.conf` to look like this:

```
{
    "kano_init": {
        "skip": true,
        "user": "myusername"
    },
    "kano_init_flow": {
        "skip": true
    }
}
```

On next reboot, you should see the graphical desktop logged in as `myusername` after a short while.
