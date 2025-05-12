import serial
import time
import numpy as np
import win32com.client

class AES_Arduino_Oscilloscope:
    def __init__(self, port, oscilloscope_ip, baudrate=115200, timeout=2):
        # Initialize Arduino Serial
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  # Allow Arduino to initialize
            self.ser.flushInput()
            print("✅ Arduino Connected")
        except serial.SerialException:
            self.ser = None
            print("❌ Arduino Not Connected")

        # Try to connect to oscilloscope
        try:
            self.scope = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")
            self.scope.MakeConnection(f"IP:{oscilloscope_ip}")
            time.sleep(1)  # Allow connection setup

            # Verify oscilloscope connection by sending a simple query
            response = self.scope.WriteString("C3:WF? DAT1", 1)  # Test query
            if response is None:
                raise Exception("No response from oscilloscope")

            self.is_scope_connected = True
            print("✅ Connected to Oscilloscope")
        except Exception as e:
            print("❌ Oscilloscope Not Connected:", e)
            self.is_scope_connected = False  # Flag to indicate missing oscilloscope

    def trigger_scope(self):
        """Set oscilloscope trigger mode to normal and start acquisition."""
        if self.is_scope_connected:
            self.scope.WriteString(r"""vbs 'app.acquisition.triggermode = "normal" ' """, 1)

    def acquire_trace(self, num_points=13000):
        """Acquire power trace from oscilloscope (Channel 1) if connected."""
        if not self.is_scope_connected:
            print("❌ Oscilloscope not connected. Skipping trace acquisition.")
            return None

        print("🔹 Starting Acquisition...")
        try:
            self.scope.WriteString(r"""vbs 'app.acquisition.triggermode = "normal" ' """, 1)
            trace = np.array(self.scope.GetIntegerWaveform("C3", num_points, 0))
            print("✅ Acquisition Successful")
            print(trace)
            return trace
        except Exception as e:
            print(f"❌ Error acquiring trace: {e}")
            return None

    def send_plaintext(self, plaintext_hex):
        """Send plaintext (16-byte hex string) to Arduino."""
        if self.ser is None:
            print("❌ Cannot send plaintext: Arduino not connected")
            return

        if len(plaintext_hex) != 32:
            raise ValueError("Plaintext must be 32 hex characters (16 bytes)")

        self.ser.flushInput()
        self.ser.write(plaintext_hex.encode() + b'\n')

    def receive_ciphertext(self):
        """Read and parse ciphertext from Arduino."""
        if self.ser is None:
            return None

        while True:
            response = self.ser.readline().decode().strip()
            print(f"Debug: {response}")  # Debugging
            if response.startswith("Ciphertext:"):
                hex_values = response.split(":")[1].strip().split(" ")
                return "".join(hex_values) 

    def encrypt(self, plaintext_hex, trace_idx):
        """Trigger oscilloscope, send plaintext, get ciphertext, and acquire trace."""
        if self.is_scope_connected:
            self.trigger_scope()  # Ensure oscilloscope is ready

        self.send_plaintext(plaintext_hex)  # Send plaintext to Arduino
        ciphertext_hex = self.receive_ciphertext()  # Get ciphertext

        if ciphertext_hex is None:
            print("❌ No ciphertext received")
            return None

        trace = self.acquire_trace()  # Read oscilloscope waveform (if available)

        # Convert to NumPy array
        pt_array = np.array([int(plaintext_hex[i:i+2], 16) for i in range(0, 32, 2)], dtype=np.uint8)
        ct_array = np.array([int(ciphertext_hex[i:i+2], 16) for i in range(0, 32, 2)], dtype=np.uint8)

        # Save data
        filename = f"ran_trace_{trace_idx}.npz"
        if trace is not None:
            np.savez(filename, plaintext=pt_array, ciphertext=ct_array, trace=trace)
        else:
            np.savez(filename, plaintext=pt_array, ciphertext=ct_array)

        print(f"✅ Trace {trace_idx} saved to {filename}")
        return ciphertext_hex

    def close(self):
        """Close serial connection and disconnect oscilloscope if connected."""
        if self.ser:
            self.ser.close()
            print("✅ Serial connection closed.")
        
        if self.is_scope_connected:
            self.scope.Disconnect()
            print("✅ Oscilloscope disconnected.")

# Configuration (Replace with actual port and oscilloscope IP)
print("Enter no. of traces")
n=int(input())
arduino = AES_Arduino_Oscilloscope(port="COM4", oscilloscope_ip="169.254.196.20")

plaintexts=[''.join(f'{byte:02x}' for byte in np.random.randint(0,256,16, dtype=np.uint8)) for _ in range(n)]

for i, pt in enumerate(plaintexts):
    print(f"🔹 Sending Plaintext: {pt}")
    ct = arduino.encrypt(pt, trace_idx=i)
    if ct:
        print(f"🔹 Ciphertext: {ct}\n")

arduino.close()
