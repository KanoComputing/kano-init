# kano-init

**kano-init** is a script to initialize a fresh installation of the Kanux OS
on a Kano kit. It is based mostly on the [raspi-config](https://github.com/asb/raspi-config)
tool from Alex Bradbury.


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
