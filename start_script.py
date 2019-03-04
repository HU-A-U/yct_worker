from proxy_yct import middle_tool

addons = [
    middle_tool.Proxy()
]

# mitmdump.exe -s start_script.py
# "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --proxy-server=127.0.0.1:8080 --ignore-certificate-errors