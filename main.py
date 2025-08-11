from zk import ZK
import datetime
from zk.finger import Finger
from zk.user import User
import argparse
import sys

# Machine IP addresses
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='ZK Attendance Machine Manager')
    parser.add_argument('--target', '-t', 
                       help='Target machine IPs (comma-separated) or single IP. Example: --target 192.168.1.100 or --target 192.168.1.100,192.168.1.101,192.168.1.102')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive menu')
    parser.add_argument('--live', '-l', action='store_true',
                       help='Start live capture for all machines')
    parser.add_argument('--user', '-u', type=str,
                       help='Search for specific user ID across all machines')
    parser.add_argument('--check', '-c', action='store_true',
                       help='Check all machines status')
    
    return parser.parse_args()

DEFAULT_MACHINES = ["192.168.9.x", "192.168.7.x", "192.168.10.x"]
machines = DEFAULT_MACHINES.copy()

def set_target_machines(target_string):
    """Set target machines from command line argument"""
    global machines
    if target_string:
        # Tách các IP bằng dấu phẩy và loại bỏ khoảng trắng
        machines = [ip.strip() for ip in target_string.split(',') if ip.strip()]
        print(f"🎯 Target machines set to: {machines}")
    else:
        print(f"📡 Using default machines: {machines}")

conn = None

def connect_machine(ip, port=4370, timeout=5):
    """Connect to a ZK machine"""
    try:
        zk = ZK(ip, port=port, timeout=timeout)
        conn = zk.connect()
        print(f"✓ Connected to machine: {ip}")
        return conn
    except Exception as e:
        print(f"✗ Failed to connect to {ip}: {e}")
        return None

def disconnect_machine(conn):
    """Disconnect from ZK machine"""
    if conn:
        conn.disconnect()
        print("✓ Disconnected from machine")

# ==================== ATTENDANCE FUNCTIONS ====================

def get_attendance_logs(conn, user_id=None):
    """Get attendance logs from the machine"""
    try:
        attendance = conn.get_attendance()
        if user_id:
            filtered_logs = [record for record in attendance 
                           if record.user_id == user_id or record.user_id == str(user_id) or record.user_id == f"0{user_id}"]
            for record in filtered_logs:
                print(f"User ID: {record.user_id}, Time: {record.timestamp}, Status: {record.status}, Punch: {record.punch}")
            print(f"Found {len(filtered_logs)} records for user {user_id}")
        else:
            for record in attendance[:10]:  # Show first 10 records
                print(f"User ID: {record.user_id}, Time: {record.timestamp}, Status: {record.status}, Punch: {record.punch}")
            print(f"Total attendance records: {len(attendance)}")
        return attendance
    except Exception as e:
        print(f"Error getting attendance: {e}")
        return []

def clear_attendance_logs(conn):
    """Clear all attendance logs"""
    try:
        conn.clear_attendance()
        print("✓ Attendance logs cleared")
    except Exception as e:
        print(f"Error clearing attendance: {e}")

# ==================== USER MANAGEMENT FUNCTIONS ====================

def get_users(conn, user_id=None):
    """Get all users or specific user"""
    try:
        users = conn.get_users()
        if user_id:
            filtered_users = [user for user in users 
                            if user.user_id == user_id or user.user_id == str(user_id) or user.user_id == f"0{user_id}"]
            for user in filtered_users:
                print(f"User ID: {user.user_id}, Name: {user.name}, Privilege: {user.privilege}, Password: {user.password}")
            print(f"Found {len(filtered_users)} users with ID {user_id}")
        else:
            for user in users[:10]:  # Show first 10 users
                print(f"User ID: {user.user_id}, Name: {user.name}, Privilege: {user.privilege}")
            print(f"Total users: {len(users)}")
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def set_user(conn, uid, name, privilege=0, password='', group_id='', user_id='', card=0):
    """Add or update a user"""
    try:
        conn.set_user(uid=uid, name=name, privilege=privilege, password=password, 
                     group_id=group_id, user_id=user_id, card=card)
        print(f"✓ User {name} (ID: {uid}) added/updated")
    except Exception as e:
        print(f"Error setting user: {e}")

def delete_user(conn, uid):
    """Delete a user"""
    try:
        conn.delete_user(uid=uid)
        print(f"✓ User {uid} deleted")
    except Exception as e:
        print(f"Error deleting user: {e}")

