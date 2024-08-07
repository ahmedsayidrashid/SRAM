from machine import Pin
import time

# Define address and data pins
address_pins = [Pin(i, Pin.OUT) for i in range(13)] 
data_pins = [Pin(i, Pin.OUT) for i in [17, 18, 19, 20, 21, 22, 26, 27]]  

ReadOrWrite = Pin(16, Pin.OUT)  # Read/Write control

def set_address(address):
    for i in range(13):
        address_pins[i].value((address >> i) & 1)
        #print("address bit number " + str(i) + ": value: " + str(address_pins[i].value()))

def configure_data_pins_as_input(): # Function to configure data pins as inputs
    for pin in data_pins:
        pin.init(Pin.IN)

def configure_data_pins_as_output():
    for pin in data_pins:
        pin.init(Pin.OUT)

# Function to read data from SRAM
def read_sram(address):
    set_address(address)
    ReadOrWrite.value(1)  # Set to read mode 
    time.sleep(0.01)  # Allow time for data to stabilize

    # Configure data pins as inputs for reading
    configure_data_pins_as_input()
    
    data = 0
    for i in range(8):  # Reading 8-bit data
        data |= (data_pins[i].value() << i)
        #print("data bit number " + str(i) + ": value: " + str(data_pins[i].value()))
    return data

# Function to write data to SRAM
def write_sram(address, data):
    set_address(address)
    ReadOrWrite.value(0)  # Set to write mode (assuming low is write mode)

    # Configure data pins as outputs for writing
    configure_data_pins_as_output()
    
    for i in range(8):
        data_pins[i].value((data >> i) & 1)
    time.sleep(0.01)  # Allow time for data to be written
 
# Function to output all the SRAM data
def read_all_sram(size):
    for address in range(size):
        data = read_sram(address)
        print(f"Address {address:04X}: Data {data:02X}")

# Function to write a specific location in memory.
def write_some_sram(start_loc, end_loc, data):
    if(end_loc < start_loc):
        print("End location must be greater")
        return
    for address in range(start_loc,end_loc+1):
        write_sram(address, data)
        print(f"Address {address:04X}: Data {data:02X}")

# Example usage
address_to_write = 0x0000
data_to_write = 0xAB

write_sram(address_to_write, data_to_write)
time.sleep(0.1)  # Wait before reading

# Read first 10 addresses of SRAM
read_all_sram(10)

# Ideal case should be to output 0xAB for address 0x00 and 0x00 for the rest of addresses.


    