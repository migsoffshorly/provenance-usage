from helpers.generate_certificates import generate_certificates

if __name__ == "__main__":
    print("[Provenance Feasibility Study]")
    # Step 1: create 2 test certificates
    generate_certificates("offshorly.com")
    # Step 2: create root