def clear_users(conn):
    """Clear all users"""
    try:
        conn.clear_users()
        print("✓ All users cleared")
    except Exception as e:
        print(f"Error clearing users: {e}")

# ==================== FINGERPRINT FUNCTIONS ====================

def get_templates(conn, user_id=None):
    """Get fingerprint templates"""
    try:
        templates = conn.get_templates()
        if user_id:
            filtered_templates = [template for template in templates if template.uid == user_id]
            for template in filtered_templates:
                print(f"User ID: {template.uid}, Finger ID: {template.fid}, Valid: {template.valid}")
            print(f"Found {len(filtered_templates)} templates for user {user_id}")
        else:
            for template in templates[:10]:  # Show first 10 templates
                print(f"User ID: {template.uid}, Finger ID: {template.fid}, Valid: {template.valid}")
            print(f"Total templates: {len(templates)}")
        return templates
    except Exception as e:
        print(f"Error getting templates: {e}")
        return []

def clear_templates(conn):
    """Clear all fingerprint templates"""
    try:
        conn.clear_templates()
        print("✓ All templates cleared")
    except Exception as e:
        print(f"Error clearing templates: {e}")

def save_template(conn, uid, fid, template_data, valid=1):
    """Save a fingerprint template"""
    try:
        template = Finger(uid=uid, fid=fid, valid=valid, template=template_data)
        conn.save_template(template)
        print(f"✓ Template saved for user {uid}, finger {fid}")
    except Exception as e:
        print(f"Error saving template: {e}")

def delete_template(conn, uid, fid=None):
    """Delete fingerprint template(s)"""
    try:
        if fid is not None:
            conn.delete_template(uid, fid)
            print(f"✓ Template deleted for user {uid}, finger {fid}")
        else:
            # Delete all templates for user
            templates = conn.get_templates()
            user_templates = [t for t in templates if t.uid == uid]
            for template in user_templates:
                conn.delete_template(uid, template.fid)
            print(f"✓ All templates deleted for user {uid}")
    except Exception as e:
        print(f"Error deleting template: {e}")

# ==================== DEVICE INFO FUNCTIONS ====================

def get_device_info(conn, machine_ip):
    """Get comprehensive device information"""
    try:
        print("=== DEVICE INFORMATION ===")
        print(f"Machine IP: {machine_ip}")
        
        # Basic info
        device_name = conn.get_device_name()
        print(f"Device Name: {device_name}")
        
        is_connected = conn.is_connect
        print(f"Is Connected: {is_connected}")
        
        # Firmware and version info
        firmware_version = conn.get_firmware_version()
        print(f"Firmware Version: {firmware_version}")
        
        # Serial number
        serial_number = conn.get_serialnumber()
        print(f"Serial Number: {serial_number}")
        
        # Platform
        platform = conn.get_platform()
        print(f"Platform: {platform}")
        
        # Device name
        device_name = conn.get_device_name()
        print(f"Device Name: {device_name}")
        
        # Face algorithm version (if supported)
        try:
            face_version = conn.get_face_version()
            print(f"Face Algorithm Version: {face_version}")
        except:
            print("Face Algorithm Version: Not supported")
            
        # Fingerprint algorithm version (if supported)  
        try:
            fp_version = conn.get_fp_version()
            print(f"Fingerprint Algorithm Version: {fp_version}")
        except:
            print("Fingerprint Algorithm Version: Not supported")
            
    except Exception as e:
        print(f"Error getting device info: {e}")

def get_device_time(conn):
    """Get device time"""
    try:
        device_time = conn.get_time()
        print(f"Device Time: {device_time}")
        return device_time
    except Exception as e:
        print(f"Error getting device time: {e}")

def set_device_time(conn, timestamp=None):
    """Set device time"""
    try:
        if timestamp is None:
            timestamp = datetime.datetime.now()
        conn.set_time(timestamp)
        print(f"✓ Device time set to: {timestamp}")
    except Exception as e:
        print(f"Error setting device time: {e}")

# ==================== SYSTEM FUNCTIONS ====================

def restart_device(conn):
    """Restart the device"""
    try:
        conn.restart()
        print("✓ Device restart initiated")
    except Exception as e:
        print(f"Error restarting device: {e}")

def power_off_device(conn):
    """Power off the device"""
    try:
        conn.poweroff()
        print("✓ Device power off initiated")
    except Exception as e:
        print(f"Error powering off device: {e}")

def enable_device(conn):
    """Enable device (unlock)"""
    try:
        conn.enable_device()
        print("✓ Device enabled")
    except Exception as e:
        print(f"Error enabling device: {e}")

