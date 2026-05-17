import requests
import time
import itertools
import string
import os
import sys
import random
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

BOLD   = '\033[1m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
RED    = '\033[91m'
CYAN   = '\033[96m'
BLUE   = '\033[34m'
PURPLE = '\033[35m'
GREY   = '\033[90m'
RESET  = '\033[0m'

FREE_RESULTS        = {}
STOP_FLAG           = False
TELEGRAM_BOT_TOKEN  = ""
TELEGRAM_CHAT_ID    = ""
DISCORD_WEBHOOK_URL = ""
proxy_pool: list[str] = []
proxy_lock            = Lock()
proxy_index           = 0
is_loading_proxies   = False

PROXY_SOURCES = [
    # ProxyScrape
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
    "https://api.proxyscrape.com/v3/?request=displayproxies&protocol=http&timeout=10000&country=all",
    # TheSpeedX
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    # monosans
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt",
    # proxy-list.download
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    # ShiftyTR / mertguvencli
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
    # hookzof
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    # jetkai
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    # clarketm
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    # sunny9577
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    # roosterkid
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    # almroot
    "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
    # rdavydov
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    # ProxyDB
    "https://proxydb.net/?protocol=http&anonimity=&country=",
    # free-proxy-list.net ham liste
    "https://free-proxy-list.net/",
    # openproxy.space
    "https://openproxy.space/list/http",
    "https://openproxy.space/list/socks4",
    "https://openproxy.space/list/socks5",
    # hidemy.name API
    "https://hidemy.io/en/proxy-list/?type=hs#list",
    # api64.ipify testi için değil ama proxy toplama için yardımcı
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt",
    # elliottophellia
    "https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt",
    # vakhov
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt",
    # zeynep-proxy benzeri alternatif
    "https://raw.githubusercontent.com/ObcbO/getproxy/master/file/http.txt",
    "https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks5.txt",
]

DISCORD_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "X-Discord-Locale": "en-US",
    "Origin": "https://discord.com",
    "Referer": "https://discord.com/",
}

INSTAGRAM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

TELEGRAM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TIKTOK_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.tiktok.com/",
}

PLATFORM_COLORS = {
    "discord":   BLUE,
    "instagram": PURPLE,
    "tiktok":    CYAN,
    "telegram":  "\033[36m",
}


def fetch_proxies_raw():
    raw = []
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=6)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = line.strip()
                    if line and ":" in line and not line.startswith("#"):
                        raw.append(line)
        except Exception:
            continue
    return list(set(raw))


def _check_single_proxy(proxy):
    try:
        pd = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r  = requests.get("http://httpbin.org/ip", proxies=pd, timeout=3)
        if r.status_code == 200:
            return proxy
    except Exception:
        pass
    return None


def load_proxies(min_alive=30, max_threads=200):
    global proxy_pool, is_loading_proxies
    if is_loading_proxies:
        return len(proxy_pool)

    is_loading_proxies = True
    print(f"\n{YELLOW}[*] Proxy kaynakları taranıyor ve test ediliyor...{RESET}")
    raw = fetch_proxies_raw()
    if not raw:
        print(f"{RED}[!] Hiç proxy kaynağına ulaşılamadı.{RESET}")
        is_loading_proxies = False
        return 0

    print(f"{CYAN}[i] {len(raw)} ham proxy alındı, ultra hızlı canlılık testi başlıyor...{RESET}")
    found   = []
    checked = 0
    lock_l  = Lock()

    def worker(p):
        nonlocal checked
        result = _check_single_proxy(p)
        with lock_l:
            checked += 1
            if result:
                found.append(result)
                print(f"\r{GREEN}[✓]{RESET} Canlı Proxy: {len(found)}   Kontrol Edilen: {checked}/{len(raw)}   ", end="")

    with ThreadPoolExecutor(max_workers=max_threads) as ex:
        futures = [ex.submit(worker, p) for p in raw]
        for f in as_completed(futures):
            if len(found) >= min_alive * 4:
                break

    print()
    random.shuffle(found)
    with proxy_lock:
        proxy_pool = found
    print(f"{GREEN}[✓] {len(proxy_pool)} adet canlı proxy havuzuna aktarıldı.{RESET}\n")
    is_loading_proxies = False
    return len(proxy_pool)


