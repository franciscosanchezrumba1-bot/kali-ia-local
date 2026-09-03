#!/usr/bin/env python3

EXAMPLES = [
    "python3 kali-tools/nmap-scanner.py -t 192.168.1.1 -p 22,80,443 -i",
    "python3 kali-tools/sqlmap-wrapper.py -u 'https://target.com/item.php?id=1' --risk 2 --level 3",
    "python3 kali-tools/network-recon.py -n 192.168.1.0/24",
    "python3 kali-tools/password-cracker.py --tool john --hash-file hashes.txt --wordlist rockyou.txt",
]

if __name__ == "__main__":
    print("Ejemplos de uso:")
    for e in EXAMPLES:
        print("-", e)