def disable_device(conn):
    """Disable device (lock)"""
    try:
        conn.disable_device()
        print("✓ Device disabled")
    except Exception as e:
        print(f"Error disabling device: {e}")

def refresh_data(conn):
    """Refresh data on device"""
    try:
        conn.refresh_data()
        print("✓ Device data refreshed")
    except Exception as e:
        print(f"Error refreshing data: {e}")

def test_voice(conn, index=0):
    """Test device voice"""
    try:
        conn.test_voice(index)
        print(f"✓ Voice test {index} played")
    except Exception as e:
        print(f"Error testing voice: {e}")

# ==================== ACCESS CONTROL FUNCTIONS ====================

def set_tz_info(conn, tz_id, start_time, end_time):
    """Set timezone information"""
    try:
        # This is a simplified example - actual implementation may vary
        print(f"Setting timezone {tz_id} from {start_time} to {end_time}")
        # conn.set_tz_info would be implemented here
    except Exception as e:
        print(f"Error setting timezone info: {e}")

# ==================== LIVE CAPTURE FUNCTIONS ====================

import threading
import time
from datetime import datetime

class LiveCaptureManager:
    """Manager for live capture functionality across multiple machines"""
    
    def __init__(self):
        self.capture_threads = {}
        self.capture_active = {}
        self.capture_data = {}
        
    def start_live_capture_single(self, machine_ip, duration=None, callback=None):
        """Start live capture for a single machine"""
        if machine_ip in self.capture_active and self.capture_active[machine_ip]:
            print(f"⚠️ Live capture already running for {machine_ip}")
            return False
            
        self.capture_active[machine_ip] = True
        self.capture_data[machine_ip] = []
        
        thread = threading.Thread(
            target=self._live_capture_worker, 
            args=(machine_ip, duration, callback)
        )
        thread.daemon = True
        self.capture_threads[machine_ip] = thread
        thread.start()
        
        print(f"✅ Live capture started for {machine_ip}")
        return True
    
    def start_live_capture_all(self, duration=None, callback=None):
        """Start live capture for all machines"""
        print(f"🚀 Starting live capture for all {len(machines)} machines...")
        started_count = 0
        
        for machine in machines:
            if self.start_live_capture_single(machine, duration, callback):
                started_count += 1
                time.sleep(0.1)  # Small delay to avoid overwhelming
        
        print(f"✅ Live capture started for {started_count}/{len(machines)} machines")
        return started_count
    
    def stop_live_capture(self, machine_ip=None):
        """Stop live capture for specific machine or all machines"""
        if machine_ip:
            if machine_ip in self.capture_active:
                self.capture_active[machine_ip] = False
                print(f"🛑 Stopping live capture for {machine_ip}")
            else:
                print(f"⚠️ No active capture for {machine_ip}")
        else:
            # Stop all captures
            for machine in list(self.capture_active.keys()):
                self.capture_active[machine] = False
            print("🛑 Stopping all live captures...")
    
    def get_capture_status(self):
        """Get status of all live captures"""
        active_captures = sum(1 for active in self.capture_active.values() if active)
        total_events = sum(len(data) for data in self.capture_data.values())
        
        print(f"\n📊 LIVE CAPTURE STATUS:")
        print(f"Active captures: {active_captures}")
        print(f"Total events captured: {total_events}")
        
        for machine, active in self.capture_active.items():
            status = "🟢 ACTIVE" if active else "🔴 STOPPED"
            event_count = len(self.capture_data.get(machine, []))
            print(f"  {machine}: {status} ({event_count} events)")
    
    def _live_capture_worker(self, machine_ip, duration, callback):
        """Worker thread for live capture"""
        start_time = time.time()
        last_attendance_count = 0
        
        print(f"🔴 Starting live monitoring for {machine_ip}")
        
        while self.capture_active.get(machine_ip, False):
            try:
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    print(f"⏰ Duration limit reached for {machine_ip}")
                    break
                
                # Connect to machine
                conn = connect_machine(machine_ip, timeout=3)
                if not conn:
                    time.sleep(5)  # Wait before retry
                    continue
                
                # Get current attendance
                attendance = conn.get_attendance()
                current_count = len(attendance)
                
                # Check for new records
                if current_count > last_attendance_count:
                    new_records = attendance[last_attendance_count:]
                    
                    for record in new_records:
                        event_data = {
                            'machine': machine_ip,
                            'timestamp': record.timestamp,
                            'user_id': record.user_id,
                            'status': record.status,
                            'punch': record.punch,
                            'captured_at': datetime.now()
                        }
                        
                        self.capture_data[machine_ip].append(event_data)
                        
                        # Print real-time event
                        print(f"🔔 LIVE EVENT [{machine_ip}] - "
                              f"User: {record.user_id} | "
                              f"Time: {record.timestamp.strftime('%H:%M:%S')} | "
                              f"Status: {record.status}")
                        
                        # Call custom callback if provided
                        if callback:
                            try:
                                callback(event_data)
                            except Exception as e:
                                print(f"⚠️ Callback error: {e}")
                
                last_attendance_count = current_count
                disconnect_machine(conn)
                
                # Wait before next check
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error in live capture for {machine_ip}: {e}")
                time.sleep(5)
        
        # Cleanup
        self.capture_active[machine_ip] = False
        print(f"🔴 Live capture stopped for {machine_ip}")

