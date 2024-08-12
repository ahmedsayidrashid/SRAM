from machine import Pin
import time

# Define address and data pins for the SRAM
address_pins = [Pin(i, Pin.OUT) for i in range(13)] 
data_pins = [Pin(i, Pin.OUT) for i in [17, 18, 19, 20, 21, 22, 26, 27]]  
ReadOrWrite = Pin(16, Pin.OUT)  # Read/Write control

# PS2 Keyboard definitions
ps2_data_pin = Pin(15, Pin.IN, Pin.PULL_UP)
clock_pin = Pin(28, Pin.IN, Pin.PULL_UP)

def set_address(address):
    for i in range(13):
        address_pins[i].value((address >> i) & 1)

def configure_data_pins_as_input(): 
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

# Function to write a specific location in memory.
def write_some_sram(start_loc, end_loc, data):
    if(end_loc < start_loc):
        print("End location must be greater")
        return
    for address in range(start_loc, end_loc + 1):
        write_sram(address, data)
        
# Function to output all the SRAM data
def read_all_sram(size):
    for address in range(size + 1):
        data = read_sram(address)
        print(f"Address {address:04X}: Data {data:02X}")

# Function to initialize the entire sram with data.
def initialize_all_sram(data): # usually data = 0x00 to reset the SRAM
    size = 64 * 1024
    for address in range(size):
        write_sram(address, data)
        
def print_sram_data(address):
    for num in range(address+1):
        data = hex(read_sram(num))[2:].upper()
        print("Address: " + str(num) + " Data: 0X" + str(data))
    print("-----") # for format purposes
    
# Function to read data from the PS/2 keyboard.
def read_ps2_keyboard():
    while True:
        if not clock_pin.value():  # Wait for a clock pulse (low signal)
            bitstream = 0
            # Read data bits
            for i in range(8):
                while clock_pin.value():  # Wait for clock to go low
                    pass
                bitstream |= (ps2_data_pin.value() << i)
                while not clock_pin.value():  # Wait for clock to go high
                    pass
            time.sleep(0.1) # some delay to be cautious
            
            #bitstream = hex(bitstream)[2:].upper() # convert the data to hex
            return bitstream
        
pc = 0 # program counter
data_to_sram = 0x00

while(1):
    data_to_sram = read_ps2_keyboard()
    
    if(data_to_sram == 0xEC): # Escape key resets the sram up to the program counter
        write_some_sram(0, pc, 0x00)
        pc = 0
        print("--- SRAM has been reset ---")
    elif(data_to_sram == 0x52): # Space key displays memory contents until the program counter
        print("--- Displaying memory contents ---")
        read_all_sram(pc)
    elif(data_to_sram == 0xCC): # Backspace (<-) key exits the program
        print("Exiting the program...")
        time.sleep(1)
        break
    else:
        write_sram(pc, data_to_sram) # write the scan keyboard input into the SRAM
        pc += 1 #increment the program counter to write to the next address
        print("Address " + str(pc) + " populated with keypress ASCII code " + str(data_to_sram))
