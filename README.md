# kano-init

**kano-init** is a script to initialize a fresh installation of the Kanux OS
on a Kano kit. It is based mostly on the [raspi-config](https://github.com/asb/raspi-config)
tool from Alex Bradbury.

**kano-init** needs a Debian Jessie system running `systemd`.

## Onboarding UI

As of kano-init 3.3, there is a new version which uses a QML based graphical UI called Overture.
It is bound to the system via systemd - the command below will skip kano-init and take the kit
directly to the Dashboard or Greeter:

```
$ systemctl set-default graphical.target
```

The command below will disable the Dashboard UI and start the new onboarding on next boot:

```
$ systemctl set-default multi-user.target
```

Whilst the new onboarding is running, it is possible to start lightdm in the background without disrupting the UI:

```
$ systemctl start lightdm
```

## New Onboarding commands

The following new commands are available. They are ready to be invoked from the Overture app
in order to follow through the steps.

 * `kano-init finalise -f` : mark the onboarding as complete, so the next reboot will take user to desktop


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