# Global live capture manager
live_manager = LiveCaptureManager()

def start_live_capture(machine_ip=None, duration=None, show_users=True):
    """Start live capture with optional user resolution"""
    
    def event_callback(event_data):
        """Callback to process live events"""
        if show_users:
            # Try to get user name
            try:
                conn = connect_machine(event_data['machine'], timeout=2)
                if conn:
                    users = conn.get_users()
                    user_name = "Unknown"
                    
                    for user in users:
                        if (user.user_id == event_data['user_id'] or 
                            user.user_id == str(event_data['user_id'])):
                            user_name = user.name
                            break
                    
                    print(f"👤 User Name: {user_name}")
                    disconnect_machine(conn)
            except:
                pass  # Don't let user resolution errors stop live capture
    
    if machine_ip:
        return live_manager.start_live_capture_single(machine_ip, duration, event_callback)
    else:
        return live_manager.start_live_capture_all(duration, event_callback)

def stop_live_capture(machine_ip=None):
    """Stop live capture"""
    live_manager.stop_live_capture(machine_ip)

def live_capture_status():
    """Show live capture status"""
    live_manager.get_capture_status()

def live_capture_interactive():
    """Interactive live capture session"""
    print("\n" + "="*60)
    print("🔴 LIVE CAPTURE SESSION")
    print("="*60)
    print("Commands:")
    print("  start <ip>     - Start capture for specific machine")
    print("  start all      - Start capture for all machines") 
    print("  stop <ip>      - Stop capture for specific machine")
    print("  stop all       - Stop all captures")
    print("  status         - Show capture status")
    print("  export         - Export captured data")
    print("  clear          - Clear captured data")
    print("  quit           - Exit live capture")
    print("="*60)
    
    while True:
        try:
            command = input("\n[LIVE] Enter command: ").strip().lower()
            
            if command == "quit" or command == "exit":
                stop_live_capture()  # Stop all captures
                break
            
            elif command.startswith("start "):
                target = command.split(" ", 1)[1]
                if target == "all":
                    start_live_capture()
                else:
                    start_live_capture(target)
            
            elif command.startswith("stop "):
                target = command.split(" ", 1)[1]
                if target == "all":
                    stop_live_capture()
                else:
                    stop_live_capture(target)
            
            elif command == "status":
                live_capture_status()
            
            elif command == "export":
                export_live_data()
            
            elif command == "clear":
                clear_live_data()
            
            elif command == "help":
                print("Available commands: start, stop, status, export, clear, quit")
            
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping all live captures...")
            stop_live_capture()
            break
        except Exception as e:
            print(f"Error: {e}")

