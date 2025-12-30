# Detailed Project Status: Stage 3 (Bidding Integration)i

## 1. Networking & Security (Windows PowerShell)

To allow your Mac's Python scripts to communicate with the "unactivated"
Windows VM, you must explicitly open the inbound traffic ports. Run these in a
PowerShell (Admin) window inside the VM:

- Open the Bidding Port:
```PS
# Opens TCP 8080 for the Table Management Protocol
New-NetFirewallRule -DisplayName "Wbridge5-Bidding" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```
- Allow Local Ping (Optional but recommended for debugging):
```PS
# Allows the Mac to ping the VM to verify the network bridge is alive
netsh advfirewall firewall add rule name="Allow-ICMPv4-In" protocol=icmpv4:8,any dir=in action=allow
```
- Verify the Rule:
```PS
Get-NetFirewallRule -DisplayName "Wbridge5-Bidding"
```

## 2. Virtualization Choice & Setup

For a developer on an M3 Max, the architecture follows this translation path:

M3 (ARM64) → VM (ARM64) → Windows 11 (ARM64) → Prism (x86 Emulator) → Wbridge5
(x86 Binary).

| Component | Choice | Trade-off / Setup Note |
|--|--|--|
| Hypervisor | Parallels Desktop | **Pros**: "Lazy" one-click Windows install; best CLI for CI. **Cons**: Subscription cost. |
| Alternative | VMware Fusion Pro | **Pros**: Free for personal use. **Cons**: Setup is slightly more manual. |
| Guest OS | Windows 11 ARM | Required for M-series compatibility. Emulates Wbridge5 with near-zero latency. |
| Licensing | Unactivated | Skip the key. Results in a watermark but zero functional impact on your bidding logic. |

### 2.1. Locating the Target IP (Mac to VM)

To connect the pipeline, you need the VM's internal IP address. Run this
inside the Windows VM:

- **Command**: `ipconfig`
- **Target**: Look for the `IPv4 Address` under the Ethernet adapter (e.g.,
  `10.211.55.3`).
- **On Mac**: Set your environment variable: `export
  BRIDGE_VM_IP="10.211.55.3"`.

## 3. The Bidding Protocol (Blue Chip Bridge)

Wbridge5 acts as the "Dealer/Server" while your Mac acts as the "Table
Manager/Director." The conversation follows this exact sequence:

1. Handshake:
- **Mac sends**: `Connecting "M3-Max" as South using protocol 1.0\r\n`
- **VM responds**: `South ("Wbridge5") seated\r\n`
2. Sending the Deal:
- **Mac sends**: `North's hand: [PBN_STRING]\r\n`
3. Receiving the Bid:
- **VM responds**: `South bids 1NT\r\n`

## 4. Execution Roadmap for your Break

| Step| Action | Status |
|--|--|--
| 1. Infra | Install Parallels/VMware and Windows 11 ARM. | In Progress |
| 2. Networking | Run the PowerShell `New-NetFirewallRule` command provided above. | Ready |
| 3. Bidding | Download Wbridge5; set to Communication > Table Manager > Server. | Ready |
| 4. Logic | Finalize `bid-hands.py` using the BCB socket strings. | Pending |

## 5. Summary of Choice Trade-offs

Using a local VM allows you to "kick the tires" for free (or the cost of
Parallels) without incurring GCP hourly fees. However, once you move to GCP,
you lose the M3 Max's "snappiness" but gain the ability to run native x86
Windows Server without any emulation layers, which is the gold standard for
long-term reliability.

### 5.1. The GCP Lifecycle (Future State)

When you move to GCP to avoid the local "Watermark," your bridge.sh will
replace the local IP with a dynamic one:

- **Start VM**: `gcloud compute instances start wbridge5-service`
- **Get IP**: `gcloud compute instances describe wbridge5-service --format='get(networkInterfaces[0].accessConfigs[0].externalIp)'`
- **Stop VM**: `gcloud compute instances stop wbridge5-service`

