import subprocess
import os


def generate_certificates(domain_name: str, base_folder: str = "certificates"):
    # Create a unique output folder based on the domain name
    output_folder = os.path.join(base_folder, domain_name)
    os.makedirs(output_folder, exist_ok=True)

    # Paths for keys and certificates within the output folder
    root_key = os.path.join(output_folder, "rootCA.key")
    root_cert = os.path.join(output_folder, "rootCA.crt")
    intermediate_key = os.path.join(output_folder, "intermediateCA.key")
    intermediate_cert = os.path.join(output_folder, "intermediateCA.crt")
    ssl_key = os.path.join(output_folder, f"{domain_name}.key")
    ssl_csr = os.path.join(output_folder, f"{domain_name}.csr")
    ssl_cert = os.path.join(output_folder, f"{domain_name}.crt")
    bundled_cert = os.path.join(output_folder, "bundled_certificate.pem")

    # Define input values for OpenSSL
    country = "US\n"  # 2-letter country code
    state = "California\n"  # State name
    locality = "San Francisco\n"  # Locality or city name
    organization = "ExampleOrg\n"  # Organization name
    organizational_unit = "IT\n"  # Organizational unit
    common_name = f"{domain_name}\n"  # Common name (domain)
    email = "admin@example.com\n"  # Email address

    # Concatenate inputs to avoid long command
    # Add empty lines for challenge password and optional company name
    openssl_input = f"{country}{state}{locality}{organization}{organizational_unit}{common_name}{email}\n\n"

    try:
        # 1. Generate root CA private key
        subprocess.run(
            ["openssl", "genpkey", "-algorithm", "RSA", "-out", root_key, "-aes256"],
            check=True,
            input="provenance".encode(),  # Replace with a secure passphrase
        )
        print("Root CA private key generated.")

        # 2. Generate root CA certificate
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-new",
                "-nodes",
                "-key",
                root_key,
                "-sha256",
                "-days",
                "3650",
                "-out",
                root_cert,
            ],
            check=True,
            input=openssl_input.encode(),
        )
        print("Root CA certificate generated.")

        # 3. Generate intermediate CA private key
        subprocess.run(
            [
                "openssl",
                "genpkey",
                "-algorithm",
                "RSA",
                "-out",
                intermediate_key,
                "-aes256",
            ],
            check=True,
            input="provenance".encode(),  # Replace with a secure passphrase
        )
        print("Intermediate CA private key generated.")

        # 4. Generate intermediate CSR
        subprocess.run(
            [
                "openssl",
                "req",
                "-new",
                "-key",
                intermediate_key,
                "-out",
                os.path.join(output_folder, "intermediateCA.csr"),
            ],
            check=True,
            input=openssl_input.encode(),
        )
        print("Intermediate CSR generated.")

        # 5. Generate intermediate certificate signed by root CA
        subprocess.run(
            [
                "openssl",
                "x509",
                "-req",
                "-in",
                os.path.join(output_folder, "intermediateCA.csr"),
                "-CA",
                root_cert,
                "-CAkey",
                root_key,
                "-CAcreateserial",
                "-out",
                intermediate_cert,
                "-days",
                "1825",
                "-sha256",
            ],
            check=True,
        )
        print("Intermediate CA certificate generated.")

        # 6. Generate SSL private key
        subprocess.run(
            ["openssl", "genpkey", "-algorithm", "RSA", "-out", ssl_key], check=True
        )
        print("SSL private key generated.")

        # 7. Generate SSL CSR
        subprocess.run(
            ["openssl", "req", "-new", "-key", ssl_key, "-out", ssl_csr],
            check=True,
            input=openssl_input.encode(),
        )
        print("SSL CSR generated.")

        # 8. Generate SSL certificate signed by intermediate CA
        subprocess.run(
            [
                "openssl",
                "x509",
                "-req",
                "-in",
                ssl_csr,
                "-CA",
                intermediate_cert,
                "-CAkey",
                intermediate_key,
                "-CAcreateserial",
                "-out",
                ssl_cert,
                "-days",
                "825",
                "-sha256",
            ],
            check=True,
        )
        print("SSL certificate generated.")

        # 9. Bundle the SSL certificate with intermediate and root certificates
        with open(bundled_cert, "w") as bundle:
            for cert in [ssl_cert, intermediate_cert, root_cert]:
                with open(cert) as f:
                    bundle.write(f.read())
        print(f"Bundled certificate created at {bundled_cert}")

    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)