def export_live_data(filename=None):
    """Export captured live data to file"""
    if not any(live_manager.capture_data.values()):
        print("⚠️ No live data to export")
        return
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"live_capture_{timestamp}.txt"
    
    try:
        with open(filename, 'w') as f:
            f.write("LIVE CAPTURE DATA EXPORT\n")
            f.write(f"Exported at: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            
            total_events = 0
            for machine, events in live_manager.capture_data.items():
                if events:
                    f.write(f"MACHINE: {machine}\n")
                    f.write("-" * 30 + "\n")
                    
                    for event in events:
                        f.write(f"Time: {event['timestamp']} | "
                               f"User: {event['user_id']} | "
                               f"Status: {event['status']} | "
                               f"Punch: {event['punch']}\n")
                        total_events += 1
                    
                    f.write("\n")
            
            f.write(f"\nTotal Events: {total_events}\n")
        
        print(f"✅ Live data exported to: {filename}")
        print(f"Total events exported: {total_events}")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def clear_live_data():
    """Clear all captured live data"""
    confirm = input("Are you sure you want to clear all live data? (yes/no): ")
    if confirm.lower() == 'yes':
        live_manager.capture_data.clear()
        print("✅ Live data cleared")
    else:
        print("❌ Clear operation cancelled")

def monitor_specific_user_live(user_id, duration=None):
    """Monitor specific user across all machines in real-time"""
    print(f"\n🔍 MONITORING USER {user_id} LIVE")
    print("="*50)
    
    def user_callback(event_data):
        """Callback for specific user events"""
        if (event_data['user_id'] == user_id or 
            event_data['user_id'] == str(user_id) or
            event_data['user_id'] == f"0{user_id}"):
            
            print(f"🎯 TARGET USER EVENT!")
            print(f"   Machine: {event_data['machine']}")
            print(f"   User ID: {event_data['user_id']}")
            print(f"   Time: {event_data['timestamp']}")
            print(f"   Status: {event_data['status']}")
            print(f"   Punch: {event_data['punch']}")
            print("-" * 30)
    
    # Start monitoring all machines
    live_manager.start_live_capture_all(duration, user_callback)
    
    try:
        if duration:
            print(f"⏰ Monitoring for {duration} seconds... Press Ctrl+C to stop early")
            time.sleep(duration)
        else:
            print("⏰ Monitoring indefinitely... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping user monitoring...")
    finally:
        stop_live_capture()

# ==================== SEARCH FUNCTIONS ====================

def find_user_in_machine(machine, user_id, search_type="user_id"):
    """Find a specific user in a machine"""
    conn = connect_machine(machine)
    if not conn:
        return None
    
    try:
        users = conn.get_users()
        found_users = []
        
        for user in users:
            if search_type == "user_id":
                # Search by user_id with different formats
                if (user.user_id == user_id or 
                    user.user_id == str(user_id) or 
                    user.user_id == f"0{user_id}" or
                    user.user_id == f"{user_id:05d}"):  # Zero-padded format
                    found_users.append(user)
            elif search_type == "name":
                # Search by name (case insensitive partial match)
                if user_id.lower() in user.name.lower():
                    found_users.append(user)
            elif search_type == "uid":
                # Search by UID
                if user.uid == user_id or user.uid == int(user_id):
                    found_users.append(user)
        
        return found_users
    except Exception as e:
        print(f"Error searching users in {machine}: {e}")
        return None
    finally:
        disconnect_machine(conn)

def find_user_in_all_machines(user_id, search_type="user_id"):
    """Find a user across all machines"""
    print(f"\n{'='*60}")
    print(f"SEARCHING FOR USER: {user_id} (Search Type: {search_type.upper()})")
    print(f"{'='*60}")
    
    total_found = 0
    results = {}
    
    for machine in machines:
        print(f"\n🔍 Searching in machine: {machine}")
        found_users = find_user_in_machine(machine, user_id, search_type)
        
        if found_users is None:
            print(f"  ❌ Failed to connect to {machine}")
            results[machine] = "CONNECTION_FAILED"
        elif len(found_users) == 0:
            print(f"  ⭕ No users found in {machine}")
            results[machine] = "NOT_FOUND"
        else:
            print(f"  ✅ Found {len(found_users)} user(s) in {machine}:")
            results[machine] = found_users
            total_found += len(found_users)
            
            for user in found_users:
                print(f"    👤 UID: {user.uid}")
                print(f"       User ID: {user.user_id}")
                print(f"       Name: {user.name}")
                print(f"       Privilege: {user.privilege}")
                print(f"       Password: {'Set' if user.password else 'Not Set'}")
                print(f"       Group ID: {user.group_id}")
                print(f"       Card: {user.card}")
                print(f"    {'-'*40}")
    
    print(f"\n{'='*60}")
    print(f"SEARCH SUMMARY")
    print(f"{'='*60}")
    print(f"Total users found: {total_found}")
    print(f"Machines searched: {len(machines)}")
    
    # Show summary by machine status
    connected = sum(1 for result in results.values() if result not in ["CONNECTION_FAILED", "NOT_FOUND"])
    failed = sum(1 for result in results.values() if result == "CONNECTION_FAILED")
    not_found = sum(1 for result in results.values() if result == "NOT_FOUND")
    
    print(f"Connected machines: {connected}")
    print(f"Failed connections: {failed}")
    print(f"Machines without user: {not_found}")
    
    return results

def find_user_with_attendance(user_id, days_back=30):
    """Find user and their recent attendance across all machines"""
    print(f"\n{'='*60}")
    print(f"SEARCHING USER {user_id} WITH ATTENDANCE (Last {days_back} days)")
    print(f"{'='*60}")
    
    # First find the user
    user_results = find_user_in_all_machines(user_id, "user_id")
    
    # Then get attendance from machines where user was found
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    total_attendance = 0
    
    for machine, result in user_results.items():
        if isinstance(result, list) and len(result) > 0:
            print(f"\n📊 Getting attendance from {machine}:")
            conn = connect_machine(machine)
            if conn:
                try:
                    attendance = conn.get_attendance()
                    user_attendance = []
                    
                    for record in attendance:
                        # Check if record belongs to our user and is recent
                        if ((record.user_id == user_id or 
                             record.user_id == str(user_id) or 
                             record.user_id == f"0{user_id}") and
                            record.timestamp >= cutoff_date):
                            user_attendance.append(record)
                    
                    if user_attendance:
                        print(f"  ✅ Found {len(user_attendance)} attendance records:")
                        total_attendance += len(user_attendance)
                        
                        # Sort by timestamp
                        user_attendance.sort(key=lambda x: x.timestamp, reverse=True)
                        
                        # Show recent records (max 10)
                        for i, record in enumerate(user_attendance[:10]):
                            print(f"    {i+1:2d}. {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - "
                                  f"Status: {record.status} - Punch: {record.punch}")
                        
                        if len(user_attendance) > 10:
                            print(f"    ... and {len(user_attendance) - 10} more records")
                    else:
                        print(f"  ⭕ No recent attendance records")
                        
                except Exception as e:
                    print(f"  ❌ Error getting attendance: {e}")
                finally:
                    disconnect_machine(conn)
    
    print(f"\n📈 ATTENDANCE SUMMARY:")
    print(f"Total attendance records found: {total_attendance}")
    return total_attendance

def search_users_by_name(name_pattern, partial_match=True):
    """Search users by name pattern across all machines"""
    print(f"\n{'='*60}")
    print(f"SEARCHING USERS BY NAME: '{name_pattern}'")
    print(f"Partial match: {partial_match}")
    print(f"{'='*60}")
    
    all_matches = []
    
    for machine in machines:
        print(f"\n🔍 Searching in machine: {machine}")
        conn = connect_machine(machine)
        
        if not conn:
            print(f"  ❌ Failed to connect")
            continue
            
        try:
            users = conn.get_users()
            machine_matches = []
            
            for user in users:
                if partial_match:
                    if name_pattern.lower() in user.name.lower():
                        machine_matches.append(user)
                else:
                    if name_pattern.lower() == user.name.lower():
                        machine_matches.append(user)
            
            if machine_matches:
                print(f"  ✅ Found {len(machine_matches)} matching users:")
                for user in machine_matches:
                    print(f"    👤 {user.name} (ID: {user.user_id}, UID: {user.uid})")
                    all_matches.append({
                        'machine': machine,
                        'user': user
                    })
            else:
                print(f"  ⭕ No matching users found")
                
        except Exception as e:
            print(f"  ❌ Error searching: {e}")
        finally:
            disconnect_machine(conn)
    
    print(f"\n📋 SEARCH SUMMARY:")
    print(f"Total matches found: {len(all_matches)}")
    
    if all_matches:
        print(f"\nAll matches:")
        for i, match in enumerate(all_matches, 1):
            user = match['user']
            print(f"{i:2d}. {user.name} (ID: {user.user_id}) - Machine: {match['machine']}")
    
    return all_matches

# ==================== MAIN FUNCTIONS ====================

def on_get_log():
    """Get attendance logs for specific user"""
    zk = ZK('192.168.9.229', port=4370, timeout=5)
    conn = zk.connect()
    if conn:
        get_attendance_logs(conn, user_id=1258)
        conn.disconnect()

def on_get_users(machine):
    """Get users from a specific machine"""
    zk = ZK(machine, port=4370, timeout=5)
    conn = zk.connect()
    if conn:
        get_users(conn, user_id=1258)
        print("=================================================")
        print(f"Machine: {machine}")
        conn.disconnect()

def on_get_all():
    """Get users from all machines"""
    for machine in machines:
        conn = connect_machine(machine)
        if conn:
            get_users(conn)
            disconnect_machine(conn)

def on_check_machine(machine):
    """Check machine status and info"""
    conn = connect_machine(machine)
    if conn:
        get_device_info(conn, machine)
        disconnect_machine(conn)

def comprehensive_machine_check(machine):
    """Perform comprehensive check of a machine"""
    print(f"\n{'='*50}")
    print(f"COMPREHENSIVE CHECK FOR MACHINE: {machine}")
    print(f"{'='*50}")
    
    conn = connect_machine(machine)
    if not conn:
        return
    
    try:
        # Device information
        get_device_info(conn, machine)
        
        # Time information
        get_device_time(conn)
        
        # User count
        users = get_users(conn)
        
        # Attendance count
        attendance = get_attendance_logs(conn)
        
        # Template count
        templates = get_templates(conn)
        
        print(f"\nSUMMARY:")
        print(f"Users: {len(users) if users else 0}")
        print(f"Attendance Records: {len(attendance) if attendance else 0}")
        print(f"Fingerprint Templates: {len(templates) if templates else 0}")
        
    except Exception as e:
        print(f"Error during comprehensive check: {e}")
    finally:
        disconnect_machine(conn)

def interactive_menu():
    """Interactive menu for testing functions"""
    while True:
        print("\n" + "="*50)
        print("ZK ATTENDANCE MACHINE MANAGER")
        print("="*50)
        print(f"📡 Current targets: {len(machines)} machine(s)")
        print("="*50)
        print("0. Show/Change target machines")
        print("1. Get attendance logs")
        print("2. Get users")
        print("3. Get device info")
        print("4. Comprehensive machine check")
        print("5. Get fingerprint templates")
        print("6. Add new user")
        print("7. Delete user")
        print("8. Clear attendance logs")
        print("9. Set device time")
        print("10. Enable/Disable device")
        print("11. Test all machines")
        print("12. 🔍 Find user by ID in all machines")
        print("13. 🔍 Find user by name in all machines") 
        print("14. 🔍 Find user with attendance records")
        print("15. 🔍 Search users by name pattern")
        print("16. 🔴 Start live capture (single machine)")
        print("17. 🔴 Start live capture (all machines)")
        print("18. 🔴 Interactive live capture session")
        print("19. 🎯 Monitor specific user live")
        print("20. 📊 Live capture status")
        print("21. 🛑 Stop live capture")
        print("22. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "0":
            show_current_targets()
            new_targets = input("Enter new target IPs (comma-separated, or press Enter to keep current): ").strip()
            if new_targets:
                set_target_machines(new_targets)
        elif choice == "1":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            user_id = input("Enter user ID (optional): ")
            conn = connect_machine(ip)
            if conn:
                get_attendance_logs(conn, int(user_id) if user_id else None)
                disconnect_machine(conn)
        
        elif choice == "2":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            user_id = input("Enter user ID (optional): ")
            conn = connect_machine(ip)
            if conn:
                get_users(conn, int(user_id) if user_id else None)
                disconnect_machine(conn)
        
        elif choice == "3":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            on_check_machine(ip)
        
        elif choice == "4":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            comprehensive_machine_check(ip)
        
        elif choice == "5":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            user_id = input("Enter user ID (optional): ")
            conn = connect_machine(ip)
            if conn:
                get_templates(conn, int(user_id) if user_id else None)
                disconnect_machine(conn)
        
        elif choice == "6":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            uid = int(input("Enter user UID: "))
            name = input("Enter user name: ")
            privilege = int(input("Enter privilege (0=User, 1=Admin): ") or "0")
            password = input("Enter password (optional): ")
            conn = connect_machine(ip)
            if conn:
                set_user(conn, uid, name, privilege, password)
                disconnect_machine(conn)
        
        elif choice == "7":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            uid = int(input("Enter user UID to delete: "))
            conn = connect_machine(ip)
            if conn:
                delete_user(conn, uid)
                disconnect_machine(conn)
        
        elif choice == "8":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            confirm = input("Are you sure you want to clear all attendance logs? (yes/no): ")
            if confirm.lower() == 'yes':
                conn = connect_machine(ip)
                if conn:
                    clear_attendance_logs(conn)
                    disconnect_machine(conn)
        
        elif choice == "9":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            conn = connect_machine(ip)
            if conn:
                set_device_time(conn)
                disconnect_machine(conn)
        
        elif choice == "10":
            ip = input("Enter machine IP (default: 192.168.9.229): ") or "192.168.9.229"
            action = input("Enter action (enable/disable): ")
            conn = connect_machine(ip)
            if conn:
                if action.lower() == 'enable':
                    enable_device(conn)
                else:
                    disable_device(conn)
                disconnect_machine(conn)
        
        elif choice == "11":
            for machine in machines:
                comprehensive_machine_check(machine)
        
        elif choice == "12":
            user_id = input("Enter user ID to search: ")
            if user_id:
                try:
                    # Try to convert to int, but also search as string
                    find_user_in_all_machines(int(user_id), "user_id")
                except ValueError:
                    find_user_in_all_machines(user_id, "user_id")
        
        elif choice == "13":
            name = input("Enter user name to search: ")
            if name:
                find_user_in_all_machines(name, "name")
        
        elif choice == "14":
            user_id = input("Enter user ID to search with attendance: ")
            days = input("Enter days back to search (default: 30): ") or "30"
            if user_id:
                try:
                    find_user_with_attendance(int(user_id), int(days))
                except ValueError:
                    find_user_with_attendance(user_id, int(days))
        
        elif choice == "15":
            pattern = input("Enter name pattern to search: ")
            partial = input("Use partial matching? (y/n, default: y): ").lower() != 'n'
            if pattern:
                search_users_by_name(pattern, partial)
        
        elif choice == "16":
            ip = input("Enter machine IP: ")
            duration_str = input("Enter duration in seconds (optional): ")
            duration = int(duration_str) if duration_str else None
            show_users = input("Show user names? (y/n, default: y): ").lower() != 'n'
            
            if ip:
                print(f"🔴 Starting live capture for {ip}...")
                start_live_capture(ip, duration, show_users)
                if duration:
                    print(f"⏰ Live capture will run for {duration} seconds")
                else:
                    print("⏰ Live capture running indefinitely. Use option 21 to stop.")
        
        elif choice == "17":
            duration_str = input("Enter duration in seconds (optional): ")
            duration = int(duration_str) if duration_str else None
            show_users = input("Show user names? (y/n, default: y): ").lower() != 'n'
            
            print(f"🔴 Starting live capture for all machines...")
            start_live_capture(None, duration, show_users)
            if duration:
                print(f"⏰ Live capture will run for {duration} seconds")
            else:
                print("⏰ Live capture running indefinitely. Use option 21 to stop.")
        
        elif choice == "18":
            live_capture_interactive()
        
        elif choice == "19":
            user_id = input("Enter user ID to monitor: ")
            duration_str = input("Enter duration in seconds (optional): ")
            duration = int(duration_str) if duration_str else None
            
            if user_id:
                try:
                    monitor_specific_user_live(int(user_id), duration)
                except ValueError:
                    monitor_specific_user_live(user_id, duration)
        
        elif choice == "20":
            live_capture_status()
        
        elif choice == "21":
            print("Stop options:")
            print("1. Stop specific machine")
            print("2. Stop all machines")
            stop_choice = input("Choose option (1-2): ")
            
            if stop_choice == "1":
                ip = input("Enter machine IP to stop: ")
                stop_live_capture(ip)
            elif stop_choice == "2":
                stop_live_capture()
            else:
                print("Invalid choice")
        elif choice == "22":
            stop_live_capture()  # Stop any running captures
            break
                
def show_current_targets():
    """Show current target machines"""
    print(f"\n📡 Current target machines:")
    for i, machine in enumerate(machines, 1):
        print(f"  {i}. {machine}")
    print()

# Run the original function or start interactive menu
if __name__ == "__main__":
    args = parse_arguments()
    
    set_target_machines(args.target)
    
    if args.user:
        print(f"🔍 Searching for user {args.user} in all target machines...")
        try:
            user_id = int(args.user)
            find_user_in_all_machines(user_id, "user_id")
        except ValueError:
            find_user_in_all_machines(args.user, "name")
    
    elif args.check:
        print("🔧 Checking all target machines...")
        for machine in machines:
            comprehensive_machine_check(machine)
    
    elif args.live:
        print("🔴 Starting live capture for all target machines...")
        try:
            start_live_capture()
            input("Press Enter to stop live capture...")
        except KeyboardInterrupt:
            pass
        finally:
            stop_live_capture()
    
    elif args.interactive or len(sys.argv) == 1:
        interactive_menu()
    
    else:
        print("Use --help for available options")