def get_next_proxy():
    global proxy_index
    with proxy_lock:
        if not proxy_pool:
            return None
        proxy_index = proxy_index % len(proxy_pool)
        p = proxy_pool[proxy_index]
        proxy_index += 1
    return {"http": f"http://{p}", "https": f"http://{p}"}


def remove_proxy(proxy_dict):
    global proxy_pool
    if not proxy_dict:
        return
    addr = proxy_dict.get("http", "").replace("http://", "")
    with proxy_lock:
        if addr in proxy_pool:
            proxy_pool.remove(addr)


def _ensure_proxies():
    """Havuz kritik seviyenin altına düştüyse arka planda yeniden yükle."""
    if len(proxy_pool) < 10 and not is_loading_proxies:
        print(f"\n{YELLOW}[!] Proxy havuzu kritik seviyede ({len(proxy_pool)}), otomatik takviye başlatılıyor...{RESET}")
        load_proxies(min_alive=30)


def _get(url, headers, proxy_dict=None, timeout=3.5, **kwargs):
    proxy = proxy_dict if proxy_dict is not None else get_next_proxy()
    if proxy is None:
        _ensure_proxies()
        return None, None
    try:
        r = requests.get(url, headers=headers, proxies=proxy, timeout=timeout, **kwargs)
        return r, proxy
    except Exception:
        if proxy:
            remove_proxy(proxy)
        return None, None


def _post(url, headers, json_data, proxy_dict=None, timeout=3.5):
    proxy = proxy_dict if proxy_dict is not None else get_next_proxy()
    if proxy is None:
        _ensure_proxies()
        return None, None
    try:
        r = requests.post(url, headers=headers, json=json_data, proxies=proxy, timeout=timeout)
        return r, proxy
    except Exception:
        if proxy:
            remove_proxy(proxy)
        return None, None


def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=5,
        )
    except Exception as e:
        print(f"{YELLOW}[Telegram hata] {e}{RESET}")


def send_discord_webhook(message):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=5)
    except Exception as e:
        print(f"{YELLOW}[Discord hata] {e}{RESET}")


def notify_free(platform, username):
    emoji = {"discord": "🟦", "instagram": "📸", "tiktok": "🎵", "telegram": "✈️"}.get(platform, "✅")
    send_telegram(f"{emoji} <b>BOŞ USERNAME!</b>\nPlatform: <code>{platform.upper()}</code>\nKullanıcı: <code>{username}</code>")
    send_discord_webhook(f"{emoji} **BOŞ USERNAME!**\nPlatform: `{platform.upper()}`\nKullanıcı: `{username}`")


