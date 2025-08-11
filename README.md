# ZK-Pwn-Manage
Advanced Offensive Security Toolkit for ZKTeco Devices
# ZK Attendance Machine Manager

**Advanced Penetration Testing & Administration Toolkit for ZKTeco Devices**

ZK Attendance Machine Manager is a powerful Python-based toolkit for security researchers, red team operators, and penetration testers to remotely manage, audit, and monitor ZKTeco biometric attendance machines.  
Supports multi-target management, real-time monitoring, advanced user searches, and live capture operations.

⚠ **Legal Disclaimer**  
This tool is intended for **authorized security testing, auditing, and research** purposes only. Using it against devices without explicit written permission may violate local, state, or federal laws. The author assumes **no responsibility** for misuse.

---

## ✨ Key Capabilities

### 🎯 Target Machine Management
- Specify target machines via CLI parameters
- Support single or multiple devices simultaneously
- Switch targets at runtime

### 👥 User Management
- Enumerate all registered users
- Add / delete / update user information
- Search users by ID or name
- Manage fingerprint templates and card IDs

### 📊 Attendance Management
- Retrieve attendance logs
- Real-time live capture of check-ins/outs
- Export attendance data
- Clear logs (authorized scenarios)

### 🔍 Advanced Search
- Find users across all connected devices
- Cross-reference with attendance history
- Real-time monitoring of specific users

### 🔧 Device Administration
- Retrieve device information & status
- Synchronize date/time
- Reboot or power-off device
- Enable/disable device remotely

---

## 📋 Requirements
```pip install pyzk ```

🚀 Usage
1. Command Line Interface:
   
base:
<pre> python main.py </pre>
Single target:
<pre> python main.py --target 192.168.1.100 --interactive </pre>
Quick Commands:
<pre>
# Find user by ID
python main.py --target 192.168.1.100 --user 1258

# Find user by name
python main.py --target 192.168.1.100 --user "Nguyen Van A"

# Check status of all targets
python main.py --target 192.168.1.100,192.168.1.101 --check

# Start real-time capture
python main.py --target 192.168.1.100 --live

# Start interactive menu
python main.py --interactive
</pre>

Main Menu:
<pre>
0. Show/Change target machines
1. Get attendance logs
2. Get users
3. Get device info
4. Comprehensive machine check
5. Get fingerprint templates
6. Add new user
7. Delete user
8. Clear attendance logs
9. Set device time
10. Enable/Disable device
11. Test all machines
12. 🔍 Find user by ID
13. 🔍 Find user by name
14. 🔍 Find user with attendance
15. 🔍 Search users by pattern
16. 🔴 Live capture (single machine)
17. 🔴 Live capture (all machines)
18. 🔴 Interactive live capture session
19. 🎯 Monitor specific user live
20. 📊 Live capture status
21. 🛑 Stop live capture
</pre>

⚙ Configuration
Default targets
<pre>
  DEFAULT_MACHINES = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
</pre>
Change port and timeout
<pre>
  def connect_machine(ip, port=4370, timeout=5):
</pre>

🛡 Security Considerations
<pre>
 No password storage: Tool does not persist device credentials
 Read-only by default: Write operations require confirmation
 Network isolation recommended: Run in secure lab environments
</pre>



