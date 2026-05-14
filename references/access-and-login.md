# Access and login

Mahuika is accessible via SSH (terminal/VSCode) or a web browser (OnDemand). All access goes via the `lander` jump host and requires IAM+MFA at login.

## Prerequisites

- An active NeSI account and project membership. Apply via `my.nesi.org.nz`.
- A second-factor authenticator app set up on your phone (TOTP).
- Optionally an SSH key pair created on the cluster (reduces login prompts).

## SSH config (Linux/macOS/WSL)

In `~/.ssh/config` on your laptop:

```sshconfig
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/ssh_mux_%h_%p_%r
    ControlPersist 1

Host lander
    User <username>
    HostName lander.hpc.nesi.org.nz
    ForwardX11 yes
    ForwardX11Trusted yes
    ServerAliveInterval 300
    ServerAliveCountMax 2

Host mahuika
    User <username>
    Hostname login.hpc.nesi.org.nz
    ProxyCommand ssh -W %h:%p lander
    ForwardX11 yes
    ForwardX11Trusted yes
    ServerAliveInterval 300
    ServerAliveCountMax 2
    # IdentityFile ~/.ssh/mahuika_key   # uncomment after setting up SSH key (below)
```

First time:

```bash
mkdir -p ~/.ssh/sockets
chmod 600 ~/.ssh/config
```

Replace `<username>` with your NeSI username.

**MobaXterm caveat**: doesn't support sockets, drop the first 4 lines (`Host *` block) when using MobaXterm.

## Connecting

```bash
ssh mahuika
```

First time prompts:

1. Accept host key (type `yes`).
2. Browser link `https://iam.nesi.org.nz/realms/public/device?user_code=XXXX-XXXX`, open it (Ctrl-click in most terminals).
3. Pick institution - sign in.
4. **Trusted device?** Yes if it's your personal laptop on a private network (skips MFA for 7 days). No if shared/incognito (you'll re-MFA every login).
5. If trusting, name the device (unique).
6. Scan TOTP QR code with authenticator app, enter 6-digit code.
7. Confirm you initiated the request (anti-phishing).
8. Press Enter in the terminal. Repeat the auth flow once more (skipped if you set up an SSH key, see below).

## Optional SSH key (recommended)

Eliminates one of the two auth prompts. Run **on Mahuika** (after first successful login):

```bash
mkdir -p ~/.ssh
[ -f .ssh/id_rsa ] || ssh-keygen -t rsa -q -N ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

Then **on your laptop**:

```bash
scp mahuika:~/.ssh/id_rsa ~/.ssh/mahuika_key
chmod 600 ~/.ssh/mahuika_key
```

Uncomment the `IdentityFile ~/.ssh/mahuika_key` line in `~/.ssh/config`.

Subsequent logins:

1. `ssh mahuika`
2. Follow IAM link.
3. Optionally enter 6-digit TOTP if trusted-device window has expired.
4. Press Enter, you're in.

**Do not** copy `mahuika_key` to other devices. Anyone with that key can be you on Mahuika. Admins can read `/home` so don't put secrets there.

## Web browser access

<https://ondemand.nesi.org.nz/> gives a dashboard for JupyterLab/RStudio/VSCode/Virtual Desktop/Terminal sessions on Mahuika. Useful for one-off tasks without SSH setup. (This skill scope intentionally excludes OnDemand-specific features, refer the user to the NeSI docs for OnDemand workflow detail.)

## VSCode Remote-SSH

Install the "Remote - SSH" extension. With the `~/.ssh/config` above, VSCode shows `mahuika` and `lander` under Remote Explorer. Connecting opens an editor on the login node.

Issues:

- VSCode tries to auto-install its remote server. If it stalls, run `code --version` once on Mahuika manually or check the VSCode output panel for the install command.
- Memory-heavy extensions on the login node can be noticed by other users, keep the Mahuika-side workspace small.

## Windows

Pick one:

1. **WSL** (recommended): Install WSL, then use the Linux instructions above.
2. **VSCode**: works with or without WSL via Remote-SSH.
3. **MobaXterm**: SSH+SFTP+X-server in one. Use the installer edition. Drop the `Host *` sockets block from `~/.ssh/config`.
4. **Git Bash**: works for terminal-only. Fewer features than MobaXterm.
5. **PuTTY / WinSCP**: legacy options, more setup, no X.

## X11 forwarding

For GUI applications launched on Mahuika displaying on your laptop:

```bash
ssh -Y mahuika
xeyes        # quick test
```

You need an X server on your laptop:

- Linux: built-in.
- macOS: XQuartz.
- Windows: VcXsrv, MobaXterm built-in, or WSLg with WSL2.

Heavy GUIs (ParaView, VMD) over X11 are sluggish. Use OnDemand Virtual Desktop instead.

## Port forwarding

To reach a service running on a compute node from your laptop:

```bash
ssh -L 8888:wbn175:8888 mahuika
```

This forwards local port 8888 to port 8888 on `wbn175`. The connection goes through `lander` automatically because of the ProxyCommand.

## Common problems

### "Account is not ready"

Either your project allocation hasn't been activated yet, or you have multiple projects and need to wait for them all to be set up. Check `my.nesi.org.nz`; contact support if it persists.

### Connection drops or freezes

`ServerAliveInterval 300` keeps the connection probing every 5 minutes. If you're on flaky WiFi, lower to 60 s. Use `tmux` on Mahuika for long-running sessions:

```bash
ssh mahuika
tmux new -s work
# inside: run your stuff
# Ctrl-b d to detach
# tmux a -t work to reattach
```

### MFA "device not recognised"

The IAM provider treats new browsers/incognito sessions as new devices. Either retrust or log in with the `--user_code` link in the *same* browser session as your last successful login.

### Replacing your TOTP

If you change phones, you have to replace your Additional Authentication Credentials via `my.nesi.org.nz`. See <https://docs.nesi.org.nz/Getting_Started/FAQs/How_do_I_replace_my_Additional_Authentication_Credentials/>.

### Locale errors at login

`Locale not supported by C library` is fixed by ensuring `LC_ALL` and `LANG` are valid in your shell init (e.g. `export LC_ALL=en_NZ.UTF-8`).

### `nn_doomed_list: file list not found`

You're on `login01` or `login02`. Switch:

```bash
ssh login03
```

(See `references/filesystems.md`.)