def pick_notification_channels():
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DISCORD_WEBHOOK_URL
    print(f"\n{YELLOW}Bildirim Kanalları{RESET}")
    if input("Telegram? (e/h): ").strip().lower() == "e":
        token = input("  Bot Token : ").strip()
        chat  = input("  Chat ID   : ").strip()
        if token and chat:
            TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID = token, chat
            send_telegram("✅ <b>Username Checker</b> — Telegram aktif")
            print(f"{GREEN}  [OK] Test mesajı gönderildi.{RESET}")
        else:
            print(f"{YELLOW}  [!] Telegram devre dışı.{RESET}")
    if input("Discord webhook? (e/h): ").strip().lower() == "e":
        hook = input("  Webhook URL: ").strip()
        if hook:
            DISCORD_WEBHOOK_URL = hook
            send_discord_webhook("**Username Checker** — Discord aktif")
            print(f"{GREEN}  [OK] Test mesajı gönderildi.{RESET}")
        else:
            print(f"{YELLOW}  [!] Discord devre dışı.{RESET}")
    print(f"\n  Telegram : {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
    print(f"  Discord  : {'✅' if DISCORD_WEBHOOK_URL else '❌'}\n")


class RateLimiter:
    def __init__(self, base_delay=0.1):
        self.base_delay = base_delay
        self.lock       = Lock()

    def ok(self):
        time.sleep(self.base_delay + random.uniform(0.01, 0.05))

    def hit(self, platform_name=""):
        print(f"{YELLOW}    [!] {platform_name.upper()} 429 (Rate Limit)! Proxy çöpe atıldı, yenisine geçiliyor...{RESET}")

def check_discord(username, rl):
    """
    Kesin cevap (True/False) alana kadar sonsuz döner.
    Proxy havuzu boşalırsa otomatik yeniden doldurur.
    """
    attempt = 0
    while not STOP_FLAG:
        attempt += 1
        _ensure_proxies()

        if not proxy_pool:
            time.sleep(1)
            continue

        r, proxy = _post(
            "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
            DISCORD_HEADERS,
            {"username": username},
        )

        if r is None:
            if attempt % 10 == 0:
                print(f"{GREY}    [~] discord/{username}: {attempt}. deneme, proxy bulunamadı...{RESET}")
            continue
        if r.status_code == 200:
            taken = r.json().get("taken")
            rl.ok()
            if taken is not None:
                return taken
            continue
        elif r.status_code == 429:
            remove_proxy(proxy)
            rl.hit("discord")
            continue
        elif r.status_code == 400:

            return None
        else:
            remove_proxy(proxy)
            continue

    return None


def check_instagram(username, rl):
    attempt = 0
    while not STOP_FLAG:
        attempt += 1
        _ensure_proxies()

        if not proxy_pool:
            time.sleep(1)
            continue

        r, proxy = _get(
            f"https://www.instagram.com/{username}/",
            INSTAGRAM_HEADERS,
            allow_redirects=True,
        )

        if r is None:
            if attempt % 10 == 0:
                print(f"{GREY}    [~] instagram/{username}: {attempt}. deneme...{RESET}")
            continue

        if r.status_code == 200:
            rl.ok()
            return True
        elif r.status_code == 404:
            rl.ok()
            return False
        elif r.status_code == 429:
            remove_proxy(proxy)
            rl.hit("instagram")
            continue
        else:
            remove_proxy(proxy)
            continue

    return None


def check_tiktok(username, rl):
    attempt = 0
    while not STOP_FLAG:
        attempt += 1
        _ensure_proxies()

        if not proxy_pool:
            time.sleep(1)
            continue

        r, proxy = _get(
            f"https://www.tiktok.com/@{username}",
            TIKTOK_HEADERS,
            timeout=4,
            allow_redirects=True,
        )

        if r is None:
            if attempt % 10 == 0:
                print(f"{GREY}    [~] tiktok/{username}: {attempt}. deneme...{RESET}")
            continue

        if r.status_code == 404:
            rl.ok()
            return False
        elif r.status_code == 200:
            taken = (
                f'"uniqueId":"{username.lower()}"' in r.text.lower()
                or "user-not-found" not in r.text.lower()
            )
            rl.ok()
            return taken
        elif r.status_code == 429:
            remove_proxy(proxy)
            rl.hit("tiktok")
            continue
        else:
            remove_proxy(proxy)
            continue

    return None


def check_telegram(username, rl):
    attempt = 0
    while not STOP_FLAG:
        attempt += 1
        _ensure_proxies()

        if not proxy_pool:
            time.sleep(1)
            continue

        r, proxy = _get(
            f"https://t.me/{username}",
            TELEGRAM_HEADERS,
            allow_redirects=True,
        )

        if r is None:
            if attempt % 10 == 0:
                print(f"{GREY}    [~] telegram/{username}: {attempt}. deneme...{RESET}")
            continue

        if r.status_code == 200:
            rl.ok()
            return "tgme_page_title" in r.text or "tgme_page_description" in r.text
        elif r.status_code == 429:
            remove_proxy(proxy)
            rl.hit("telegram")
            continue
        else:
            remove_proxy(proxy)
            continue

    return None


PLATFORM_CHECKERS = {
    "discord":   check_discord,
    "instagram": check_instagram,
    "tiktok":    check_tiktok,
    "telegram":  check_telegram,
}


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    cls()
    print(f"""{CYAN}{BOLD}
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║        All Platform Username Checker + Proxy         ║
    ║                                                      ║
    ║   ██████╗ ██╗  ██╗██╗     ██████╗ ███████╗           ║
    ║   ██╔══██╗╚██╗██╔╝██║     ╚════██╗██╔════╝           ║
    ║   ██║  ██║ ╚███╔╝ ██║      █████╔╝███████╗           ║
    ║   ██║  ██║ ██╔██╗ ██║     ╚═══██╗╚════██║           ║
    ║   ██████╔╝██╔╝ ██╗███████╗██████╔╝███████║           ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝{RESET}
    """)
    print(f"  Telegram  : {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
    print(f"  Discord   : {'✅' if DISCORD_WEBHOOK_URL else '❌'}")
    print(f"  Proxy     : {GREEN}{len(proxy_pool)} canlı{RESET}" if proxy_pool else f"  Proxy     : {YELLOW}yüklenmedi / kritik seviyede{RESET}")
    print()


def print_result(platform, username, status):
    pc  = PLATFORM_COLORS.get(platform, "")
    tag = f"{pc}[{platform.upper()[:2]}]{RESET}"
    if status is True:
        print(f"{tag} {RED}[DOLU]  {username}{RESET}")
    elif status is False:
        print(f"{tag} {GREEN}[BOŞ]   {username}  <- ALINABİLİR!{RESET}")
        FREE_RESULTS.setdefault(platform, []).append(username)
        notify_free(platform, username)
    else:
        print(f"{tag} {GREY}[SKIP]  {username}  (geçersiz format veya durduruldu){RESET}")


def save_results():
    if not FREE_RESULTS:
        return
    with open("bos_usernameler.txt", "w", encoding="utf-8") as f:
        for platform, names in FREE_RESULTS.items():
            f.write(f"\n=== {platform.upper()} ===\n")
            for n in names:
                f.write(n + "\n")
    total = sum(len(v) for v in FREE_RESULTS.values())
    print(f"\n{GREEN}[OK] {total} boş username -> bos_usernameler.txt{RESET}")


def pick_platforms():
    print(f"\n{YELLOW}Platform seç:{RESET}")
    print("  1) Discord\n  2) Instagram\n  3) TikTok\n  4) Telegram\n  5) Hepsi")
    raw = input("Seç (virgülle: 1,3 or 5): ").strip()
    mapping = {
        "1": ["discord"], "2": ["instagram"], "3": ["tiktok"],
        "4": ["telegram"], "5": ["discord", "instagram", "tiktok", "telegram"],
    }
    platforms = []
    for token in raw.split(","):
        platforms.extend(mapping.get(token.strip(), []))
    return list(dict.fromkeys(platforms)) or ["discord"]


def scan_list(usernames, platforms, workers=16):
    global STOP_FLAG
    STOP_FLAG = False
    rate_limiters = {p: RateLimiter(base_delay=0.1) for p in platforms}
    tasks = [(p, u) for u in usernames for p in platforms]
    random.shuffle(tasks)
    total = len(tasks)
    done  = 0
    lock  = Lock()
    px_info = f"{GREEN}{len(proxy_pool)} proxy{RESET}" if proxy_pool else f"{YELLOW}proxy yok (otomatik toplanacak){RESET}"
    print(f"\n{BLUE}[->] {len(usernames)} username × {len(platforms)} platform = {total} istek{RESET}")
    print(f"{BLUE}[->] Proxy: {px_info}  |  Ctrl+C durdurur{RESET}")
    print(f"{BLUE}[->] NOT: Artık SKIP yok — kesin cevap alana kadar her username tekrar denenir.{RESET}\n")

    def worker_fn(args):
        nonlocal done
        platform, username = args
        if STOP_FLAG:
            return
        status = PLATFORM_CHECKERS[platform](username, rate_limiters[platform])
        with lock:
            done += 1
            print_result(platform, username, status)
            sys.stdout.write(f"{GREY}    [{done}/{total}] Kalan: {total - done}  |  Aktif Proxy: {len(proxy_pool)}{RESET}\n")
            sys.stdout.flush()

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(worker_fn, t) for t in tasks]
        try:
            for f in as_completed(futures):
                pass
        except KeyboardInterrupt:
            STOP_FLAG = True
            print(f"\n{YELLOW}[!] Durduruldu.{RESET}")

    free = sum(len(v) for v in FREE_RESULTS.values())
    print(f"\n{BLUE}[OK] Bitti! Boş: {free} | Toplam: {total}{RESET}")


def gen_combos(chars, length):
    combos = ["".join(c) for c in itertools.product(chars, repeat=length)]
    random.shuffle(combos)
    return combos


def gen_word_patterns(word):
    chars = string.ascii_lowercase + string.digits
    usernames = [word]
    for c in chars:
        usernames += [c + word, word + c, c + "_" + word, word + "_" + c]
    result = list(dict.fromkeys(usernames))
    random.shuffle(result)
    return result


def menu_proxy_setup():
    val = input(f"Minimum canlı proxy sayısı [30]: ").strip()
    min_alive = int(val) if val.isdigit() else 30
    load_proxies(min_alive=min_alive)
    input(f"\n{YELLOW}[↵] Devam için ENTER{RESET}")


def menu_single():
    username = input(f"\n{YELLOW}Kullanıcı adı: {RESET}").strip()
    if not username:
        return
    pick_notification_channels()
    platforms = pick_platforms()
    for p in platforms:
        rl     = RateLimiter()
        status = PLATFORM_CHECKERS[p](username, rl)
        print_result(p, username, status)
    save_results()


def menu_nl_checker(forced_length=None):
    if forced_length:
        length = forced_length
    else:
        print(f"\n{YELLOW}Kaç harf?{RESET}")
        print("  1) 5L\n  2) 4L\n  3) 3L\n  4) 2L\n  5) 1L")
        c      = input("Seç: ").strip()
        length = {"1": 5, "2": 4, "3": 3, "4": 2, "5": 1}.get(c)

    if not length:
        print("Geçersiz Harf Seçimi.")
        return

    print(f"\n{YELLOW}Karakter seti:{RESET}\n  1) a-z\n  2) a-z + 0-9\n  3) 0-9")
    cs    = input("Seç: ").strip()
    chars = {"1": string.ascii_lowercase, "2": string.ascii_lowercase + string.digits, "3": string.digits}.get(cs, string.ascii_lowercase)
    combos = gen_combos(chars, length)
    print(f"\n{BLUE}{len(combos)} kombinasyon üretildi.{RESET}")
    pick_notification_channels()
    platforms  = pick_platforms()
    total_reqs = len(combos) * len(platforms)
    if total_reqs > 5000:
        print(f"{YELLOW}[!] {total_reqs} istek gönderilecek.{RESET}")
        if input("Devam? (e/h): ").strip().lower() != "e":
            return
    scan_list(combos, platforms)
    save_results()


def menu_word():
    raw   = input(f"\n{YELLOW}Kelime(ler) gir, virgülle ayır (örnek: dai,void,neo):\n> {RESET}").strip()
    words = [w.strip() for w in raw.split(",") if w.strip()]
    if not words:
        print("Kelime girmedin.")
        return
    all_usernames = []
    for word in words:
        patterns = gen_word_patterns(word)
        print(f"{GREY}'{word}' -> {len(patterns)} varyant{RESET}")
        all_usernames.extend(patterns)
    all_usernames = list(dict.fromkeys(all_usernames))
    random.shuffle(all_usernames)
    pick_notification_channels()
    platforms = pick_platforms()
    scan_list(all_usernames, platforms)
    save_results()


def menu_custom_list():
    path = input(f"\n{YELLOW}Dosya yolu: {RESET}").strip()
    if not os.path.exists(path):
        print(f"{RED}Dosya bulunamadı: {path}{RESET}")
        return
    with open(path, encoding="utf-8") as f:
        usernames = [line.strip() for line in f if line.strip()]
    random.shuffle(usernames)
    pick_notification_channels()
    platforms = pick_platforms()
    scan_list(usernames, platforms)
    save_results()


def main():
    banner()
    if input(f"{YELLOW}Proxy yüklensin mi? (e/h): {RESET}").strip().lower() == "e":
        load_proxies(min_alive=40)

    while True:
        banner()
        print(f"""{BLUE}====== MENÜ ======{RESET}
    1)  Tekli Arama
    2)  5L Checker
    3)  4L Checker
    4)  3L Checker
    5)  2L Checker
    6)  1L Checker
    7)  Söze Göre  (dai -> 1dai, qdai, daiw, dai_x...)
    8)  Özel Liste (txt dosyası)
    9)  Bildirim Ayarları
    P)  Proxy Yönetimi  [{GREEN}{len(proxy_pool)} canlı{RESET}]
    0)  Çıkış
    {BLUE}=================={RESET}""")
        choice = input("\nSeç: ").strip().lower()
        if   choice == "1": menu_single()
        elif choice == "2": menu_nl_checker(forced_length=5)
        elif choice == "3": menu_nl_checker(forced_length=4)
        elif choice == "4": menu_nl_checker(forced_length=3)
        elif choice == "5": menu_nl_checker(forced_length=2)
        elif choice == "6": menu_nl_checker(forced_length=1)
        elif choice == "7": menu_word()
        elif choice == "8": menu_custom_list()
        elif choice == "9": pick_notification_channels()
        elif choice == "p": menu_proxy_setup()
        elif choice == "0":
            print(f"{YELLOW}Çıkılıyor...{RESET}")
            break
        else:
            print("Geçersiz seçim.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Durduruldu.{RESET}\n")
        save_results()
        sys.exit(0)