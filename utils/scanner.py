# utils/scanner.py
"""
Simple subdomain probe + DNS resolver.
- resolve DNS (socket.gethostbyname)
- optionally try HTTP/HTTPS to fetch status code
- uses ThreadPoolExecutor for concurrency
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def _resolve(fqdn, timeout):
    try:
        socket.setdefaulttimeout(timeout)
        return socket.gethostbyname(fqdn)
    except Exception:
        return None

def _probe(fqdn, timeout, check_http):
    ip = _resolve(fqdn, timeout)
    if not ip:
        return None
    http_status = None
    if check_http:
        session = requests.Session()
        for scheme in ("http://", "https://"):
            try:
                r = session.get(scheme + fqdn, timeout=timeout, allow_redirects=True)
                http_status = r.status_code
                break
            except requests.RequestException:
                continue
    return {"fqdn": fqdn, "ip": ip, "status": http_status}

def scan(domain, subdomains, callback=None, progress_callback=None,
         max_workers=30, timeout=2, check_http=True, stop_event=None):
    """
    Scan list of subdomains (strings) for the given domain.
    - callback(result_dict) is called for each positive result
    - progress_callback(scanned, total) is called as tasks complete
    - returns list of result_dicts
    """
    domain = domain.strip().rstrip(".")
    valid = [s.strip() for s in subdomains if s and not s.startswith("#")]
    total = len(valid)
    results = []
    if total == 0:
        return results

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_probe, f"{s}.{domain}", timeout, check_http): s for s in valid}
        scanned = 0
        for future in as_completed(futures):
            if stop_event and stop_event.is_set():
                break
            scanned += 1
            if progress_callback:
                try:
                    progress_callback(scanned, total)
                except Exception:
                    pass
            try:
                res = future.result()
            except Exception:
                res = None
            if res:
                results.append(res)
                if callback:
                    try:
                        callback(res)
                    except Exception:
                        pass
    return results
