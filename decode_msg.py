# Decode MSG #7 raw bytes
msg = "11010032003276"

print(f"Raw hex string: {msg}")
print(f"Length: {len(msg)} chars = {len(msg)//2} bytes")
print()
print("Byte by byte:")

for i in range(0, len(msg), 2):
    byte_hex = msg[i:i+2]
    byte_dec = int(byte_hex, 16)
    print(f"  Byte {i//2}: {byte_hex} = {byte_dec} decimal")

print()
print("MDB 1101 Setup Min/Max Prices interpretation:")
print(f"  Command    : {msg[0:4]}")
print(f"  Max price  : {msg[4:6]} hex = {int(msg[4:6],16)} decimal")
print(f"  Min price  : {msg[8:10]} hex = {int(msg[8:10],16)} decimal")

scale = 1  # from MSG #6: scale=01 = 1 cent
max_price = int(msg[4:6], 16) * scale
min_price = int(msg[8:10], 16) * scale
print()
print(f"  Max price in cents: {max_price} = ${max_price/100:.2f}")
print(f"  Min price in cents: {min_price} = ${min_price/100:.2f}")
print()

# Check adapter config
adapter_max = 0x3C  # from MSG #2: 3C
print(f"Adapter max config : 0x3C = {adapter_max} = ${adapter_max/100:.2f}")
print()

if max_price == adapter_max * scale:
    print("MATCH - prices agree")
else:
    print(f"MISMATCH - machine says ${max_price/100:.2f} but adapter expects ${adapter_max/100:.2f}")
    print("This may not be the actual problem though")
