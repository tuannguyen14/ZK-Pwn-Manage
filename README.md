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
```bash
pip install pyzk
