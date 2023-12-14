import requests
from urllib.parse import urlparse
import socket
from retry import retry

def get_ip_address(url):
    try:
        ip_address = socket.gethostbyname(urlparse(url).hostname)
        return ip_address
    except socket.gaierror as e:
        print(f"Error resolving IP address: {e}")
        return None

@retry(tries=3, delay=2, backoff=2)
def backtrace_link(url, max_redirects=10, timeout=10, force_traceback=False):
    redirects = 0

    while redirects < max_redirects:
        try:
            response = requests.head(url, allow_redirects=False, timeout=timeout)
            if response.status_code in [301, 302, 303, 307, 308] or force_traceback:
                redirects += 1
                redirected_url = response.headers.get('Location')
                if redirected_url is None:
                    print(f"Warning: No 'Location' header in redirect response for {url}")
                    break

                # Get and display the IP address of the redirected URL
                redirected_ip = get_ip_address(redirected_url)
                if redirected_ip:
                    print(f"{redirects}. Redirect: {url} -> {redirected_url} | IP Address: {redirected_ip}")
                else:
                    print(f"{redirects}. Redirect: {url} -> {redirected_url}")

                url = redirected_url  # Update the URL for the next iteration
            else:
                print(f"Final URL after {redirects} redirects: {url}")

                # Get and display the IP address of the final URL
                final_ip = get_ip_address(url)
                if final_ip:
                    print(f"Final IP Address: {final_ip}")

                break
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    # Take user input for the target URL
    target_url = input("Enter the target's URL: ")
    
    # Example usage with a timeout of 20 seconds and force trace back
    backtrace_link(target_url, timeout=20, force_traceback=True)