## 6. Running from Mac

### 6.1. Running Parallels Headless

You can control the VM entirely from your Mac terminal using the prlctl
command (Parallels Control). This is the "Pro" way to keep your M3 Max
environment clean.

To start the VM without a window:
```bash
prlctl start "Windows 11" --headless
```

To check the status:
```bash
prlctl list
```

To shut it down gracefully:
```bash
prlctl stop "Windows 11"
```

### 6.2. Automating Wbridge5 Startup

Since the VM is headless, you won't be able to click "Start" on the Wbridge5
UI. You need the engine to launch automatically in Server Mode the moment
Windows boots.

The Shortcut Method:

1. In your VM, create a shortcut to `Wbridge5.exe`.
2. Right-click the shortcut > **Properties**.
3. In the "Target" field, append the command-line arguments for the Table
   Manager (Wbridge5 documentation notes `-t` or `-server` flags often work,
   but verify your version's specifics).
4. Move this shortcut to the Windows Startup folder: `shell:startup`.

### 6.3. Updated Networking Context

Running headless makes your previous PowerShell and IP steps even more
critical because you won't have a GUI to troubleshoot "live".

- Confirm Inbound Rule: Ensure the New-NetFirewallRule for port 8080 is active
  so the headless process can receive your Python socket calls.
- Static IP: In Parallels, go to Preferences > Network and ensure your VM is
  assigned a "Permanent" or static IP so your Mac scripts don't lose the
  connection.

## 7. Setup for GCP

For a cloud deployment, relying on the "Desktop Shortcut" method is possible
via Remote Desktop (RDP), but it breaks the Virtue of Laziness because it
requires manual intervention every time you rebuild the VM.

To make this truly "Cloud Native" and headless, you should use GCP Startup
Scripts (PowerShell) to configure the Windows environment as code.

### 7.1. The "Lazy" Automation: Startup Scripts

GCP allows you to provide a `metadata-startup-script` that runs as the System
user every time the VM boots. This is where you set up your environment
without ever opening a GUI.

### 7.2. Implementation: PowerShell vs. Registry

Since Wbridge5 is a GUI-based application, it requires a "User Session" to run
its engine logic correctly. In a headless GCP environment, you have two
professional options:

**Option A: The Registry "Run" Key (Auto-Login Method)**

This is the most compatible way for legacy GUI apps. You configure Windows to
auto-login to a specific user and then launch the app via the registry.

```PS
# Set up Auto-Login (Careful with credentials in plain text here; use GCP Secret Manager in production)
$regPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
Set-ItemProperty -Path $regPath -Name "AutoAdminLogon" -Value "1"
Set-ItemProperty -Path $regPath -Name "DefaultUserName" -Value "BridgeUser"
Set-ItemProperty -Path $regPath -Name "DefaultPassword" -Value "YourSecurePassword"

# Add Wbridge5 to the Run key with the Table Manager flag
# Note: Verify the '-t' or '-server' flag in your local 'tire-kicking' first
$runPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
Set-ItemProperty -Path $runPath -Name "Wbridge5" -Value "C:\Wbridge5\Wbridge5.exe -t"
```

**Option B: Scheduled Task (The "Cleanest" Headless Way)**

This allows the app to start "At System Startup" without needing a visible
desktop session.

```PS
$action = New-ScheduledTaskAction -Execute "C:\Wbridge5\Wbridge5.exe" -Argument "-t"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "Wbridge5Engine" -Action $action -Trigger $trigger -Principal $principal
```

3. Using a Service Wrapper (NSSM)

If Wbridge5 proves "cranky" when running without a real desktop session, many
developers use NSSM (Non-Sucking Service Manager). It wraps a .exe and turns
it into a standard Windows Service that you can manage via Start-Service or
Stop-Service.

```PS
# Hypothetical automated setup via Chocolatey or direct download
nssm install Wbridge5Service "C:\Wbridge5\Wbridge5.exe" "-t"
Start-Service Wbridge5Service
```
